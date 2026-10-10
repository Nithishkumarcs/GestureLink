"""
GestureLink - Mouse Control Module
Translates hand landmarks into screen cursor movements, clicks, double clicks, and scrolling.
Features interaction area mapping, adaptive EMA smoothing, and drag-and-drop.
"""

import time
import math
from typing import Tuple, Optional
import pyautogui
from utils.helpers import map_range, exponential_smoothing
from utils.logger import get_logger

logger = get_logger("MouseControl")

# Optimize PyAutoGUI for real-time cursor control
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.001


class MouseController:
    """
    Handles desktop mouse automation via PyAutoGUI.
    Includes smoothing, screen coordinate remapping, click debouncing, and scrolling.
    """

    def __init__(self, smoothing: float = 0.60, sensitivity: float = 1.30,
                 margin_x: float = 0.15, margin_y: float = 0.18,
                 click_cooldown: float = 0.35, double_click_cooldown: float = 0.60,
                 scroll_sensitivity: float = 1.20, scroll_deadzone: float = 0.015):
        self.smoothing = smoothing
        self.sensitivity = sensitivity
        self.margin_x = margin_x
        self.margin_y = margin_y
        self.click_cooldown = click_cooldown
        self.double_click_cooldown = double_click_cooldown
        self.scroll_sensitivity = scroll_sensitivity
        self.scroll_deadzone = scroll_deadzone

        # Screen dimensions
        try:
            self.screen_width, self.screen_height = pyautogui.size()
        except Exception:
            self.screen_width, self.screen_height = 1920, 1080

        # Cursor state tracking
        self.prev_screen_x: Optional[float] = None
        self.prev_screen_y: Optional[float] = None

        # Click & drag state
        self.last_click_time = 0.0
        self.last_double_click_time = 0.0
        self.is_dragging = False
        self.pinch_start_time = 0.0

        # Scroll tracking
        self.prev_scroll_y: Optional[float] = None
        self.last_scroll_time = 0.0

    def update_settings(self, smoothing: Optional[float] = None, sensitivity: Optional[float] = None,
                        margin_x: Optional[float] = None, margin_y: Optional[float] = None,
                        scroll_sensitivity: Optional[float] = None):
        """Allows dynamic adjustment of calibration settings."""
        if smoothing is not None:
            self.smoothing = smoothing
        if sensitivity is not None:
            self.sensitivity = sensitivity
        if margin_x is not None:
            self.margin_x = margin_x
        if margin_y is not None:
            self.margin_y = margin_y
        if scroll_sensitivity is not None:
            self.scroll_sensitivity = scroll_sensitivity

    def move_cursor(self, norm_x: float, norm_y: float) -> Tuple[int, int]:
        """
        Maps normalized index fingertip coordinates within the interaction box to screen coordinates
        with adaptive smoothing to eliminate hand jitter.
        """
        # 1. Remap from interaction box [margin_x, 1 - margin_x] to full [0.0, 1.0]
        mapped_x = map_range(norm_x, self.margin_x, 1.0 - self.margin_x, 0.0, 1.0)
        mapped_y = map_range(norm_y, self.margin_y, 1.0 - self.margin_y, 0.0, 1.0)

        # 2. Scale to screen pixels
        target_x = mapped_x * self.screen_width
        target_y = mapped_y * self.screen_height

        # 3. Apply smoothing
        if self.prev_screen_x is None or self.prev_screen_y is None:
            cur_x = target_x
            cur_y = target_y
        else:
            # Distance from previous position
            dist = math.hypot(target_x - self.prev_screen_x, target_y - self.prev_screen_y)
            # Deadzone for micro-tremors (< 3 pixels)
            if dist < 3.0:
                cur_x = self.prev_screen_x
                cur_y = self.prev_screen_y
            else:
                # Dynamic alpha: tiny movement gets heavy smoothing, fast movement gets responsive alpha
                alpha = min(0.9, self.smoothing + (dist / 1000.0) * 0.2)
                cur_x = exponential_smoothing(self.prev_screen_x, target_x, alpha)
                cur_y = exponential_smoothing(self.prev_screen_y, target_y, alpha)

        # 4. Clamp to screen boundaries (keep 2px away from extreme (0,0) to prevent accidental failsafe)
        cur_x = max(2, min(self.screen_width - 3, cur_x))
        cur_y = max(2, min(self.screen_height - 3, cur_y))

        self.prev_screen_x = cur_x
        self.prev_screen_y = cur_y

        try:
            pyautogui.moveTo(int(cur_x), int(cur_y))
        except pyautogui.FailSafeException:
            logger.debug("PyAutoGUI fail-safe triggered on moveTo (mouse at screen corner).")
        except Exception as e:
            logger.debug(f"pyautogui moveTo warning: {e}")

        return int(cur_x), int(cur_y)

    def handle_pinch(self, is_pinched: bool, hold_duration: float = 0.0) -> Optional[str]:
        """
        Processes pinch gesture for left-click or drag-and-drop.
        Returns action string if an action was executed.
        """
        now = time.time()

        if is_pinched:
            # If held for more than 0.4s and not yet dragging, initiate mouse drag
            if hold_duration > 0.4 and not self.is_dragging:
                try:
                    pyautogui.mouseDown()
                    self.is_dragging = True
                    logger.info("Mouse Drag Started")
                    return "Drag Started"
                except pyautogui.FailSafeException:
                    logger.debug("PyAutoGUI fail-safe triggered on mouseDown.")
                except Exception as e:
                    logger.error(f"Error on mouseDown: {e}")

            # If it's a short initial tap, record start
            if self.pinch_start_time == 0.0:
                self.pinch_start_time = now

        else:
            # Pinch released
            if self.is_dragging:
                try:
                    pyautogui.mouseUp()
                    self.is_dragging = False
                    self.pinch_start_time = 0.0
                    logger.info("Mouse Drag Released")
                    return "Drag Released"
                except pyautogui.FailSafeException:
                    self.is_dragging = False
                    self.pinch_start_time = 0.0
                except Exception as e:
                    logger.error(f"Error on mouseUp: {e}")

            # If released quickly (tap) and cooldown passed -> Single Left Click
            if self.pinch_start_time > 0.0:
                duration = now - self.pinch_start_time
                self.pinch_start_time = 0.0
                if duration <= 0.4 and (now - self.last_click_time >= self.click_cooldown):
                    try:
                        pyautogui.click()
                        self.last_click_time = now
                        logger.info("Left Click Executed")
                        return "Left Click"
                    except pyautogui.FailSafeException:
                        logger.warning("PyAutoGUI fail-safe triggered on click (mouse at screen corner).")
                        self.last_click_time = now
                        return "Left Click"
                    except Exception as e:
                        logger.error(f"Error on click: {e}")

        return None

    def double_click(self) -> bool:
        """Executes a double click with cooldown."""
        now = time.time()
        if now - self.last_double_click_time >= self.double_click_cooldown:
            try:
                pyautogui.doubleClick()
                self.last_double_click_time = now
                logger.info("Double Click Executed")
                return True
            except pyautogui.FailSafeException:
                logger.warning("PyAutoGUI fail-safe triggered on double click.")
                self.last_double_click_time = now
                return True
            except Exception as e:
                logger.error(f"Error on double click: {e}")
        return False

    def handle_scroll(self, curr_y: float) -> Optional[str]:
        """
        Scrolls up/down based on vertical movement of two fingers.
        Only scrolls when movement exceeds the deadzone.
        """
        if self.prev_scroll_y is None:
            self.prev_scroll_y = curr_y
            return None

        dy = curr_y - self.prev_scroll_y
        self.prev_scroll_y = curr_y

        # Deadzone check (ignore tiny stationary drift)
        if abs(dy) < self.scroll_deadzone:
            return None

        # Hand moving up (decreasing Y in image coordinates) -> scroll up (+ clicks)
        # Hand moving down (increasing Y in image coordinates) -> scroll down (- clicks)
        scroll_amount = -int(dy * 150 * self.scroll_sensitivity)
        if scroll_amount == 0:
            scroll_amount = -1 if dy > 0 else 1

        try:
            pyautogui.scroll(scroll_amount)
            action = "Scroll Up" if scroll_amount > 0 else "Scroll Down"
            return action
        except pyautogui.FailSafeException:
            return "Scroll Up" if scroll_amount > 0 else "Scroll Down"
        except Exception as e:
            logger.error(f"Error on scroll: {e}")
            return None

    def reset_positions(self):
        """Resets smoothed coordinate history (e.g. when hand leaves frame)."""
        self.prev_screen_x = None
        self.prev_screen_y = None
        self.prev_scroll_y = None
        if self.is_dragging:
            try:
                pyautogui.mouseUp()
            except Exception:
                pass
            self.is_dragging = False

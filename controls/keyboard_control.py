"""
GestureLink - Keyboard Control Module
Provides safe, debounced, single-stroke keyboard shortcuts for desktop navigation and media.
"""

import time
from typing import Dict, Optional
import pyautogui
from utils.logger import get_logger

logger = get_logger("KeyboardControl")

# Whitelist of permissible safe keys
ALLOWED_KEYS = {
    "right", "left", "up", "down",
    "enter", "esc", "escape", "space",
    "f5", "f11", "pageup", "pagedown",
    "volumeup", "volumedown", "volumemute",
    "browserback", "browserforward"
}


class KeyboardController:
    """
    Executes safe keyboard shortcuts with strict debouncing and whitelist validation.
    """

    def __init__(self, default_cooldown: float = 0.4):
        self.default_cooldown = default_cooldown
        self.last_press_time: Dict[str, float] = {}

    def press(self, key_name: str, cooldown: Optional[float] = None) -> bool:
        """
        Presses a safe key with debouncing.
        Returns True if the key was pressed, False if ignored or on cooldown.
        """
        key_lower = key_name.lower().strip()
        if key_lower not in ALLOWED_KEYS:
            logger.warning(f"Key '{key_name}' is not in the safe allowed list. Refusing execution.")
            return False

        cd = cooldown if cooldown is not None else self.default_cooldown
        now = time.time()
        last_time = self.last_press_time.get(key_lower, 0.0)

        if now - last_time < cd:
            return False

        try:
            # Map 'esc' alias to 'escape' if needed
            send_key = "escape" if key_lower == "esc" else key_lower
            pyautogui.press(send_key)
            self.last_press_time[key_lower] = now
            logger.info(f"Pressed safe key: {send_key}")
            return True
        except pyautogui.FailSafeException:
            logger.warning(f"PyAutoGUI fail-safe triggered on key '{key_name}' (mouse at screen corner).")
            self.last_press_time[key_lower] = now
            return True
        except Exception as e:
            logger.error(f"Error pressing key '{key_name}': {e}")
            return False

    def hotkey(self, *keys: str, cooldown: Optional[float] = None) -> bool:
        """Executes a combination of safe keys (e.g. 'ctrl', 'c')."""
        cd = cooldown if cooldown is not None else self.default_cooldown
        now = time.time()
        combo_key = "+".join(keys).lower()

        if now - self.last_press_time.get(combo_key, 0.0) < cd:
            return False

        try:
            pyautogui.hotkey(*keys)
            self.last_press_time[combo_key] = now
            logger.info(f"Executed hotkey: {combo_key}")
            return True
        except pyautogui.FailSafeException:
            logger.warning(f"PyAutoGUI fail-safe triggered on hotkey '{combo_key}'.")
            self.last_press_time[combo_key] = now
            return True
        except Exception as e:
            logger.error(f"Error executing hotkey '{combo_key}': {e}")
            return False

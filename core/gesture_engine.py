"""
GestureLink - Gesture Engine & Stability System
Consecutive-frame confirmation, debouncing, cooldown timers, and Mode Management.
"""

import time
from collections import deque
from enum import Enum
from typing import Dict, Any, Optional, Callable, Tuple
from core.gesture_recognition import GestureType, GestureRecognizer
from utils.logger import get_logger

logger = get_logger("GestureEngine")


class AppMode(Enum):
    IDLE = "Idle"
    MOUSE_CONTROL = "Mouse Control"
    AIR_WRITING = "Air Writing"
    WHITEBOARD = "Virtual Whiteboard"
    APPLICATION_CONTROL = "App Launcher"
    PRESENTATION_CONTROL = "Presentation"


class GestureStabilityTracker:
    """
    Stabilizes raw gesture classifications using consecutive-frame verification,
    debouncing, and cooldown management to prevent flickering or accidental triggers.
    """

    def __init__(self, required_frames: int = 4, cooldown_seconds: float = 0.4):
        self.required_frames = required_frames
        self.cooldown_seconds = cooldown_seconds

        self._history = deque(maxlen=max(2, required_frames))
        self.raw_gesture = GestureType.NONE
        self.stable_gesture = GestureType.NONE
        self.previous_stable_gesture = GestureType.NONE

        self.last_trigger_time: Dict[GestureType, float] = {}
        self.gesture_start_time = 0.0
        self.is_new_trigger = False

    def update(self, detected_gesture: GestureType) -> Tuple[GestureType, bool, float]:
        """
        Updates the tracker with a newly detected gesture from the current frame.

        Returns:
            Tuple of:
            - stable_gesture: currently confirmed stable gesture
            - is_new_event: True on the exact frame the gesture became stabilized
            - hold_duration: how long (in seconds) the stable gesture has been held
        """
        self.raw_gesture = detected_gesture
        self._history.append(detected_gesture)

        # Check if history is consistently filled with the same gesture
        all_match = (len(self._history) >= self.required_frames and 
                     all(g == detected_gesture for g in self._history))

        now = time.time()
        is_new_event = False
        hold_duration = 0.0

        if all_match and detected_gesture != GestureType.NONE:
            if detected_gesture != self.stable_gesture:
                # Transition to new stable gesture
                self.previous_stable_gesture = self.stable_gesture
                self.stable_gesture = detected_gesture
                self.gesture_start_time = now

                # Verify cooldown
                last_time = self.last_trigger_time.get(detected_gesture, 0.0)
                if now - last_time >= self.cooldown_seconds:
                    is_new_event = True
                    self.last_trigger_time[detected_gesture] = now
            else:
                # Continuing the same gesture
                hold_duration = now - self.gesture_start_time
        elif detected_gesture == GestureType.NONE:
            if len(self._history) >= 2 and all(g == GestureType.NONE for g in list(self._history)[-2:]):
                self.stable_gesture = GestureType.NONE
                self.gesture_start_time = 0.0

        return self.stable_gesture, is_new_event, hold_duration

    def get_stability_ratio(self) -> float:
        """Returns the ratio of frames in history matching the raw gesture."""
        if not self._history or self.raw_gesture == GestureType.NONE:
            return 0.0
        matches = sum(1 for g in self._history if g == self.raw_gesture)
        return matches / float(self._history.maxlen)

    def trigger_cooldown(self, gesture: GestureType, duration: Optional[float] = None):
        """Manually forces a cooldown for a specific gesture."""
        self.last_trigger_time[gesture] = time.time() + (duration if duration is not None else self.cooldown_seconds)

    def reset(self):
        """Clears state history."""
        self._history.clear()
        self.raw_gesture = GestureType.NONE
        self.stable_gesture = GestureType.NONE
        self.gesture_start_time = 0.0


class GestureEngine:
    """
    Central orchestration engine:
    Tracks modes, routes stable gestures, and applies emergency stop locks.
    """

    def __init__(self, stability_frames: int = 4, cooldown_seconds: float = 0.4):
        self.stability_tracker = GestureStabilityTracker(
            required_frames=stability_frames,
            cooldown_seconds=cooldown_seconds
        )
        self.current_mode = AppMode.MOUSE_CONTROL
        self.emergency_stop = False
        self.last_action_desc = "Idle"

    def set_mode(self, mode: AppMode):
        """Switches the active operating mode."""
        if mode != self.current_mode:
            logger.info(f"Operating mode changed: {self.current_mode.value} -> {mode.value}")
            self.current_mode = mode
            self.stability_tracker.reset()
            self.last_action_desc = f"Switched to {mode.value}"

    def trigger_emergency_stop(self):
        """Activates emergency safety lock, freezing all automation."""
        self.emergency_stop = True
        self.last_action_desc = "EMERGENCY STOP ACTIVATED"
        logger.warning("EMERGENCY STOP ACTIVATED. All desktop inputs disabled.")

    def reset_emergency_stop(self):
        """Re-enables automation after emergency stop."""
        self.emergency_stop = False
        self.stability_tracker.reset()
        self.last_action_desc = "Automation Resumed"
        logger.info("Emergency stop cleared. Automation resumed.")

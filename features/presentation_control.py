"""
GestureLink - Presentation Control Module
Allows touchless slide navigation (PowerPoint, Google Slides, Keynote, PDF viewers)
using directional hand gestures and hand swipes.
"""

import time
from typing import Tuple, Optional
from controls.keyboard_control import KeyboardController
from utils.logger import get_logger

logger = get_logger("PresentationControl")


class PresentationController:
    """
    Manages presentation slideshows via safe keyboard events,
    with swipe velocity detection, debouncing, and visual status feedback.
    """

    def __init__(self, keyboard_controller: Optional[KeyboardController] = None,
                 swipe_threshold: float = 0.12, action_cooldown: float = 0.8):
        self.kb = keyboard_controller if keyboard_controller is not None else KeyboardController()
        self.swipe_threshold = swipe_threshold
        self.action_cooldown = action_cooldown

        self.last_action_time = 0.0
        self.last_action_desc = "Ready"
        self.prev_hand_x: Optional[float] = None

    def handle_swipe(self, norm_x: float) -> Optional[str]:
        """
        Detects rapid horizontal hand movement (swiping right or left) to advance slides.
        """
        now = time.time()
        if now - self.last_action_time < self.action_cooldown:
            self.prev_hand_x = norm_x
            return None

        if self.prev_hand_x is None:
            self.prev_hand_x = norm_x
            return None

        dx = norm_x - self.prev_hand_x
        self.prev_hand_x = norm_x

        # Moving right in mirrored frame means user moved hand right
        if dx > self.swipe_threshold:
            return self.next_slide()
        elif dx < -self.swipe_threshold:
            return self.previous_slide()

        return None

    def next_slide(self) -> str:
        """Triggers next slide via Right Arrow key."""
        now = time.time()
        if now - self.last_action_time >= self.action_cooldown:
            if self.kb.press("right", cooldown=0.1):
                self.last_action_time = now
                self.last_action_desc = "Next Slide >>"
                logger.info("Presentation Action: Next Slide")
                return self.last_action_desc
        return ""

    def previous_slide(self) -> str:
        """Triggers previous slide via Left Arrow key."""
        now = time.time()
        if now - self.last_action_time >= self.action_cooldown:
            if self.kb.press("left", cooldown=0.1):
                self.last_action_time = now
                self.last_action_desc = "<< Previous Slide"
                logger.info("Presentation Action: Previous Slide")
                return self.last_action_desc
        return ""

    def start_presentation(self) -> str:
        """Starts slideshow from beginning via F5 key."""
        now = time.time()
        if now - self.last_action_time >= self.action_cooldown:
            if self.kb.press("f5", cooldown=0.1):
                self.last_action_time = now
                self.last_action_desc = "Slideshow Started (F5)"
                logger.info("Presentation Action: Start Slideshow")
                return self.last_action_desc
        return ""

    def exit_presentation(self) -> str:
        """Exits presentation via Escape key."""
        now = time.time()
        if now - self.last_action_time >= self.action_cooldown:
            if self.kb.press("escape", cooldown=0.1):
                self.last_action_time = now
                self.last_action_desc = "Slideshow Exited (ESC)"
                logger.info("Presentation Action: Exit Slideshow")
                return self.last_action_desc
        return ""

    def reset_tracking(self):
        """Resets hand position history."""
        self.prev_hand_x = None

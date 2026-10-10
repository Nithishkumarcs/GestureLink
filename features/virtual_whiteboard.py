"""
GestureLink - Virtual Whiteboard Feature
Dedicated, high-resolution digital whiteboard window controlled touchlessly via hand gestures.
Supports drawing, erasing, undo, redo, color selection, and PNG export.
"""

import os
import time
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any
import cv2
import numpy as np
from utils.logger import get_logger
from utils.helpers import calculate_distance_2d

logger = get_logger("VirtualWhiteboard")


class VirtualWhiteboard:
    """
    High-resolution virtual whiteboard canvas with state history (undo/redo),
    touchless gesture drawing, and color palettes.
    """

    COLORS = {
        "White": (255, 255, 255),
        "Cyan": (255, 235, 0),
        "Emerald": (80, 240, 100),
        "Gold": (0, 200, 255),
        "Coral": (80, 100, 255),
        "Purple": (255, 100, 200),
    }

    def __init__(self, width: int = 1280, height: int = 720, dark_theme: bool = True):
        self.width = width
        self.height = height
        self.dark_theme = dark_theme
        self.bg_color = (24, 28, 38) if dark_theme else (245, 245, 250)

        # Drawing canvas (BGR)
        self.canvas = np.full((height, width, 3), self.bg_color, dtype=np.uint8)

        # History stacks for Undo / Redo
        self.undo_stack: List[np.ndarray] = []
        self.redo_stack: List[np.ndarray] = []
        self.max_history = 20

        # Pen configuration
        self.current_color_name = "Cyan" if dark_theme else "Coral"
        self.current_color = self.COLORS[self.current_color_name]
        self.brush_size = 5
        self.eraser_size = 35

        # Drawing state
        self.is_drawing = False
        self.last_pos: Optional[Tuple[int, int]] = None

        # Captures directory
        self.captures_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "captures"
        )
        os.makedirs(self.captures_dir, exist_ok=True)

    def set_color(self, color_name: str):
        """Sets drawing color."""
        if color_name in self.COLORS:
            self.current_color_name = color_name
            self.current_color = self.COLORS[color_name]
            logger.info(f"Whiteboard color set to {color_name}")

    def cycle_color(self) -> str:
        """Cycles to next color in palette."""
        keys = list(self.COLORS.keys())
        idx = (keys.index(self.current_color_name) + 1) % len(keys)
        self.set_color(keys[idx])
        return keys[idx]

    def _save_state(self):
        """Saves current canvas state before a new stroke for undo."""
        self.undo_stack.append(self.canvas.copy())
        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)
        self.redo_stack.clear()

    def process_gesture_point(self, norm_x: float, norm_y: float, action: str) -> Tuple[int, int]:
        """
        Translates normalized coordinates from camera to high-resolution whiteboard pixels
        and executes the requested action ('draw', 'erase', 'hover').
        """
        px = int(np.clip(norm_x * self.width, 0, self.width - 1))
        py = int(np.clip(norm_y * self.height, 0, self.height - 1))
        curr_pos = (px, py)

        if action == "draw":
            if not self.is_drawing:
                self._save_state()
                self.is_drawing = True
                self.last_pos = curr_pos

            if self.last_pos is not None:
                dist = calculate_distance_2d(self.last_pos, curr_pos)
                if dist >= 2.0:
                    cv2.line(self.canvas, self.last_pos, curr_pos, self.current_color, self.brush_size, cv2.LINE_AA)
                    cv2.circle(self.canvas, curr_pos, self.brush_size // 2, self.current_color, -1, cv2.LINE_AA)
                    self.last_pos = curr_pos

        elif action == "erase":
            if self.is_drawing:
                self.is_drawing = False
                self.last_pos = None

            cv2.circle(self.canvas, curr_pos, self.eraser_size, self.bg_color, -1)

        else:  # hover / stop
            self.is_drawing = False
            self.last_pos = None

        return px, py

    def undo(self) -> bool:
        """Restores previous canvas state."""
        if not self.undo_stack:
            return False
        self.redo_stack.append(self.canvas.copy())
        self.canvas = self.undo_stack.pop()
        self.last_pos = None
        self.is_drawing = False
        logger.info("Whiteboard Undo executed.")
        return True

    def redo(self) -> bool:
        """Reapplies undone action."""
        if not self.redo_stack:
            return False
        self.undo_stack.append(self.canvas.copy())
        self.canvas = self.redo_stack.pop()
        self.last_pos = None
        self.is_drawing = False
        logger.info("Whiteboard Redo executed.")
        return True

    def clear(self):
        """Clears the entire whiteboard canvas."""
        self._save_state()
        self.canvas[:] = self.bg_color
        self.last_pos = None
        self.is_drawing = False
        logger.info("Whiteboard cleared.")

    def save_as_png(self) -> Tuple[bool, str]:
        """Saves current whiteboard to PNG image."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"whiteboard_{timestamp}.png"
        filepath = os.path.join(self.captures_dir, filename)

        try:
            cv2.imwrite(filepath, self.canvas)
            logger.info(f"Saved whiteboard to {filepath}")
            return True, filepath
        except Exception as e:
            err = f"Failed to save whiteboard image: {e}"
            logger.error(err)
            return False, err

    def get_render_frame(self, cursor_pos: Optional[Tuple[int, int]] = None,
                         cursor_mode: str = "hover") -> np.ndarray:
        """
        Returns a copy of the canvas with a visual gesture cursor indicator overlay.
        """
        display = self.canvas.copy()

        if cursor_pos is not None:
            cx, cy = cursor_pos
            if cursor_mode == "draw":
                cv2.circle(display, (cx, cy), self.brush_size + 4, self.current_color, 2, cv2.LINE_AA)
                cv2.circle(display, (cx, cy), 3, (255, 255, 255), -1, cv2.LINE_AA)
            elif cursor_mode == "erase":
                cv2.circle(display, (cx, cy), self.eraser_size, (100, 100, 255), 2, cv2.LINE_AA)
            else:  # hover
                cv2.circle(display, (cx, cy), 8, (200, 200, 200), 1, cv2.LINE_AA)
                cv2.circle(display, (cx, cy), 2, (255, 255, 255), -1, cv2.LINE_AA)

        return display

"""
GestureLink - Air Writing Feature
Tracks index fingertip in 3D/2D space to draw smooth digital strokes in the air.
Supports multiple colors, anti-jitter smoothing, stroke undo, eraser mode, and PNG export.
"""

import os
import time
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any
import cv2
import numpy as np
from utils.logger import get_logger
from utils.helpers import calculate_distance_2d

logger = get_logger("AirWriting")

COLOR_PALETTE = {
    "Cyan": (255, 235, 0),        # BGR
    "Neon Green": (50, 255, 50),
    "Sunburst": (0, 165, 255),
    "Magenta": (255, 50, 255),
    "White": (255, 255, 255),
}


class AirWriter:
    """
    Manages air writing strokes, real-time smoothing, eraser mechanics,
    and rendering on top of camera frames or independent canvases.
    """

    def __init__(self, width: int = 640, height: int = 480, 
                 default_color_name: str = "Cyan", thickness: int = 4):
        self.width = width
        self.height = height
        self.canvas = np.zeros((height, width, 4), dtype=np.uint8)  # BGRA canvas
        self.thickness = thickness
        self.current_color_name = default_color_name
        self.color_bgr = COLOR_PALETTE.get(default_color_name, (255, 235, 0))

        # Stroke tracking: List of strokes, where each stroke is a list of points (x, y)
        self.strokes: List[Dict[str, Any]] = []
        self.current_stroke: Optional[List[Tuple[int, int]]] = None
        self.last_point: Optional[Tuple[int, int]] = None
        self.eraser_radius = 28

        # Captures directory
        self.captures_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "captures"
        )
        os.makedirs(self.captures_dir, exist_ok=True)

    def set_color(self, color_name: str):
        """Changes the active drawing color."""
        if color_name in COLOR_PALETTE:
            self.current_color_name = color_name
            self.color_bgr = COLOR_PALETTE[color_name]
            logger.info(f"Air writing color set to {color_name}")

    def cycle_color(self) -> str:
        """Cycles to the next available color in the palette."""
        colors = list(COLOR_PALETTE.keys())
        idx = (colors.index(self.current_color_name) + 1) % len(colors)
        self.set_color(colors[idx])
        return colors[idx]

    def add_point(self, px: int, py: int):
        """Adds a point to the current stroke with interpolation to prevent gaps."""
        curr_pt = (int(px), int(py))

        if self.current_stroke is None:
            # Start new stroke
            self.current_stroke = [curr_pt]
            self.last_point = curr_pt
            return

        # Check distance from last point
        dist = calculate_distance_2d(self.last_point, curr_pt)
        if dist < 2.0:
            return  # Filter micro-movements

        # Draw segment onto canvas
        cv2.line(
            self.canvas,
            self.last_point,
            curr_pt,
            (*self.color_bgr, 255),
            self.thickness,
            cv2.LINE_AA
        )
        cv2.circle(
            self.canvas,
            curr_pt,
            self.thickness // 2,
            (*self.color_bgr, 255),
            -1,
            cv2.LINE_AA
        )

        self.current_stroke.append(curr_pt)
        self.last_point = curr_pt

    def end_stroke(self):
        """Finalizes the current stroke when pen lifts (e.g. hand opens or changes gesture)."""
        if self.current_stroke and len(self.current_stroke) > 1:
            self.strokes.append({
                "points": list(self.current_stroke),
                "color": self.color_bgr,
                "thickness": self.thickness
            })
        self.current_stroke = None
        self.last_point = None

    def erase_at(self, px: int, py: int):
        """Erases strokes near the specified fingertip position."""
        self.end_stroke()
        # Clear circle on BGRA canvas
        cv2.circle(self.canvas, (int(px), int(py)), self.eraser_radius, (0, 0, 0, 0), -1)

    def undo(self) -> bool:
        """Removes the most recent stroke and rebuilds the canvas."""
        if not self.strokes:
            return False

        self.strokes.pop()
        self._rebuild_canvas()
        logger.info("Undid last air writing stroke.")
        return True

    def clear(self):
        """Clears all strokes and resets the canvas."""
        self.strokes.clear()
        self.current_stroke = None
        self.last_point = None
        self.canvas[:] = (0, 0, 0, 0)
        logger.info("Air writing canvas cleared.")

    def _rebuild_canvas(self):
        """Re-draws all saved strokes onto a fresh canvas."""
        self.canvas = np.zeros((self.height, self.width, 4), dtype=np.uint8)
        for stroke in self.strokes:
            points = stroke["points"]
            color = stroke["color"]
            thick = stroke["thickness"]
            for i in range(1, len(points)):
                cv2.line(self.canvas, points[i - 1], points[i], (*color, 255), thick, cv2.LINE_AA)
                cv2.circle(self.canvas, points[i], thick // 2, (*color, 255), -1, cv2.LINE_AA)

    def overlay_on_frame(self, frame: np.ndarray) -> np.ndarray:
        """Blends the BGRA drawing canvas smoothly onto an input BGR camera frame."""
        if frame.shape[0] != self.height or frame.shape[1] != self.width:
            canvas_resized = cv2.resize(self.canvas, (frame.shape[1], frame.shape[0]), interpolation=cv2.INTER_NEAREST)
        else:
            canvas_resized = self.canvas

        # Alpha blending
        alpha = canvas_resized[:, :, 3] / 255.0
        for c in range(3):
            frame[:, :, c] = (1.0 - alpha) * frame[:, :, c] + alpha * canvas_resized[:, :, c]

        return frame

    def save_as_png(self, background_frame: Optional[np.ndarray] = None) -> Tuple[bool, str]:
        """
        Saves the air writing drawing as a PNG image to the captures directory.
        Returns (success: bool, filepath: str).
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"air_writing_{timestamp}.png"
        filepath = os.path.join(self.captures_dir, filename)

        try:
            if background_frame is not None:
                # Save combined image
                out_img = background_frame.copy()
                self.overlay_on_frame(out_img)
                cv2.imwrite(filepath, out_img)
            else:
                # Save transparent drawing
                cv2.imwrite(filepath, self.canvas)

            logger.info(f"Saved air writing drawing to {filepath}")
            return True, filepath
        except Exception as e:
            err = f"Failed to save air writing image: {e}"
            logger.error(err)
            return False, err

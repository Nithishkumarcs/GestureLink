"""
GestureLink - Helper Utilities
Geometric calculations, coordinate transformations, smoothing, and OpenCV HUD drawing.
"""

import math
import cv2
import numpy as np
from typing import Tuple, List, Optional, Union


def calculate_distance_2d(p1: Union[Tuple[float, float], List[float]], 
                          p2: Union[Tuple[float, float], List[float]]) -> float:
    """Calculates Euclidean distance between two 2D points."""
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def calculate_distance_3d(p1: Union[Tuple[float, float, float], List[float]], 
                          p2: Union[Tuple[float, float, float], List[float]]) -> float:
    """Calculates Euclidean distance between two 3D points."""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2 + (p1[2] - p2[2])**2)


def calculate_angle(a: Tuple[float, float], 
                    b: Tuple[float, float], 
                    c: Tuple[float, float]) -> float:
    """
    Calculates angle ABC (vertex at B) in degrees [0, 180].
    """
    ba = (a[0] - b[0], a[1] - b[1])
    bc = (c[0] - b[0], c[1] - b[1])

    dot_product = ba[0] * bc[0] + ba[1] * bc[1]
    mag_ba = math.hypot(ba[0], ba[1])
    mag_bc = math.hypot(bc[0], bc[1])

    if mag_ba * mag_bc == 0:
        return 0.0

    cosine_angle = dot_product / (mag_ba * mag_bc)
    cosine_angle = max(-1.0, min(1.0, cosine_angle))
    return math.degrees(math.acos(cosine_angle))


def map_range(val: float, in_min: float, in_max: float, 
              out_min: float, out_max: float, clamp: bool = True) -> float:
    """Maps a value from input range to output range, with optional clamping."""
    if in_max == in_min:
        return out_min
    normalized = (val - in_min) / (in_max - in_min)
    if clamp:
        normalized = max(0.0, min(1.0, normalized))
    return out_min + normalized * (out_max - out_min)


def exponential_smoothing(current: float, target: float, alpha: float) -> float:
    """
    Applies exponential moving average filter.
    alpha in (0, 1]: higher alpha = faster response, lower alpha = smoother.
    """
    alpha = max(0.01, min(1.0, alpha))
    return alpha * target + (1.0 - alpha) * current


def smooth_point(prev_point: Optional[Tuple[float, float]], 
                 curr_point: Tuple[float, float], 
                 alpha: float) -> Tuple[float, float]:
    """Smooths a 2D coordinate point using EMA."""
    if prev_point is None:
        return curr_point
    return (
        exponential_smoothing(prev_point[0], curr_point[0], alpha),
        exponential_smoothing(prev_point[1], curr_point[1], alpha)
    )


def calculate_palm_scale(landmarks: List[dict]) -> float:
    """
    Calculates the palm scale based on distance between Wrist (0) and Middle MCP (9).
    Used to normalize gesture thresholds regardless of distance from camera.
    """
    if len(landmarks) < 10:
        return 0.2  # default sensible fallback
    p0 = (landmarks[0]["x"], landmarks[0]["y"])
    p9 = (landmarks[9]["x"], landmarks[9]["y"])
    dist = calculate_distance_2d(p0, p9)
    return max(0.05, dist)


# --- OpenCV HUD Drawing Helpers ---

def draw_hud_box(frame: np.ndarray, x1: int, y1: int, x2: int, y2: int, 
                 color: Tuple[int, int, int] = (0, 220, 255), 
                 thickness: int = 1, corner_len: int = 20) -> None:
    """Draws a futuristic HUD bounding box with highlighted corners."""
    # Thin frame outline
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)

    c_thick = thickness + 2
    # Top-Left corner
    cv2.line(frame, (x1, y1), (x1 + corner_len, y1), color, c_thick)
    cv2.line(frame, (x1, y1), (x1, y1 + corner_len), color, c_thick)
    # Top-Right corner
    cv2.line(frame, (x2, y1), (x2 - corner_len, y1), color, c_thick)
    cv2.line(frame, (x2, y1), (x2, y1 + corner_len), color, c_thick)
    # Bottom-Left corner
    cv2.line(frame, (x1, y2), (x1 + corner_len, y2), color, c_thick)
    cv2.line(frame, (x1, y2), (x1, y2 - corner_len), color, c_thick)
    # Bottom-Right corner
    cv2.line(frame, (x2, y2), (x2 - corner_len, y2), color, c_thick)
    cv2.line(frame, (x2, y2), (x2, y2 - corner_len), color, c_thick)


def draw_text_with_background(frame: np.ndarray, text: str, 
                              origin: Tuple[int, int], 
                              font_scale: float = 0.55, 
                              text_color: Tuple[int, int, int] = (255, 255, 255), 
                              bg_color: Tuple[int, int, int] = (20, 24, 33), 
                              alpha: float = 0.75, 
                              padding: int = 6) -> None:
    """Draws text with a semi-transparent dark rounded badge background."""
    font = cv2.FONT_HERSHEY_SIMPLEX
    thickness = 1
    (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)

    x, y = origin
    x1 = max(0, x - padding)
    y1 = max(0, y - text_h - padding)
    x2 = min(frame.shape[1], x + text_w + padding)
    y2 = min(frame.shape[0], y + baseline + padding)

    overlay = frame.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), bg_color, -1)
    cv2.addWeighted(overlay, alpha, frame, 1.0 - alpha, 0, frame)

    cv2.putText(frame, text, (x, y), font, font_scale, text_color, thickness, cv2.LINE_AA)

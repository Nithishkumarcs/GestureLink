"""
GestureLink - Gesture Recognition Module
Classifies hand landmarks into distinct, robust gestures using normalized geometry and angles.
"""

from enum import Enum
from typing import Dict, List, Any, Tuple, Optional
from utils.helpers import calculate_distance_2d, calculate_angle
from utils.logger import get_logger

logger = get_logger("GestureRecognition")


class GestureType(Enum):
    NONE = "None"
    OPEN_PALM = "Open Palm"         # 🖐️
    INDEX_FINGER = "Index Finger"   # ☝️
    TWO_FINGERS = "Two Fingers"     # ✌️
    PINCH = "Pinch"                 # 🤏
    FIST = "Fist"                   # ✊
    THUMB_UP = "Thumb Up"           # 👍
    THUMB_DOWN = "Thumb Down"       # 👎
    OK_GESTURE = "OK Gesture"       # 👌


GESTURE_EMOJIS = {
    GestureType.NONE: "⚪",
    GestureType.OPEN_PALM: "🖐️",
    GestureType.INDEX_FINGER: "☝️",
    GestureType.TWO_FINGERS: "✌️",
    GestureType.PINCH: "🤏",
    GestureType.FIST: "✊",
    GestureType.THUMB_UP: "👍",
    GestureType.THUMB_DOWN: "👎",
    GestureType.OK_GESTURE: "👌",
}


class GestureRecognizer:
    """
    Analyzes hand landmarks, finger extension states, and relative distances
    to classify gestures reliably across varying camera distances.
    """

    def __init__(self, pinch_threshold: float = 0.055):
        self.pinch_threshold = pinch_threshold

    def recognize(self, hand_data: Dict[str, Any]) -> Tuple[GestureType, float, Dict[str, Any]]:
        """
        Recognizes the active gesture from detected hand data.

        Returns:
            Tuple of:
            - GestureType enum
            - Confidence score (float 0.0 to 1.0)
            - Extra metrics dict (e.g. pinch_distance, velocity, swipe direction)
        """
        if not hand_data or "landmarks" not in hand_data:
            return GestureType.NONE, 0.0, {}

        lms = hand_data["landmarks"]
        finger_states = hand_data.get("finger_states", {})
        palm_scale = hand_data.get("palm_scale", 0.2)

        thumb_open = finger_states.get("thumb", False)
        index_open = finger_states.get("index", False)
        middle_open = finger_states.get("middle", False)
        ring_open = finger_states.get("ring", False)
        pinky_open = finger_states.get("pinky", False)

        # Landmark points
        wrist = (lms[0]["x"], lms[0]["y"])
        thumb_tip = (lms[4]["x"], lms[4]["y"])
        thumb_mcp = (lms[2]["x"], lms[2]["y"])
        index_tip = (lms[8]["x"], lms[8]["y"])
        index_mcp = (lms[5]["x"], lms[5]["y"])

        # Normalized pinch distance relative to palm scale
        raw_pinch_dist = calculate_distance_2d(thumb_tip, index_tip)
        normalized_pinch_dist = raw_pinch_dist / max(0.01, palm_scale)
        is_pinched = normalized_pinch_dist < (self.pinch_threshold * 5.0)

        # 1. OK Gesture (👌): Thumb and index pinched, while middle, ring, pinky are extended
        if is_pinched and middle_open and ring_open:
            confidence = min(1.0, max(0.7, 1.0 - (normalized_pinch_dist / (self.pinch_threshold * 5.0)) * 0.3))
            return GestureType.OK_GESTURE, confidence, {
                "pinch_distance": raw_pinch_dist,
                "normalized_pinch_dist": normalized_pinch_dist
            }

        # 2. Pinch Gesture (🤏): Thumb and index pinched, other fingers NOT all open
        if is_pinched and not (middle_open and ring_open and pinky_open):
            confidence = min(1.0, max(0.65, 1.0 - (normalized_pinch_dist / (self.pinch_threshold * 5.0)) * 0.35))
            return GestureType.PINCH, confidence, {
                "pinch_distance": raw_pinch_dist,
                "normalized_pinch_dist": normalized_pinch_dist
            }

        # 3. Open Palm (🖐️): All 5 fingers extended open
        if thumb_open and index_open and middle_open and ring_open and pinky_open:
            return GestureType.OPEN_PALM, 0.95, {}

        # 4. Fist (✊): All fingers closed
        if not index_open and not middle_open and not ring_open and not pinky_open and not thumb_open:
            return GestureType.FIST, 0.92, {}

        # 5. Thumb Up (👍): Thumb open pointing upward, other 4 fingers closed
        if thumb_open and not index_open and not middle_open and not ring_open and not pinky_open:
            # Check orientation: thumb tip is significantly higher (lower Y in screen coords) than thumb MCP
            dy = thumb_tip[1] - thumb_mcp[1]
            dx = abs(thumb_tip[0] - thumb_mcp[0])

            if dy < -0.04 and abs(dy) > dx * 0.7:  # Pointing upward
                return GestureType.THUMB_UP, 0.90, {"dy": dy}

            if dy > 0.04 and abs(dy) > dx * 0.7:   # Pointing downward
                return GestureType.THUMB_DOWN, 0.90, {"dy": dy}

        # 6. Two Fingers (✌️): Index and Middle open, Ring and Pinky closed
        if index_open and middle_open and not ring_open and not pinky_open:
            return GestureType.TWO_FINGERS, 0.90, {
                "index_tip": index_tip,
                "middle_tip": (lms[12]["x"], lms[12]["y"])
            }

        # 7. Index Finger (☝️): Index open, Middle, Ring, Pinky closed
        if index_open and not middle_open and not ring_open and not pinky_open:
            return GestureType.INDEX_FINGER, 0.92, {
                "index_tip": index_tip
            }

        # Safe fallback: if partially open palm
        if index_open and middle_open and ring_open and pinky_open:
            return GestureType.OPEN_PALM, 0.80, {}

        return GestureType.NONE, 0.0, {}

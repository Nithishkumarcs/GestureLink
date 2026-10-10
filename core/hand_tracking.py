"""
GestureLink - Hand Tracking Module
Robust hand detection and 21-landmark tracking supporting MediaPipe Tasks and MediaPipe Solutions,
with rotation-invariant, distance-independent finger state determination.
"""

import os
import cv2
import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from utils.logger import get_logger
from utils.helpers import calculate_distance_2d, calculate_angle, calculate_palm_scale

logger = get_logger("HandTracking")

# Standard MediaPipe 21 Landmark Indices
WRIST = 0
THUMB_CMC = 1
THUMB_MCP = 2
THUMB_IP = 3
THUMB_TIP = 4
INDEX_MCP = 5
INDEX_PIP = 6
INDEX_DIP = 7
INDEX_TIP = 8
MIDDLE_MCP = 9
MIDDLE_PIP = 10
MIDDLE_DIP = 11
MIDDLE_TIP = 12
RING_MCP = 13
RING_PIP = 14
RING_DIP = 15
RING_TIP = 16
PINKY_MCP = 17
PINKY_PIP = 18
PINKY_DIP = 19
PINKY_TIP = 20

HAND_CONNECTIONS = [
    # Palm
    (WRIST, INDEX_MCP), (INDEX_MCP, MIDDLE_MCP), (MIDDLE_MCP, RING_MCP), 
    (RING_MCP, PINKY_MCP), (PINKY_MCP, WRIST),
    # Thumb
    (WRIST, THUMB_CMC), (THUMB_CMC, THUMB_MCP), (THUMB_MCP, THUMB_IP), (THUMB_IP, THUMB_TIP),
    # Index
    (INDEX_MCP, INDEX_PIP), (INDEX_PIP, INDEX_DIP), (INDEX_DIP, INDEX_TIP),
    # Middle
    (MIDDLE_MCP, MIDDLE_PIP), (MIDDLE_PIP, MIDDLE_DIP), (MIDDLE_DIP, MIDDLE_TIP),
    # Ring
    (RING_MCP, RING_PIP), (RING_PIP, RING_DIP), (RING_DIP, RING_TIP),
    # Pinky
    (PINKY_MCP, PINKY_PIP), (PINKY_PIP, PINKY_DIP), (PINKY_DIP, PINKY_TIP),
]


class HandTracker:
    """
    Detects hands, tracks 21 3D landmarks, and computes geometric finger states.
    Automatically handles MediaPipe Tasks HandLandmarker or fallback to Solutions.
    """

    def __init__(self, model_path: Optional[str] = None, max_num_hands: int = 1,
                 min_detection_confidence: float = 0.6, min_tracking_confidence: float = 0.5):
        self.max_num_hands = max_num_hands
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self.engine_type = "unknown"
        self.landmarker = None
        self.solutions_hands = None

        # Resolve model path
        if model_path is None or not os.path.exists(model_path):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base_dir, "assets", "models", "hand_landmarker.task")

        self.model_path = model_path
        self._init_tracker()

    def _init_tracker(self):
        """Initializes the hand tracking engine."""
        # 1. Try MediaPipe Tasks API (MediaPipe 1.0+)
        try:
            import mediapipe as mp
            from mediapipe.tasks.python import vision
            from mediapipe.tasks.python.core import base_options

            if os.path.exists(self.model_path):
                options = vision.HandLandmarkerOptions(
                    base_options=base_options.BaseOptions(model_asset_path=self.model_path),
                    running_mode=vision.RunningMode.IMAGE,
                    num_hands=self.max_num_hands,
                    min_hand_detection_confidence=self.min_detection_confidence,
                    min_tracking_confidence=self.min_tracking_confidence
                )
                self.landmarker = vision.HandLandmarker.create_from_options(options)
                self.engine_type = "tasks"
                logger.info(f"MediaPipe Tasks HandLandmarker initialized using {self.model_path}")
                return
            else:
                logger.warning(f"Tasks model file not found at {self.model_path}")
        except Exception as e:
            logger.warning(f"Could not initialize MediaPipe Tasks: {e}")

        # 2. Try MediaPipe Solutions API (MediaPipe < 1.0)
        try:
            import mediapipe as mp
            if hasattr(mp, "solutions") and hasattr(mp.solutions, "hands"):
                self.solutions_hands = mp.solutions.hands.Hands(
                    static_image_mode=False,
                    max_num_hands=self.max_num_hands,
                    min_detection_confidence=self.min_detection_confidence,
                    min_tracking_confidence=self.min_tracking_confidence
                )
                self.engine_type = "solutions"
                logger.info("MediaPipe Solutions Hands initialized successfully.")
                return
        except Exception as e:
            logger.warning(f"Could not initialize MediaPipe Solutions: {e}")

        logger.error("Failed to initialize any hand tracking engine. Hand tracking will be offline.")
        self.engine_type = "none"

    def process(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Processes an RGB frame and returns detected hands with landmarks and finger states.
        
        Returns:
            List of dictionaries for each detected hand:
            {
                "landmarks": List of 21 dicts [{'x': float, 'y': float, 'z': float, 'px': int, 'py': int}],
                "handedness": "Right" or "Left",
                "palm_scale": float,
                "finger_states": {
                    "thumb": bool,
                    "index": bool,
                    "middle": bool,
                    "ring": bool,
                    "pinky": bool
                }
            }
        """
        if frame is None or self.engine_type == "none":
            return []

        h, w, _ = frame.shape
        detected_hands = []

        if self.engine_type == "tasks":
            detected_hands = self._process_tasks(frame, w, h)
        elif self.engine_type == "solutions":
            detected_hands = self._process_solutions(frame, w, h)

        return detected_hands

    def _process_tasks(self, frame: np.ndarray, w: int, h: int) -> List[Dict[str, Any]]:
        """Processes frame using MediaPipe Tasks HandLandmarker."""
        import mediapipe as mp
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        result = self.landmarker.detect(mp_image)
        if not result or not result.hand_landmarks:
            return []

        hands_data = []
        for i, raw_landmarks in enumerate(result.hand_landmarks):
            handedness = "Right"
            if result.handedness and i < len(result.handedness) and result.handedness[i]:
                handedness = result.handedness[i][0].category_name

            landmarks = []
            for lm in raw_landmarks:
                px = int(np.clip(lm.x * w, 0, w - 1))
                py = int(np.clip(lm.y * h, 0, h - 1))
                landmarks.append({
                    "x": float(lm.x),
                    "y": float(lm.y),
                    "z": float(lm.z),
                    "px": px,
                    "py": py
                })

            palm_scale = calculate_palm_scale(landmarks)
            finger_states = self.detect_finger_states(landmarks, palm_scale, handedness)

            hands_data.append({
                "landmarks": landmarks,
                "handedness": handedness,
                "palm_scale": palm_scale,
                "finger_states": finger_states
            })

        return hands_data

    def _process_solutions(self, frame: np.ndarray, w: int, h: int) -> List[Dict[str, Any]]:
        """Processes frame using MediaPipe Solutions Hands."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.solutions_hands.process(rgb_frame)

        if not result or not result.multi_hand_landmarks:
            return []

        hands_data = []
        for i, hand_lms in enumerate(result.multi_hand_landmarks):
            handedness = "Right"
            if result.multi_handedness and i < len(result.multi_handedness):
                handedness = result.multi_handedness[i].classification[0].label

            landmarks = []
            for lm in hand_lms.landmark:
                px = int(np.clip(lm.x * w, 0, w - 1))
                py = int(np.clip(lm.y * h, 0, h - 1))
                landmarks.append({
                    "x": float(lm.x),
                    "y": float(lm.y),
                    "z": float(lm.z),
                    "px": px,
                    "py": py
                })

            palm_scale = calculate_palm_scale(landmarks)
            finger_states = self.detect_finger_states(landmarks, palm_scale, handedness)

            hands_data.append({
                "landmarks": landmarks,
                "handedness": handedness,
                "palm_scale": palm_scale,
                "finger_states": finger_states
            })

        return hands_data

    def detect_finger_states(self, landmarks: List[Dict[str, Any]], palm_scale: float, handedness: str) -> Dict[str, bool]:
        """
        Determines whether each finger (Thumb, Index, Middle, Ring, Pinky) is OPEN (True) or CLOSED (False).
        Uses rotation-invariant landmark geometry and palm-relative distances.
        """
        if len(landmarks) < 21:
            return {"thumb": False, "index": False, "middle": False, "ring": False, "pinky": False}

        wrist = (landmarks[WRIST]["x"], landmarks[WRIST]["y"])

        # Check Index, Middle, Ring, Pinky
        # Tip must be significantly further from wrist than PIP and MCP joints
        finger_configs = [
            ("index", INDEX_TIP, INDEX_DIP, INDEX_PIP, INDEX_MCP),
            ("middle", MIDDLE_TIP, MIDDLE_DIP, MIDDLE_PIP, MIDDLE_MCP),
            ("ring", RING_TIP, RING_DIP, RING_PIP, RING_MCP),
            ("pinky", PINKY_TIP, PINKY_DIP, PINKY_PIP, PINKY_MCP),
        ]

        states = {}

        for name, tip_idx, dip_idx, pip_idx, mcp_idx in finger_configs:
            tip_pt = (landmarks[tip_idx]["x"], landmarks[tip_idx]["y"])
            pip_pt = (landmarks[pip_idx]["x"], landmarks[pip_idx]["y"])
            mcp_pt = (landmarks[mcp_idx]["x"], landmarks[mcp_idx]["y"])

            dist_tip_wrist = calculate_distance_2d(tip_pt, wrist)
            dist_pip_wrist = calculate_distance_2d(pip_pt, wrist)
            dist_tip_mcp = calculate_distance_2d(tip_pt, mcp_pt)
            dist_pip_mcp = calculate_distance_2d(pip_pt, mcp_pt)

            # Extended condition: tip is further from wrist than pip, and tip-mcp is extended
            is_extended = (dist_tip_wrist > dist_pip_wrist) and (dist_tip_mcp > dist_pip_mcp * 1.1)
            states[name] = bool(is_extended)

        # Thumb detection:
        # Check angle at MCP and IP, and distance of thumb tip from index MCP and pinky MCP
        thumb_tip = (landmarks[THUMB_TIP]["x"], landmarks[THUMB_TIP]["y"])
        thumb_ip = (landmarks[THUMB_IP]["x"], landmarks[THUMB_IP]["y"])
        thumb_mcp = (landmarks[THUMB_MCP]["x"], landmarks[THUMB_MCP]["y"])
        thumb_cmc = (landmarks[THUMB_CMC]["x"], landmarks[THUMB_CMC]["y"])
        index_mcp = (landmarks[INDEX_MCP]["x"], landmarks[INDEX_MCP]["y"])
        pinky_mcp = (landmarks[PINKY_MCP]["x"], landmarks[PINKY_MCP]["y"])

        thumb_angle = calculate_angle(thumb_cmc, thumb_mcp, thumb_tip)
        dist_thumb_index = calculate_distance_2d(thumb_tip, index_mcp)
        dist_thumb_pinky = calculate_distance_2d(thumb_tip, pinky_mcp)

        # Extended if thumb tip is moved away from palm and angle is reasonably straight
        thumb_open = (dist_thumb_index > palm_scale * 0.45) and (thumb_angle > 120.0 or dist_thumb_pinky > palm_scale * 0.8)
        states["thumb"] = bool(thumb_open)

        return states

    def draw_landmarks(self, frame: np.ndarray, landmarks: List[Dict[str, Any]], 
                       color_joints=(0, 255, 200), color_bones=(0, 160, 255)):
        """Draws a stylized cyberpunk-inspired hand skeleton on the frame."""
        if not landmarks or len(landmarks) < 21:
            return

        # Draw bone connections
        for start_idx, end_idx in HAND_CONNECTIONS:
            p1 = (landmarks[start_idx]["px"], landmarks[start_idx]["py"])
            p2 = (landmarks[end_idx]["px"], landmarks[end_idx]["py"])
            cv2.line(frame, p1, p2, color_bones, 2, cv2.LINE_AA)

        # Draw joints
        for i, lm in enumerate(landmarks):
            pt = (lm["px"], lm["py"])
            # Highlight fingertips
            if i in [THUMB_TIP, INDEX_TIP, MIDDLE_TIP, RING_TIP, PINKY_TIP]:
                cv2.circle(frame, pt, 6, (0, 255, 255), -1, cv2.LINE_AA)
                cv2.circle(frame, pt, 8, (255, 255, 255), 1, cv2.LINE_AA)
            else:
                cv2.circle(frame, pt, 3, color_joints, -1, cv2.LINE_AA)

    def close(self):
        """Releases underlying MediaPipe landmarker resources."""
        if self.landmarker is not None:
            try:
                self.landmarker.close()
            except Exception as e:
                logger.error(f"Error closing HandLandmarker: {e}")
            finally:
                self.landmarker = None

        if self.solutions_hands is not None:
            try:
                self.solutions_hands.close()
            except Exception as e:
                logger.error(f"Error closing solutions hands: {e}")
            finally:
                self.solutions_hands = None

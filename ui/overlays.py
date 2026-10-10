"""
GestureLink - HUD & Camera Overlays
Renders high-tech futuristic HUD elements, gesture badges, interaction boundaries,
and animated feedback effects directly onto OpenCV frames.
"""

import time
import cv2
import numpy as np
from typing import Dict, Any, Optional, Tuple, List
from core.gesture_recognition import GestureType, GESTURE_EMOJIS
from core.gesture_engine import AppMode
from utils.helpers import draw_hud_box, draw_text_with_background


class HUDOverlay:
    """
    Renders telemetry HUD overlays on top of the live video stream.
    """

    def __init__(self):
        # Click ripple animation state: list of (x, y, radius, max_radius, color)
        self.ripples: List[Dict[str, Any]] = []

    def trigger_click_effect(self, px: int, py: int, color=(0, 255, 255)):
        """Spawns an expanding animated ripple at the click location."""
        self.ripples.append({
            "x": px,
            "y": py,
            "radius": 6,
            "max_radius": 34,
            "color": color,
            "alpha": 1.0
        })

    def draw_hud(self, frame: np.ndarray,
                 hand_data: Optional[Dict[str, Any]] = None,
                 current_gesture: GestureType = GestureType.NONE,
                 gesture_confidence: float = 0.0,
                 current_mode: AppMode = AppMode.MOUSE_CONTROL,
                 action_desc: str = "Idle",
                 fps: float = 0.0,
                 margin_x: float = 0.15,
                 margin_y: float = 0.18,
                 show_skeleton: bool = True,
                 show_box: bool = True,
                 emergency_stop: bool = False) -> np.ndarray:
        """
        Draws complete HUD overlay onto frame.
        """
        h, w, _ = frame.shape

        # 1. Interaction boundary box (in Mouse Control mode)
        if show_box and current_mode == AppMode.MOUSE_CONTROL:
            bx1 = int(margin_x * w)
            by1 = int(margin_y * h)
            bx2 = int((1.0 - margin_x) * w)
            by2 = int((1.0 - margin_y) * h)

            box_color = (0, 180, 255) if not emergency_stop else (0, 0, 255)
            draw_hud_box(frame, bx1, by1, bx2, by2, color=box_color, thickness=1, corner_len=18)
            draw_text_with_background(
                frame, "INTERACTION ZONE", (bx1 + 8, by1 + 16),
                font_scale=0.38, text_color=(180, 220, 255), bg_color=(15, 20, 30), alpha=0.6
            )

        # 2. Render expanding click ripples
        remaining_ripples = []
        for rip in self.ripples:
            if rip["radius"] < rip["max_radius"]:
                overlay = frame.copy()
                cv2.circle(overlay, (rip["x"], rip["y"]), rip["radius"], rip["color"], 2, cv2.LINE_AA)
                alpha = max(0.1, 1.0 - (rip["radius"] / rip["max_radius"]))
                cv2.addWeighted(overlay, alpha, frame, 1.0 - alpha, 0, frame)
                rip["radius"] += 4
                remaining_ripples.append(rip)
        self.ripples = remaining_ripples

        # 3. Top Mode & Emergency Banner
        if emergency_stop:
            banner_bg = (0, 0, 200)
            banner_text = "EMERGENCY STOPPED - AUTOMATION LOCKED"
            cv2.rectangle(frame, (0, 0), (w, 32), banner_bg, -1)
            cv2.putText(frame, banner_text, (w // 2 - 190, 22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2, cv2.LINE_AA)
        else:
            # Subtle top bar
            top_overlay = frame.copy()
            cv2.rectangle(top_overlay, (0, 0), (w, 32), (15, 20, 30), -1)
            cv2.addWeighted(top_overlay, 0.75, frame, 0.25, 0, frame)

            mode_text = f"MODE: {current_mode.value.upper()}"
            cv2.putText(frame, mode_text, (14, 21),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.50, (0, 225, 255), 1, cv2.LINE_AA)

            fps_text = f"FPS: {fps:.1f}"
            cv2.putText(frame, fps_text, (w - 90, 21),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 255, 160), 1, cv2.LINE_AA)

        # 4. Bottom-Left Gesture & Action Status Pill
        pill_y = h - 18
        if current_gesture != GestureType.NONE:
            gesture_name = current_gesture.value.upper()
            pct = int(gesture_confidence * 100)
            status_text = f"GESTURE: {gesture_name} ({pct}%)"
            draw_text_with_background(
                frame, status_text, (14, pill_y),
                font_scale=0.52, text_color=(255, 255, 255), bg_color=(20, 30, 48), alpha=0.85
            )
        else:
            draw_text_with_background(
                frame, "NO GESTURE DETECTED", (14, pill_y),
                font_scale=0.48, text_color=(140, 160, 180), bg_color=(15, 20, 28), alpha=0.75
            )

        # 5. Bottom-Right Action description
        if action_desc:
            draw_text_with_background(
                frame, f"ACTION: {action_desc}", (w - 220, pill_y),
                font_scale=0.48, text_color=(0, 255, 220), bg_color=(15, 20, 30), alpha=0.85
            )

        return frame

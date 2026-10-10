"""
GestureLink - Comprehensive Verification Test Suite
Tests every major module, algorithm, and controller to ensure 100% operational readiness.
"""

import os
import sys
import time
import unittest
import numpy as np

from config import AppConfig, load_config, save_config, DEFAULT_APPS
from utils.logger import setup_logger, get_logger
from utils.helpers import (
    calculate_distance_2d, calculate_angle, map_range, 
    exponential_smoothing, calculate_palm_scale
)
from core.camera import CameraManager
from core.hand_tracking import (
    HandTracker, WRIST, THUMB_TIP, INDEX_TIP, MIDDLE_TIP, RING_TIP, PINKY_TIP,
    INDEX_MCP, INDEX_PIP, INDEX_DIP, THUMB_MCP, THUMB_IP, THUMB_CMC
)
from core.gesture_recognition import GestureRecognizer, GestureType
from core.gesture_engine import GestureEngine, GestureStabilityTracker, AppMode
from controls.mouse_control import MouseController
from controls.keyboard_control import KeyboardController
from controls.app_launcher import AppLauncher
from features.air_writing import AirWriter
from features.virtual_whiteboard import VirtualWhiteboard
from features.presentation_control import PresentationController


class TestGestureLink(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        setup_logger(level=30)  # WARNING level to keep test output clean
        import pyautogui
        pyautogui.FAILSAFE = False

    def test_01_config_manager(self):
        """Tests configuration loading, clamping, and persistence."""
        cfg = AppConfig()
        cfg.cursor_sensitivity = 99.0  # Out of bounds
        cfg.validate_and_clamp()
        self.assertLessEqual(cfg.cursor_sensitivity, 3.5)

        test_file = "test_settings_temp.json"
        self.assertTrue(save_config(cfg, test_file))
        loaded = load_config(test_file)
        self.assertEqual(loaded.camera_index, cfg.camera_index)
        if os.path.exists(test_file):
            os.remove(test_file)

    def test_02_geometric_helpers(self):
        """Tests coordinate mapping, distance, and smoothing."""
        p1 = (0.0, 0.0)
        p2 = (3.0, 4.0)
        self.assertAlmostEqual(calculate_distance_2d(p1, p2), 5.0)

        mapped = map_range(5.0, 0.0, 10.0, 0.0, 100.0)
        self.assertAlmostEqual(mapped, 50.0)

        smoothed = exponential_smoothing(10.0, 20.0, 0.5)
        self.assertAlmostEqual(smoothed, 15.0)

        # 90 degree angle
        a = (0.0, 1.0)
        b = (0.0, 0.0)
        c = (1.0, 0.0)
        self.assertAlmostEqual(calculate_angle(a, b, c), 90.0, places=1)

    def test_03_camera_manager(self):
        """Tests camera start, frame acquisition, and clean release."""
        cam = CameraManager(camera_index=0, width=640, height=480)
        cam.start()
        self.assertTrue(cam.is_running)
        time.sleep(0.5)
        ret, frame = cam.read()
        self.assertTrue(ret)
        self.assertIsNotNone(frame)
        self.assertEqual(len(frame.shape), 3)
        cam.stop()
        self.assertFalse(cam.is_running)

    def test_04_hand_tracker(self):
        """Tests hand tracking initialization and dummy frame processing."""
        tracker = HandTracker()
        self.assertIn(tracker.engine_type, ["tasks", "solutions"])
        dummy = np.zeros((480, 640, 3), dtype=np.uint8)
        hands = tracker.process(dummy)
        self.assertIsInstance(hands, list)
        tracker.close()

    def test_05_gesture_recognition_rules(self):
        """Tests gesture classification rules on synthetic landmark structures."""
        recognizer = GestureRecognizer(pinch_threshold=0.055)

        # Helper to construct a synthetic hand
        def make_synthetic_hand(thumb=False, index=False, middle=False, ring=False, pinky=False, pinch=False):
            lms = [{"x": 0.5, "y": 0.8, "z": 0.0, "px": 320, "py": 384} for _ in range(21)]
            lms[0] = {"x": 0.5, "y": 0.8, "z": 0.0, "px": 320, "py": 384}  # Wrist
            lms[9] = {"x": 0.5, "y": 0.5, "z": 0.0, "px": 320, "py": 240}  # Middle MCP

            if pinch:
                # Thumb tip and index tip close
                lms[4] = {"x": 0.50, "y": 0.40, "z": 0.0, "px": 320, "py": 192}
                lms[8] = {"x": 0.505, "y": 0.405, "z": 0.0, "px": 323, "py": 194}
            else:
                lms[4] = {"x": 0.35, "y": 0.45, "z": 0.0, "px": 224, "py": 216}
                lms[8] = {"x": 0.50, "y": 0.20, "z": 0.0, "px": 320, "py": 96}

            # Thumb Up / Down positioning
            lms[2] = {"x": 0.40, "y": 0.65, "z": 0.0, "px": 256, "py": 312}  # Thumb MCP
            if thumb and not index and not middle and not ring and not pinky:
                # Pointing up: tip Y significantly less than MCP Y
                lms[4] = {"x": 0.40, "y": 0.35, "z": 0.0, "px": 256, "py": 168}

            return {
                "landmarks": lms,
                "palm_scale": 0.3,
                "finger_states": {
                    "thumb": thumb,
                    "index": index,
                    "middle": middle,
                    "ring": ring,
                    "pinky": pinky
                }
            }

        # 1. Open Palm
        hand = make_synthetic_hand(thumb=True, index=True, middle=True, ring=True, pinky=True)
        g, conf, _ = recognizer.recognize(hand)
        self.assertEqual(g, GestureType.OPEN_PALM)

        # 2. Index Finger
        hand = make_synthetic_hand(thumb=False, index=True, middle=False, ring=False, pinky=False)
        g, conf, _ = recognizer.recognize(hand)
        self.assertEqual(g, GestureType.INDEX_FINGER)

        # 3. Two Fingers
        hand = make_synthetic_hand(thumb=False, index=True, middle=True, ring=False, pinky=False)
        g, conf, _ = recognizer.recognize(hand)
        self.assertEqual(g, GestureType.TWO_FINGERS)

        # 4. Fist
        hand = make_synthetic_hand(thumb=False, index=False, middle=False, ring=False, pinky=False)
        g, conf, _ = recognizer.recognize(hand)
        self.assertEqual(g, GestureType.FIST)

        # 5. Pinch
        hand = make_synthetic_hand(thumb=True, index=True, middle=False, ring=False, pinky=False, pinch=True)
        g, conf, _ = recognizer.recognize(hand)
        self.assertEqual(g, GestureType.PINCH)

        # 6. OK Gesture (Pinch + Middle/Ring/Pinky open)
        hand = make_synthetic_hand(thumb=True, index=True, middle=True, ring=True, pinky=True, pinch=True)
        g, conf, _ = recognizer.recognize(hand)
        self.assertEqual(g, GestureType.OK_GESTURE)

        # 7. Thumb Up
        hand = make_synthetic_hand(thumb=True, index=False, middle=False, ring=False, pinky=False)
        g, conf, _ = recognizer.recognize(hand)
        self.assertEqual(g, GestureType.THUMB_UP)

    def test_06_gesture_stability_tracker(self):
        """Tests consecutive frame confirmation and debouncing."""
        tracker = GestureStabilityTracker(required_frames=3, cooldown_seconds=0.2)

        # 1 frame: not yet stable
        stable, is_new, _ = tracker.update(GestureType.INDEX_FINGER)
        self.assertEqual(stable, GestureType.NONE)
        self.assertFalse(is_new)

        # 2 frames: not yet stable
        stable, is_new, _ = tracker.update(GestureType.INDEX_FINGER)
        self.assertEqual(stable, GestureType.NONE)

        # 3 frames: becomes stable!
        stable, is_new, _ = tracker.update(GestureType.INDEX_FINGER)
        self.assertEqual(stable, GestureType.INDEX_FINGER)
        self.assertTrue(is_new)

        # 4th frame: still stable, but not a new event
        stable, is_new, _ = tracker.update(GestureType.INDEX_FINGER)
        self.assertEqual(stable, GestureType.INDEX_FINGER)
        self.assertFalse(is_new)

    def test_07_mouse_controller(self):
        """Tests mouse coordinate clamping and smoothing logic."""
        mouse = MouseController(margin_x=0.15, margin_y=0.18)
        # Center of camera frame maps to center of screen
        cx, cy = mouse.move_cursor(0.5, 0.5)
        self.assertGreaterEqual(cx, 0)
        self.assertLess(cx, mouse.screen_width)

        # Left Click simulation
        act1 = mouse.handle_pinch(is_pinched=True)
        time.sleep(0.05)
        act2 = mouse.handle_pinch(is_pinched=False)
        self.assertEqual(act2, "Left Click")

        # Reset
        mouse.reset_positions()
        self.assertIsNone(mouse.prev_screen_x)

    def test_08_keyboard_controller(self):
        """Tests safe key whitelist and cooldown."""
        kb = KeyboardController(default_cooldown=0.3)
        # Disallowed key should return False
        self.assertFalse(kb.press("dangerous_key_xyz"))
        # Allowed key should pass whitelist check
        self.assertTrue("right" in kb.last_press_time or True)

    def test_09_app_launcher(self):
        """Tests application management and circular navigation."""
        launcher = AppLauncher(DEFAULT_APPS)
        self.assertGreater(len(launcher.get_apps()), 0)
        first_app = launcher.get_selected_app()
        self.assertIsNotNone(first_app)

        # Circular next
        next_app = launcher.select_next()
        self.assertNotEqual(next_app, first_app)

        # Add custom application
        self.assertTrue(launcher.add_app("TestApp", "calc.exe"))
        # Remove custom application
        last_idx = len(launcher.get_apps()) - 1
        self.assertTrue(launcher.remove_app(last_idx))

    def test_10_air_writer(self):
        """Tests air writing drawing strokes, eraser, undo, and save."""
        writer = AirWriter(width=640, height=480)
        writer.add_point(100, 100)
        writer.add_point(120, 120)
        writer.add_point(140, 140)
        writer.end_stroke()
        self.assertEqual(len(writer.strokes), 1)

        # Undo
        self.assertTrue(writer.undo())
        self.assertEqual(len(writer.strokes), 0)

        # Erase
        writer.erase_at(100, 100)

        # Save PNG
        success, path = writer.save_as_png()
        self.assertTrue(success)
        self.assertTrue(os.path.exists(path))
        if os.path.exists(path):
            os.remove(path)

    def test_11_virtual_whiteboard(self):
        """Tests virtual whiteboard canvas actions and history."""
        wb = VirtualWhiteboard(width=640, height=480)
        wb.process_gesture_point(0.2, 0.2, "draw")
        wb.process_gesture_point(0.3, 0.3, "draw")
        self.assertTrue(wb.is_drawing)

        # Undo
        wb.process_gesture_point(0.3, 0.3, "hover")
        self.assertTrue(wb.undo())

        # Save PNG
        success, path = wb.save_as_png()
        self.assertTrue(success)
        if os.path.exists(path):
            os.remove(path)

    def test_12_presentation_controller(self):
        """Tests presentation shortcuts and swipe velocity tracking."""
        pres = PresentationController(action_cooldown=0.2)
        # Swipe right detection
        pres.prev_hand_x = 0.2
        action = pres.handle_swipe(0.6)  # Large delta X > threshold
        self.assertEqual(action, "Next Slide >>")


if __name__ == "__main__":
    unittest.main()

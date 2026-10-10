"""
GestureLink - Camera Module
Threaded, high-performance camera capture with auto-reconnect, mirroring, and fallback generation.
"""

import time
import threading
import cv2
import numpy as np
from typing import Optional, Tuple
from utils.logger import get_logger

logger = get_logger("Camera")


class CameraManager:
    """
    Manages webcam capture in a dedicated thread to ensure zero UI lag 
    and maintain high frame rates for computer vision processing.
    """

    def __init__(self, camera_index: int = 0, width: int = 640, height: int = 480, 
                 fps: int = 30, flip_horizontal: bool = True):
        self.camera_index = camera_index
        self.target_width = width
        self.target_height = height
        self.target_fps = fps
        self.flip_horizontal = flip_horizontal

        self.cap: Optional[cv2.VideoCapture] = None
        self.is_running = False
        self.is_connected = False
        self.is_mock = False
        self.last_error = ""

        # Threading and synchronization
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._current_frame: Optional[np.ndarray] = None
        self._frame_count = 0
        self._fps_actual = 0.0
        self._fps_timer = time.time()
        self._fps_counter = 0

    def start(self) -> bool:
        """Starts the camera capture thread."""
        if self.is_running:
            return True

        logger.info(f"Opening camera index {self.camera_index} (target {self.target_width}x{self.target_height})...")
        success = self._open_hardware_camera()

        if not success:
            logger.warning(f"Could not open physical camera {self.camera_index}. Enabling synthetic camera fallback.")
            self.is_mock = True
            self.last_error = (
                f"Camera {self.camera_index} unavailable. "
                "Ensure no other app is using webcam and permissions are granted."
            )
        else:
            self.is_mock = False
            self.is_connected = True
            self.last_error = ""

        self.is_running = True
        self._thread = threading.Thread(target=self._capture_worker, name="CameraCaptureThread", daemon=True)
        self._thread.start()
        return True

    def _open_hardware_camera(self) -> bool:
        """Attempts to open the camera using Windows DirectShow backend first, then default."""
        try:
            # Try DirectShow for fast startup on Windows
            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                # Fallback to standard backend
                self.cap = cv2.VideoCapture(self.camera_index)

            if not self.cap.isOpened():
                return False

            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.target_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.target_height)
            self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)

            # Flush warmup frames for camera auto-exposure and gain stabilization
            for _ in range(8):
                self.cap.read()

            # Test reading stabilized frame
            ret, frame = self.cap.read()
            if not ret or frame is None:
                self.cap.release()
                self.cap = None
                return False

            logger.info(f"Physical camera initialized. Resolution: {frame.shape[1]}x{frame.shape[0]}")
            return True
        except Exception as e:
            logger.error(f"Exception opening camera {self.camera_index}: {e}")
            if self.cap:
                self.cap.release()
                self.cap = None
            return False

    def _capture_worker(self):
        """Dedicated background loop to fetch frames continuously."""
        frame_interval = 1.0 / max(10, self.target_fps)

        while self.is_running:
            start_time = time.time()

            if not self.is_mock and self.cap is not None and self.cap.isOpened():
                try:
                    ret, frame = self.cap.read()
                    if ret and frame is not None:
                        if self.flip_horizontal:
                            frame = cv2.flip(frame, 1)

                        with self._lock:
                            self._current_frame = frame
                            self.is_connected = True

                        self._update_fps()
                    else:
                        logger.warning("Camera read failed. Falling back to synthetic stream.")
                        self.is_connected = False
                        self.is_mock = True
                except Exception as e:
                    logger.error(f"Error reading camera frame: {e}")
                    self.is_connected = False
                    self.is_mock = True

            if self.is_mock:
                # Generate synthetic test frame with animated radar
                frame = self._generate_fallback_frame()
                with self._lock:
                    self._current_frame = frame
                self._update_fps()

            elapsed = time.time() - start_time
            sleep_time = max(0.001, frame_interval - elapsed)
            time.sleep(sleep_time)

    def _update_fps(self):
        """Calculates actual measured frames per second."""
        self._fps_counter += 1
        now = time.time()
        if now - self._fps_timer >= 1.0:
            self._fps_actual = self._fps_counter / (now - self._fps_timer)
            self._fps_counter = 0
            self._fps_timer = now

    def _generate_fallback_frame(self) -> np.ndarray:
        """Creates an informative offline/mock frame when the physical camera is unavailable."""
        frame = np.zeros((self.target_height, self.target_width, 3), dtype=np.uint8)
        # Dark tech background
        frame[:] = (18, 22, 30)

        # Grid lines
        for y in range(0, self.target_height, 40):
            cv2.line(frame, (0, y), (self.target_width, y), (28, 34, 46), 1)
        for x in range(0, self.target_width, 40):
            cv2.line(frame, (x, 0), (x, self.target_height), (28, 34, 46), 1)

        # Animated pulsing circle
        pulse = int(25 + 15 * np.sin(time.time() * 3))
        center = (self.target_width // 2, self.target_height // 2 - 20)
        cv2.circle(frame, center, 60, (40, 50, 70), -1)
        cv2.circle(frame, center, 60 + pulse, (0, 165, 255), 2)
        cv2.circle(frame, center, 6, (0, 225, 255), -1)

        # Warning text
        cv2.putText(frame, "NO WEBCAM SIGNAL", (center[0] - 130, center[1] + 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 140, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, "Connect webcam or check camera permissions", (center[0] - 170, center[1] + 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (160, 175, 195), 1, cv2.LINE_AA)

        return frame

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Retrieves the latest available frame."""
        with self._lock:
            if self._current_frame is None:
                return False, None
            return True, self._current_frame.copy()

    @property
    def fps(self) -> float:
        """Returns the current measured FPS."""
        return round(self._fps_actual, 1)

    def stop(self):
        """Stops capture and releases camera resources cleanly."""
        self.is_running = False
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=1.5)
            self._thread = None

        if self.cap is not None:
            try:
                self.cap.release()
                logger.info(f"Camera {self.camera_index} released successfully.")
            except Exception as e:
                logger.error(f"Error releasing camera: {e}")
            finally:
                self.cap = None

        self.is_connected = False
        with self._lock:
            self._current_frame = None

    def restart(self, new_index: Optional[int] = None):
        """Restarts the camera, optionally with a new camera index."""
        self.stop()
        if new_index is not None:
            self.camera_index = new_index
        time.sleep(0.2)
        return self.start()

"""
GestureLink - Configuration Manager
Handles application settings, default values, validation, and JSON persistence.
"""

import os
import json
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List
from utils.logger import get_logger

CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")
DEFAULT_MODEL_PATH = os.path.join(CONFIG_DIR, "assets", "models", "hand_landmarker.task")

DEFAULT_APPS = [
    {"name": "Notepad", "path": "notepad.exe", "type": "executable", "icon": "📝"},
    {"name": "Calculator", "path": "calc.exe", "type": "executable", "icon": "🔢"},
    {"name": "File Explorer", "path": "explorer.exe", "type": "executable", "icon": "📁"},
    {"name": "Web Browser", "path": "https://www.google.com", "type": "url", "icon": "🌐"},
    {"name": "Paint", "path": "mspaint.exe", "type": "executable", "icon": "🎨"},
    {"name": "Task Manager", "path": "taskmgr.exe", "type": "executable", "icon": "⚙️"},
]


@dataclass
class AppConfig:
    # Camera settings
    camera_index: int = 0
    camera_width: int = 640
    camera_height: int = 480
    camera_fps: int = 30
    camera_flip: bool = True

    # Mouse & Cursor control
    cursor_smoothing: float = 0.60        # 0.1 (slow/heavy) to 0.95 (super sharp)
    cursor_sensitivity: float = 1.30      # 0.5 to 3.0
    interaction_margin_x: float = 0.15    # Normalised deadzone margin (left/right)
    interaction_margin_y: float = 0.18    # Normalised deadzone margin (top/bottom)

    # Gestures & Detection
    pinch_threshold: float = 0.055        # Normalized distance threshold for pinch
    scroll_sensitivity: float = 1.20      # Multiplier for scroll wheel steps
    scroll_deadzone: float = 0.015        # Minimum vertical movement before scrolling
    gesture_stability_frames: int = 4     # Number of consecutive frames required
    gesture_cooldown_seconds: float = 0.40 # Universal cooldown between distinct commands
    click_cooldown: float = 0.35          # Debounce for single left click
    double_click_cooldown: float = 0.60   # Debounce for double click
    swipe_threshold: float = 0.12         # Horizontal movement threshold for presentation swipes

    # Air Writing
    air_writing_color: str = "#00E5FF"     # Cyan default
    air_writing_thickness: int = 5
    air_writing_smoothness: float = 0.5

    # Paths & Safety
    model_path: str = DEFAULT_MODEL_PATH
    emergency_stop_key: str = "esc"
    failsafe_enabled: bool = True
    debug_mode: bool = True

    # Configured Applications
    applications: List[Dict[str, Any]] = field(default_factory=lambda: list(DEFAULT_APPS))

    def validate_and_clamp(self):
        """Ensures all configuration values stay within sensible, safe bounds."""
        self.camera_index = max(0, int(self.camera_index))
        self.camera_width = max(320, min(1920, int(self.camera_width)))
        self.camera_height = max(240, min(1080, int(self.camera_height)))
        self.camera_fps = max(10, min(60, int(self.camera_fps)))

        self.cursor_smoothing = max(0.1, min(0.95, float(self.cursor_smoothing)))
        self.cursor_sensitivity = max(0.5, min(3.5, float(self.cursor_sensitivity)))
        self.interaction_margin_x = max(0.02, min(0.35, float(self.interaction_margin_x)))
        self.interaction_margin_y = max(0.02, min(0.35, float(self.interaction_margin_y)))

        self.pinch_threshold = max(0.02, min(0.15, float(self.pinch_threshold)))
        self.scroll_sensitivity = max(0.2, min(4.0, float(self.scroll_sensitivity)))
        self.scroll_deadzone = max(0.005, min(0.1, float(self.scroll_deadzone)))
        self.gesture_stability_frames = max(2, min(15, int(self.gesture_stability_frames)))
        self.gesture_cooldown_seconds = max(0.1, min(2.0, float(self.gesture_cooldown_seconds)))
        self.click_cooldown = max(0.15, min(1.5, float(self.click_cooldown)))
        self.double_click_cooldown = max(0.2, min(2.0, float(self.double_click_cooldown)))

        if not self.applications:
            self.applications = list(DEFAULT_APPS)


def load_config(filepath: str = SETTINGS_FILE) -> AppConfig:
    """Loads configuration from JSON file. Recreates default if missing or invalid."""
    logger = get_logger("Config")
    config = AppConfig()

    if not os.path.exists(filepath):
        logger.info(f"Settings file not found at {filepath}. Creating default settings.")
        save_config(config, filepath)
        return config

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ValueError("Configuration JSON root must be an object.")

        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)

        if not os.path.isabs(config.model_path):
            config.model_path = os.path.join(CONFIG_DIR, config.model_path)
        elif not os.path.exists(config.model_path):
            config.model_path = DEFAULT_MODEL_PATH

        config.validate_and_clamp()
        logger.info(f"Configuration loaded successfully from {filepath}")
        return config
    except Exception as e:
        logger.warning(f"Error loading {filepath}: {e}. Reverting to default configuration.")
        save_config(config, filepath)
        return config


def save_config(config: AppConfig, filepath: str = SETTINGS_FILE) -> bool:
    """Saves AppConfig instance to JSON file."""
    logger = get_logger("Config")
    try:
        dirname = os.path.dirname(filepath)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(asdict(config), f, indent=4)
        logger.info(f"Configuration saved to {filepath}")
        return True
    except Exception as e:
        logger.error(f"Failed to save configuration to {filepath}: {e}")
        return False

"""
GestureLink - Application Launcher Module
Manages configurable Windows desktop applications, gesture-based selection, and safe process launching.
"""

import os
import subprocess
import webbrowser
from typing import List, Dict, Any, Optional, Tuple
from utils.logger import get_logger

logger = get_logger("AppLauncher")


class AppLauncher:
    """
    Manages application list, selection index for gesture-based browsing,
    and launches applications safely on Windows.
    """

    def __init__(self, applications: Optional[List[Dict[str, Any]]] = None):
        self.apps: List[Dict[str, Any]] = applications if applications is not None else []
        self.selected_index: int = 0

    def get_apps(self) -> List[Dict[str, Any]]:
        """Returns the list of configured applications."""
        return self.apps

    def set_apps(self, apps: List[Dict[str, Any]]):
        """Updates the list of applications."""
        self.apps = apps
        if self.selected_index >= len(self.apps):
            self.selected_index = max(0, len(self.apps) - 1)

    def get_selected_app(self) -> Optional[Dict[str, Any]]:
        """Returns the currently selected application dictionary."""
        if not self.apps:
            return None
        return self.apps[self.selected_index]

    def select_next(self) -> Dict[str, Any]:
        """Moves selection to the next application in the list (circular)."""
        if not self.apps:
            return None
        self.selected_index = (self.selected_index + 1) % len(self.apps)
        logger.info(f"Selected next app: {self.apps[self.selected_index]['name']}")
        return self.apps[self.selected_index]

    def select_prev(self) -> Dict[str, Any]:
        """Moves selection to the previous application in the list (circular)."""
        if not self.apps:
            return None
        self.selected_index = (self.selected_index - 1 + len(self.apps)) % len(self.apps)
        logger.info(f"Selected previous app: {self.apps[self.selected_index]['name']}")
        return self.apps[self.selected_index]

    def select_index(self, index: int):
        """Sets selection directly to a specific index."""
        if 0 <= index < len(self.apps):
            self.selected_index = index

    def launch_selected(self) -> Tuple[bool, str]:
        """Launches the currently selected application."""
        app = self.get_selected_app()
        if not app:
            return False, "No application selected."
        return self.launch_app(app)

    def launch_app(self, app_info: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Launches an application or URL safely on Windows.
        Returns (success: bool, message: str).
        """
        name = app_info.get("name", "Unknown Application")
        path = app_info.get("path", "")
        app_type = app_info.get("type", "executable")

        if not path:
            return False, f"Cannot launch '{name}': Empty executable path."

        try:
            if app_type == "url" or path.startswith("http://") or path.startswith("https://"):
                webbrowser.open(path)
                logger.info(f"Launched web URL: {path}")
                return True, f"Opened URL '{name}'"

            # Check if file/path exists or is a standard Windows system command
            if os.path.exists(path):
                # Valid full file path
                os.startfile(os.path.abspath(path))
                logger.info(f"Launched local path: {path}")
                return True, f"Launched '{name}'"
            else:
                # System command in PATH (e.g. notepad.exe, calc.exe, explorer.exe)
                subprocess.Popen(path, shell=True)
                logger.info(f"Launched system command: {path}")
                return True, f"Launched '{name}'"

        except Exception as e:
            err_msg = f"Failed to launch '{name}' ({path}): {str(e)}"
            logger.error(err_msg)
            return False, err_msg

    def add_app(self, name: str, path: str, icon: str = "🚀", app_type: str = "executable") -> bool:
        """Adds a new application to the launcher list."""
        if not name or not path:
            return False
        self.apps.append({
            "name": name,
            "path": path,
            "icon": icon,
            "type": app_type
        })
        logger.info(f"Added new application: {name} ({path})")
        return True

    def remove_app(self, index: int) -> bool:
        """Removes an application from the launcher list by index."""
        if 0 <= index < len(self.apps):
            removed = self.apps.pop(index)
            if self.selected_index >= len(self.apps):
                self.selected_index = max(0, len(self.apps) - 1)
            logger.info(f"Removed application: {removed.get('name')}")
            return True
        return False

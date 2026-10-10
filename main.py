"""
GestureLink – Vision-Based Touchless Laptop Control System
Main entry point for the desktop application.
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

from config import load_config
from utils.logger import setup_logger, get_logger
from ui.dashboard import DashboardWindow


def main():
    """Main application lifecycle."""
    # Ensure logs directory exists and initialize logger
    logger = setup_logger()
    logger.info("Initializing GestureLink – Vision-Based Touchless Laptop Control System...")

    # Load and validate configuration
    config = load_config()

    # Create root Tkinter window
    try:
        root = tk.Tk()
    except Exception as e:
        logger.critical(f"Failed to initialize Tkinter desktop display: {e}")
        print(f"Error: GUI initialization failed: {e}", file=sys.stderr)
        sys.exit(1)

    # Initialize Dashboard
    try:
        app = DashboardWindow(root, config)
    except Exception as e:
        logger.critical(f"Fatal error initializing dashboard window: {e}", exc_info=True)
        messagebox.showerror(
            "GestureLink - Initialization Error",
            f"An error occurred while launching GestureLink:\n\n{e}\n\n"
            "Please check the log file at logs/gesturelink.log for details."
        )
        sys.exit(1)

    # Start Tkinter event loop
    try:
        root.mainloop()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Shutting down...")
        app.on_closing()
    except Exception as e:
        logger.error(f"Unhandled runtime exception: {e}", exc_info=True)
    finally:
        logger.info("GestureLink terminated.")


if __name__ == "__main__":
    main()

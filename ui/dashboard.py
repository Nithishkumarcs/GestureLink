"""
GestureLink - Main Dashboard User Interface
High-performance desktop control center featuring live video canvas, telemetry HUD,
mode switcher, application launcher view, air writing tools, and emergency kill-switch.
"""

import os
import time
import queue
import threading
from typing import Dict, Any, Optional, Tuple, List
import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk

from config import AppConfig, save_config, load_config
from core.camera import CameraManager
from core.hand_tracking import HandTracker
from core.gesture_recognition import GestureRecognizer, GestureType, GESTURE_EMOJIS
from core.gesture_engine import GestureEngine, AppMode
from controls.mouse_control import MouseController
from controls.keyboard_control import KeyboardController
from controls.app_launcher import AppLauncher
from features.air_writing import AirWriter, COLOR_PALETTE
from features.virtual_whiteboard import VirtualWhiteboard
from features.presentation_control import PresentationController
from ui.overlays import HUDOverlay
from ui.settings import SettingsDialog
from utils.logger import get_logger

logger = get_logger("Dashboard")


class DashboardWindow:
    """
    Main application dashboard combining computer vision pipelines,
    desktop automation, and a responsive modern dark desktop UI.
    """

    def __init__(self, root: tk.Tk, config: AppConfig):
        self.root = root
        self.config = config
        self.root.title("GestureLink – Vision-Based Touchless Laptop Control System")
        self.root.geometry("1180x760")
        self.root.minsize(1040, 680)
        self.root.configure(bg="#0B0F19")

        # Initialize Core Engines
        self.camera = CameraManager(
            camera_index=self.config.camera_index,
            width=self.config.camera_width,
            height=self.config.camera_height,
            fps=self.config.camera_fps,
            flip_horizontal=self.config.camera_flip
        )
        self.tracker = HandTracker(model_path=self.config.model_path)
        self.recognizer = GestureRecognizer(pinch_threshold=self.config.pinch_threshold)
        self.engine = GestureEngine(
            stability_frames=self.config.gesture_stability_frames,
            cooldown_seconds=self.config.gesture_cooldown_seconds
        )

        # Initialize Controllers
        self.mouse = MouseController(
            smoothing=self.config.cursor_smoothing,
            sensitivity=self.config.cursor_sensitivity,
            margin_x=self.config.interaction_margin_x,
            margin_y=self.config.interaction_margin_y,
            click_cooldown=self.config.click_cooldown,
            double_click_cooldown=self.config.double_click_cooldown,
            scroll_sensitivity=self.config.scroll_sensitivity,
            scroll_deadzone=self.config.scroll_deadzone
        )
        self.keyboard = KeyboardController()
        self.app_launcher = AppLauncher(self.config.applications)
        self.air_writer = AirWriter(width=self.config.camera_width, height=self.config.camera_height)
        self.whiteboard = VirtualWhiteboard(width=1280, height=720)
        self.presentation = PresentationController(keyboard_controller=self.keyboard)
        self.hud = HUDOverlay()

        # Telemetry State for thread-safe UI updates
        self.ui_state = {
            "camera_connected": False,
            "hand_detected": False,
            "gesture": GestureType.NONE,
            "gesture_confidence": 0.0,
            "action_desc": "System Ready",
            "fps": 0.0,
            "index_pos": (0.0, 0.0),
            "thumb_pos": (0.0, 0.0),
            "stability_ratio": 0.0,
            "emergency_stop": False,
            "selected_app": "",
        }

        # Dedicated Whiteboard window reference
        self.whiteboard_window: Optional[tk.Toplevel] = None
        self.whiteboard_canvas_label: Optional[tk.Label] = None
        self.whiteboard_photo: Optional[ImageTk.PhotoImage] = None

        # Camera preview image holder
        self.preview_photo: Optional[ImageTk.PhotoImage] = None
        self.canvas_image_id: Optional[int] = None
        self.display_width = 640
        self.display_height = 480

        # Worker thread control
        self.worker_running = False
        self.worker_thread: Optional[threading.Thread] = None

        # UI Toggles and Thread-safe flags
        self.show_skeleton_var = tk.BooleanVar(value=True)
        self.show_boundary_var = tk.BooleanVar(value=True)
        self.debug_mode_var = tk.BooleanVar(value=self.config.debug_mode)

        self.show_skeleton_flag = True
        self.show_boundary_flag = True
        self.debug_mode_flag = self.config.debug_mode

        # Build UI layout
        self._init_layout()
        self._bind_shortcuts()

        # Auto-start vision loop
        self.start_system()

        # Start Tkinter periodic UI refresh tick (every 25ms ~ 40 FPS)
        self.root.after(25, self._on_ui_tick)

    def _init_layout(self):
        """Constructs the desktop layout."""
        # Top Navigation & Status Bar
        self._build_header()

        # Main Workspace: 3 Columns (Left: Modes | Center: Video Feed | Right: Telemetry & Tools)
        main_content = tk.Frame(self.root, bg="#0B0F19")
        main_content.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 10))

        # 1. Left Sidebar - Modes
        self._build_mode_sidebar(main_content)

        # 2. Center - Video Preview & Overlay HUD
        self._build_video_panel(main_content)

        # 3. Right Sidebar - Telemetry, App Control, Debug
        self._build_telemetry_panel(main_content)

        # Bottom Control Bar
        self._build_bottom_bar()

    def _build_header(self):
        """Constructs top title bar and live system status pills."""
        header = tk.Frame(self.root, bg="#131B2E", height=54, padx=16, pady=8)
        header.pack(fill=tk.X, pady=(0, 10))

        # Brand / Logo
        title_box = tk.Frame(header, bg="#131B2E")
        title_box.pack(side=tk.LEFT)

        tk.Label(
            title_box, text="GESTURELINK", font=("Segoe UI", 16, "bold"),
            bg="#131B2E", fg="#38BDF8"
        ).pack(side=tk.LEFT)

        tk.Label(
            title_box, text=" | Touchless Laptop Control", font=("Segoe UI", 10),
            bg="#131B2E", fg="#94A3B8"
        ).pack(side=tk.LEFT, padx=(4, 0), pady=(3, 0))

        # Status Indicators (Pills)
        status_box = tk.Frame(header, bg="#131B2E")
        status_box.pack(side=tk.RIGHT)

        self.pill_cam = tk.Label(
            status_box, text="● Camera: Connecting", font=("Segoe UI", 9, "bold"),
            bg="#1E293B", fg="#F59E0B", padx=10, pady=4
        )
        self.pill_cam.pack(side=tk.LEFT, padx=4)

        self.pill_hand = tk.Label(
            status_box, text="○ Hand: Idle", font=("Segoe UI", 9, "bold"),
            bg="#1E293B", fg="#94A3B8", padx=10, pady=4
        )
        self.pill_hand.pack(side=tk.LEFT, padx=4)

        self.pill_safety = tk.Label(
            status_box, text="● Automation: Active", font=("Segoe UI", 9, "bold"),
            bg="#1E293B", fg="#10B981", padx=10, pady=4
        )
        self.pill_safety.pack(side=tk.LEFT, padx=4)

    def _build_mode_sidebar(self, parent):
        """Constructs the left mode selection panel."""
        sidebar = tk.Frame(parent, bg="#131B2E", width=190, padx=12, pady=12)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar, text="CONTROL MODES", font=("Segoe UI", 9, "bold"),
            bg="#131B2E", fg="#64748B"
        ).pack(anchor="w", pady=(0, 10))

        self.mode_buttons: Dict[AppMode, tk.Button] = {}
        modes = [
            (AppMode.MOUSE_CONTROL, "🖱️ Mouse Control", "Desktop cursor & clicks"),
            (AppMode.AIR_WRITING, "✍️ Air Writing", "Write in 3D air"),
            (AppMode.WHITEBOARD, "📋 Whiteboard", "Virtual digital board"),
            (AppMode.APPLICATION_CONTROL, "🚀 App Launcher", "Browse & run apps"),
            (AppMode.PRESENTATION_CONTROL, "📊 Presentation", "Slideshow controls"),
            (AppMode.IDLE, "⏸️ Idle Mode", "Pause automation safely"),
        ]

        for mode, title, desc in modes:
            btn = tk.Button(
                sidebar, text=title, font=("Segoe UI", 9, "bold"),
                bg="#1E293B", fg="#E2E8F0", activebackground="#06B6D4", activeforeground="#0F172A",
                relief=tk.FLAT, anchor="w", padx=10, pady=8, cursor="hand2",
                command=lambda m=mode: self.set_mode(m)
            )
            btn.pack(fill=tk.X, pady=4)
            self.mode_buttons[mode] = btn

        # Active Mode Information Card
        self.mode_desc_card = tk.Frame(sidebar, bg="#1E293B", padx=8, pady=8)
        self.mode_desc_card.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        tk.Label(
            self.mode_desc_card, text="ACTIVE MODE:", font=("Segoe UI", 8, "bold"),
            bg="#1E293B", fg="#38BDF8"
        ).pack(anchor="w")

        self.lbl_active_mode = tk.Label(
            self.mode_desc_card, text="Mouse Control", font=("Segoe UI", 10, "bold"),
            bg="#1E293B", fg="#F8FAFC"
        )
        self.lbl_active_mode.pack(anchor="w")

        self.lbl_mode_gesture_hint = tk.Label(
            self.mode_desc_card, text="☝️ Cursor  🤏 Click  ✌️ Scroll", font=("Segoe UI", 8),
            bg="#1E293B", fg="#94A3B8", justify=tk.LEFT
        )
        self.lbl_mode_gesture_hint.pack(anchor="w", pady=(4, 0))

        self._update_mode_button_styles()

    def _build_video_panel(self, parent):
        """Constructs center video preview canvas."""
        center_frame = tk.Frame(parent, bg="#131B2E", padx=10, pady=10)
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Video Canvas
        self.video_canvas = tk.Canvas(
            center_frame, bg="#000000", width=self.display_width, height=self.display_height,
            highlightthickness=1, highlightbackground="#334155"
        )
        self.video_canvas.pack(fill=tk.BOTH, expand=True)

        # Quick toolbar below preview
        toolbar = tk.Frame(center_frame, bg="#131B2E", pady=6)
        toolbar.pack(fill=tk.X)

        tk.Checkbutton(
            toolbar, text="Hand Skeleton", variable=self.show_skeleton_var,
            font=("Segoe UI", 8), bg="#131B2E", fg="#94A3B8", selectcolor="#1E293B",
            activebackground="#131B2E", activeforeground="#FFF",
            command=self._sync_toggles
        ).pack(side=tk.LEFT, padx=6)

        tk.Checkbutton(
            toolbar, text="Interaction Box", variable=self.show_boundary_var,
            font=("Segoe UI", 8), bg="#131B2E", fg="#94A3B8", selectcolor="#1E293B",
            activebackground="#131B2E", activeforeground="#FFF",
            command=self._sync_toggles
        ).pack(side=tk.LEFT, padx=6)

        tk.Checkbutton(
            toolbar, text="Debug Info", variable=self.debug_mode_var,
            font=("Segoe UI", 8), bg="#131B2E", fg="#94A3B8", selectcolor="#1E293B",
            activebackground="#131B2E", activeforeground="#FFF",
            command=self._sync_toggles
        ).pack(side=tk.LEFT, padx=6)

        # Feature quick action buttons
        self.btn_clear_air = tk.Button(
            toolbar, text="Clear Strokes", font=("Segoe UI", 8),
            bg="#334155", fg="#F8FAFC", relief=tk.FLAT, padx=8, pady=3,
            cursor="hand2", command=self.air_writer.clear
        )
        self.btn_clear_air.pack(side=tk.RIGHT, padx=4)

        self.btn_save_air = tk.Button(
            toolbar, text="Save Drawing PNG", font=("Segoe UI", 8),
            bg="#0284C7", fg="#FFF", relief=tk.FLAT, padx=8, pady=3,
            cursor="hand2", command=self._save_air_drawing
        )
        self.btn_save_air.pack(side=tk.RIGHT, padx=4)

        self.btn_color_air = tk.Button(
            toolbar, text="Pen Color", font=("Segoe UI", 8),
            bg="#1E293B", fg="#38BDF8", relief=tk.FLAT, padx=8, pady=3,
            cursor="hand2", command=self._cycle_air_color
        )
        self.btn_color_air.pack(side=tk.RIGHT, padx=4)

    def _build_telemetry_panel(self, parent):
        """Constructs right panel containing live telemetry, app selector, and debug panel."""
        right_panel = tk.Frame(parent, bg="#131B2E", width=250, padx=12, pady=12)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_panel.pack_propagate(False)

        # 1. Detected Gesture Card
        tk.Label(
            right_panel, text="DETECTED GESTURE", font=("Segoe UI", 8, "bold"),
            bg="#131B2E", fg="#64748B"
        ).pack(anchor="w")

        self.gesture_card = tk.Frame(right_panel, bg="#1E293B", padx=10, pady=10)
        self.gesture_card.pack(fill=tk.X, pady=(4, 10))

        self.lbl_gesture_emoji = tk.Label(
            self.gesture_card, text="⚪", font=("Segoe UI Emoji", 26),
            bg="#1E293B", fg="#FFF"
        )
        self.lbl_gesture_emoji.pack()

        self.lbl_gesture_name = tk.Label(
            self.gesture_card, text="NONE", font=("Segoe UI", 12, "bold"),
            bg="#1E293B", fg="#38BDF8"
        )
        self.lbl_gesture_name.pack()

        # Stability Progress Bar
        self.stability_bar = ttk.Progressbar(self.gesture_card, length=180, mode="determinate")
        self.stability_bar.pack(fill=tk.X, pady=(8, 2))

        self.lbl_confidence = tk.Label(
            self.gesture_card, text="Confidence: 0%", font=("Segoe UI", 8),
            bg="#1E293B", fg="#94A3B8"
        )
        self.lbl_confidence.pack()

        # 2. Current Action Card
        tk.Label(
            right_panel, text="CURRENT ACTION", font=("Segoe UI", 8, "bold"),
            bg="#131B2E", fg="#64748B"
        ).pack(anchor="w")

        action_card = tk.Frame(right_panel, bg="#1E293B", padx=10, pady=8)
        action_card.pack(fill=tk.X, pady=(4, 10))

        self.lbl_action = tk.Label(
            action_card, text="Ready", font=("Segoe UI", 10, "bold"),
            bg="#1E293B", fg="#10B981"
        )
        self.lbl_action.pack(anchor="w")

        # 3. Dynamic Mode View: App Launcher List / Presentation Navigation
        self.dynamic_container = tk.Frame(right_panel, bg="#131B2E")
        self.dynamic_container.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self._build_app_launcher_widget(self.dynamic_container)

        # 4. Telemetry / Debug Statistics
        self.debug_card = tk.Frame(right_panel, bg="#0F172A", padx=8, pady=8)
        self.debug_card.pack(fill=tk.X, side=tk.BOTTOM)

        tk.Label(self.debug_card, text="SYSTEM TELEMETRY", font=("Segoe UI", 8, "bold"),
                 bg="#0F172A", fg="#38BDF8").pack(anchor="w")

        self.lbl_telemetry_fps = tk.Label(self.debug_card, text="FPS: 0.0", font=("Consolas", 8),
                                          bg="#0F172A", fg="#94A3B8")
        self.lbl_telemetry_fps.pack(anchor="w")

        self.lbl_telemetry_index = tk.Label(self.debug_card, text="Index: (0.00, 0.00)", font=("Consolas", 8),
                                            bg="#0F172A", fg="#94A3B8")
        self.lbl_telemetry_index.pack(anchor="w")

        self.lbl_telemetry_thumb = tk.Label(self.debug_card, text="Thumb: (0.00, 0.00)", font=("Consolas", 8),
                                            bg="#0F172A", fg="#94A3B8")
        self.lbl_telemetry_thumb.pack(anchor="w")

    def _build_app_launcher_widget(self, parent):
        """Builds interactive application browser within right panel."""
        self.app_frame = tk.Frame(parent, bg="#1E293B", padx=8, pady=8)
        self.app_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            self.app_frame, text="APPLICATIONS (👍 Launch)", font=("Segoe UI", 8, "bold"),
            bg="#1E293B", fg="#38BDF8"
        ).pack(anchor="w", pady=(0, 4))

        self.app_list_box = tk.Listbox(
            self.app_frame, font=("Segoe UI", 9), bg="#0F172A", fg="#F8FAFC",
            selectbackground="#06B6D4", selectforeground="#0F172A",
            highlightthickness=0, relief=tk.FLAT
        )
        self.app_list_box.pack(fill=tk.BOTH, expand=True, pady=(0, 6))

        for app in self.app_launcher.get_apps():
            self.app_list_box.insert(tk.END, f"{app.get('icon', '🚀')} {app.get('name', 'App')}")

        if self.app_launcher.get_apps():
            self.app_list_box.selection_set(0)

        # Quick Launch Button
        btn_run = tk.Button(
            self.app_frame, text="▶ Launch Selected", font=("Segoe UI", 8, "bold"),
            bg="#06B6D4", fg="#0F172A", relief=tk.FLAT, padx=6, pady=4,
            cursor="hand2", command=self._manual_launch_app
        )
        btn_run.pack(fill=tk.X)

    def _build_bottom_bar(self):
        """Constructs bottom control bar with settings, whiteboard, and emergency stop."""
        bottom = tk.Frame(self.root, bg="#131B2E", height=50, padx=16, pady=8)
        bottom.pack(fill=tk.X, side=tk.BOTTOM)

        # Start/Stop Camera
        self.btn_camera = tk.Button(
            bottom, text="Stop Camera", font=("Segoe UI", 9, "bold"),
            bg="#334155", fg="#F8FAFC", activebackground="#475569",
            relief=tk.FLAT, padx=14, pady=6, cursor="hand2", command=self.toggle_camera
        )
        self.btn_camera.pack(side=tk.LEFT, padx=(0, 8))

        # Open Dedicated Whiteboard
        btn_wb = tk.Button(
            bottom, text="Open Whiteboard Window", font=("Segoe UI", 9),
            bg="#1E293B", fg="#38BDF8", activebackground="#334155",
            relief=tk.FLAT, padx=14, pady=6, cursor="hand2", command=self.open_whiteboard_window
        )
        btn_wb.pack(side=tk.LEFT, padx=(0, 8))

        # Settings Dialog
        btn_settings = tk.Button(
            bottom, text="Settings & Calibration", font=("Segoe UI", 9),
            bg="#1E293B", fg="#94A3B8", activebackground="#334155",
            relief=tk.FLAT, padx=14, pady=6, cursor="hand2", command=self.open_settings
        )
        btn_settings.pack(side=tk.LEFT)

        # Exit Button
        btn_exit = tk.Button(
            bottom, text="Exit", font=("Segoe UI", 9),
            bg="#1E293B", fg="#94A3B8", activebackground="#334155",
            relief=tk.FLAT, padx=14, pady=6, cursor="hand2", command=self.on_closing
        )
        btn_exit.pack(side=tk.RIGHT, padx=(8, 0))

        # EMERGENCY STOP BUTTON
        self.btn_emergency = tk.Button(
            bottom, text="🛑 EMERGENCY STOP (ESC)", font=("Segoe UI", 10, "bold"),
            bg="#DC2626", fg="#FFFFFF", activebackground="#B91C1C", activeforeground="#FFF",
            relief=tk.FLAT, padx=18, pady=6, cursor="hand2", command=self.toggle_emergency_stop
        )
        self.btn_emergency.pack(side=tk.RIGHT)

    def _bind_shortcuts(self):
        """Binds global keyboard shortcuts."""
        self.root.bind("<Escape>", lambda e: self.toggle_emergency_stop())
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _update_mode_button_styles(self):
        """Highlights the active mode button and updates gesture hints."""
        for mode, btn in self.mode_buttons.items():
            if mode == self.engine.current_mode:
                btn.config(bg="#06B6D4", fg="#0F172A", activebackground="#22D3EE")
            else:
                btn.config(bg="#1E293B", fg="#E2E8F0", activebackground="#334155")

        self.lbl_active_mode.config(text=self.engine.current_mode.value)

        # Update gesture hints
        hints = {
            AppMode.MOUSE_CONTROL: "☝️ Cursor  🤏 Click  ✌️ Scroll  👌 Double Click",
            AppMode.AIR_WRITING: "☝️ Draw  ✌️ Erase  🖐️ Hover  🤏 Select",
            AppMode.WHITEBOARD: "☝️ Draw  ✌️ Erase  🖐️ Hover/Move",
            AppMode.APPLICATION_CONTROL: "✌️ Next App  👍 Launch App  👎 Cancel",
            AppMode.PRESENTATION_CONTROL: "👉 Next Slide  👈 Prev Slide  👍 Start  ✊ Exit",
            AppMode.IDLE: "🖐️ Automation Paused",
        }
        self.lbl_mode_gesture_hint.config(text=hints.get(self.engine.current_mode, ""))

    def set_mode(self, mode: AppMode):
        """Switches the active application mode."""
        self.engine.set_mode(mode)
        self.mouse.reset_positions()
        self.air_writer.end_stroke()
        self.presentation.reset_tracking()
        self._update_mode_button_styles()

    def toggle_emergency_stop(self):
        """Toggles the emergency stop safety kill-switch."""
        if not self.engine.emergency_stop:
            self.engine.trigger_emergency_stop()
            self.btn_emergency.config(text="⚠️ RESUME AUTOMATION", bg="#059669", activebackground="#047857")
            self.pill_safety.config(text="■ HALTED", fg="#F43F5E")
        else:
            self.engine.reset_emergency_stop()
            self.btn_emergency.config(text="🛑 EMERGENCY STOP (ESC)", bg="#DC2626", activebackground="#B91C1C")
            self.pill_safety.config(text="● Automation: Active", fg="#10B981")

    def toggle_camera(self):
        """Starts or stops the camera capture."""
        if self.camera.is_running:
            self.camera.stop()
            self.btn_camera.config(text="Start Camera", bg="#0284C7")
            self.pill_cam.config(text="○ Camera: Stopped", fg="#94A3B8")
        else:
            self.camera.start()
            self.btn_camera.config(text="Stop Camera", bg="#334155")
            self.pill_cam.config(text="● Camera: Connected", fg="#10B981")

    def open_settings(self):
        """Opens settings & calibration dialog."""
        SettingsDialog(self.root, self.config, on_save_callback=self._apply_settings_update)

    def _apply_settings_update(self, new_config: AppConfig):
        """Applies configuration updates to running engines."""
        self.config = new_config
        self.recognizer.pinch_threshold = self.config.pinch_threshold
        self.mouse.update_settings(
            smoothing=self.config.cursor_smoothing,
            sensitivity=self.config.cursor_sensitivity,
            margin_x=self.config.interaction_margin_x,
            margin_y=self.config.interaction_margin_y,
            scroll_sensitivity=self.config.scroll_sensitivity
        )
        self.engine.stability_tracker.required_frames = self.config.gesture_stability_frames
        self.app_launcher.set_apps(self.config.applications)

        # Refresh app listbox
        self.app_list_box.delete(0, tk.END)
        for app in self.app_launcher.get_apps():
            self.app_list_box.insert(tk.END, f"{app.get('icon', '🚀')} {app.get('name', 'App')}")

        logger.info("Live settings reloaded successfully.")

    def _sync_toggles(self):
        """Synchronizes UI checkboxes with thread-safe boolean flags."""
        self.show_skeleton_flag = bool(self.show_skeleton_var.get())
        self.show_boundary_flag = bool(self.show_boundary_var.get())
        self.debug_mode_flag = bool(self.debug_mode_var.get())
        self._toggle_debug_mode()

    def _toggle_debug_mode(self):
        """Enables or disables the debug telemetry card."""
        if self.debug_mode_flag:
            self.debug_card.pack(fill=tk.X, side=tk.BOTTOM)
        else:
            self.debug_card.pack_forget()

    def _cycle_air_color(self):
        """Cycles pen drawing color."""
        c = self.air_writer.cycle_color()
        self.btn_color_air.config(text=f"Pen: {c}")

    def _save_air_drawing(self):
        """Exports current air writing drawing to PNG."""
        success, path = self.air_writer.save_as_png()
        if success:
            messagebox.showinfo("Saved Drawing", f"Drawing saved successfully to:\n{path}")
        else:
            messagebox.showerror("Save Failed", f"Could not save drawing:\n{path}")

    def _manual_launch_app(self):
        """Launches application selected in listbox."""
        sel = self.app_list_box.curselection()
        if sel:
            self.app_launcher.select_index(sel[0])
            success, msg = self.app_launcher.launch_selected()
            if not success:
                messagebox.showerror("Launch Error", msg)

    def open_whiteboard_window(self):
        """Opens dedicated high-resolution virtual whiteboard window."""
        if self.whiteboard_window is not None and tk.Toplevel.winfo_exists(self.whiteboard_window):
            self.whiteboard_window.lift()
            return

        self.set_mode(AppMode.WHITEBOARD)
        self.whiteboard_window = tk.Toplevel(self.root)
        self.whiteboard_window.title("GestureLink – Virtual Whiteboard")
        self.whiteboard_window.geometry("1000x640")
        self.whiteboard_window.configure(bg="#0B0F19")

        # Top Whiteboard Toolbar
        wb_bar = tk.Frame(self.whiteboard_window, bg="#131B2E", padx=10, pady=6)
        wb_bar.pack(fill=tk.X)

        tk.Label(wb_bar, text="VIRTUAL WHITEBOARD", font=("Segoe UI", 11, "bold"),
                 bg="#131B2E", fg="#38BDF8").pack(side=tk.LEFT, padx=6)

        btn_wb_clear = tk.Button(wb_bar, text="Clear", bg="#334155", fg="#FFF", relief=tk.FLAT,
                                 command=self.whiteboard.clear)
        btn_wb_clear.pack(side=tk.LEFT, padx=4)

        btn_wb_undo = tk.Button(wb_bar, text="Undo", bg="#334155", fg="#FFF", relief=tk.FLAT,
                                command=self.whiteboard.undo)
        btn_wb_undo.pack(side=tk.LEFT, padx=4)

        btn_wb_save = tk.Button(wb_bar, text="Save PNG", bg="#0284C7", fg="#FFF", relief=tk.FLAT,
                                command=lambda: messagebox.showinfo("Whiteboard Saved", self.whiteboard.save_as_png()[1]))
        btn_wb_save.pack(side=tk.LEFT, padx=4)

        # Whiteboard Display Label
        self.whiteboard_canvas_label = tk.Label(self.whiteboard_window, bg="#181C26")
        self.whiteboard_canvas_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def start_system(self):
        """Starts camera and the background processing worker."""
        self.camera.start()
        self.worker_running = True
        self.worker_thread = threading.Thread(target=self._cv_worker, name="GestureCVWorker", daemon=True)
        self.worker_thread.start()

    def _cv_worker(self):
        """
        High-speed background computer vision and automation thread.
        Never touches Tkinter widgets directly (updates self.ui_state).
        """
        while self.worker_running:
            try:
                ret, frame = self.camera.read()
                if not ret or frame is None:
                    self.ui_state["camera_connected"] = False
                    time.sleep(0.02)
                    continue

                self.ui_state["camera_connected"] = self.camera.is_connected
                self.ui_state["fps"] = self.camera.fps

                # 1. Process Hands
                hands = self.tracker.process(frame)
                hand_detected = len(hands) > 0
                self.ui_state["hand_detected"] = hand_detected

                active_gesture = GestureType.NONE
                confidence = 0.0
                action_desc = "Idle"
                hand_data = hands[0] if hand_detected else None

                if hand_detected and hand_data:
                    # 2. Gesture Recognition
                    active_gesture, confidence, metrics = self.recognizer.recognize(hand_data)
                    lms = hand_data["landmarks"]

                    # Extract landmark coordinates
                    index_norm = (lms[8]["x"], lms[8]["y"])
                    thumb_norm = (lms[4]["x"], lms[4]["y"])
                    index_px = (lms[8]["px"], lms[8]["py"])

                    self.ui_state["index_pos"] = index_norm
                    self.ui_state["thumb_pos"] = thumb_norm

                    # 3. Gesture Stability Tracking
                    stable_gesture, is_new_event, hold_dur = self.engine.stability_tracker.update(active_gesture)
                    self.ui_state["stability_ratio"] = self.engine.stability_tracker.get_stability_ratio()

                    # 4. Dispatch automation based on Active Mode (if not Emergency Stopped)
                    if not self.engine.emergency_stop:
                        action_desc = self._execute_mode_automation(
                            stable_gesture, is_new_event, hold_dur, index_norm, index_px, metrics
                        )
                    else:
                        action_desc = "AUTOMATION LOCKED"

                    # 5. Draw Skeleton on frame if enabled
                    if self.show_skeleton_flag:
                        self.tracker.draw_landmarks(frame, lms)

                else:
                    self.engine.stability_tracker.update(GestureType.NONE)
                    self.mouse.reset_positions()
                    self.air_writer.end_stroke()
                    self.presentation.reset_tracking()

                # 6. Air Writing Canvas Overlay (if in Air Writing mode)
                if self.engine.current_mode == AppMode.AIR_WRITING:
                    frame = self.air_writer.overlay_on_frame(frame)

                # 7. Render Telemetry HUD on video frame
                hud_frame = self.hud.draw_hud(
                    frame=frame,
                    hand_data=hand_data,
                    current_gesture=active_gesture,
                    gesture_confidence=confidence,
                    current_mode=self.engine.current_mode,
                    action_desc=action_desc,
                    fps=self.camera.fps,
                    margin_x=self.config.interaction_margin_x,
                    margin_y=self.config.interaction_margin_y,
                    show_skeleton=self.show_skeleton_flag,
                    show_box=self.show_boundary_flag,
                    emergency_stop=self.engine.emergency_stop
                )

                # Store states for UI thread
                self.ui_state["gesture"] = active_gesture
                self.ui_state["gesture_confidence"] = confidence
                self.ui_state["action_desc"] = action_desc
                self.ui_state["emergency_stop"] = self.engine.emergency_stop
                self._last_processed_frame = hud_frame

                time.sleep(0.005)
            except Exception as e:
                logger.error(f"Error in vision worker thread: {e}", exc_info=True)
                time.sleep(0.02)

    def _execute_mode_automation(self, gesture: GestureType, is_new_event: bool,
                                 hold_dur: float, index_norm: Tuple[float, float],
                                 index_px: Tuple[int, int], metrics: Dict[str, Any]) -> str:
        """Dispatches stabilized gestures to the active operating mode."""
        mode = self.engine.current_mode
        action = "Tracking"

        # --- MOUSE CONTROL MODE ---
        if mode == AppMode.MOUSE_CONTROL:
            if gesture == GestureType.INDEX_FINGER:
                cx, cy = self.mouse.move_cursor(index_norm[0], index_norm[1])
                action = f"Cursor ({cx}, {cy})"

            elif gesture == GestureType.PINCH:
                # Left Click or Drag
                click_act = self.mouse.handle_pinch(is_pinched=True, hold_duration=hold_dur)
                if click_act:
                    action = click_act
                    self.hud.trigger_click_effect(index_px[0], index_px[1], color=(0, 255, 255))
                else:
                    action = "Holding Pinch"

            elif gesture == GestureType.OK_GESTURE:
                if is_new_event and self.mouse.double_click():
                    action = "Double Click"
                    self.hud.trigger_click_effect(index_px[0], index_px[1], color=(0, 200, 255))

            elif gesture == GestureType.TWO_FINGERS:
                sc_act = self.mouse.handle_scroll(index_norm[1])
                if sc_act:
                    action = sc_act

            elif gesture == GestureType.FIST:
                if is_new_event:
                    self.keyboard.press("f11")
                    action = "Toggle Fullscreen / Minimize"

            elif gesture == GestureType.OPEN_PALM:
                self.mouse.reset_positions()
                action = "Idle (Safe Palm)"

            # Ensure mouse drag releases if pinch stops
            if gesture != GestureType.PINCH:
                self.mouse.handle_pinch(is_pinched=False)

        # --- AIR WRITING MODE ---
        elif mode == AppMode.AIR_WRITING:
            if gesture == GestureType.INDEX_FINGER:
                self.air_writer.add_point(index_px[0], index_px[1])
                action = "Drawing Stroke"
            elif gesture == GestureType.TWO_FINGERS:
                self.air_writer.erase_at(index_px[0], index_px[1])
                action = "Erasing"
            elif gesture == GestureType.OPEN_PALM:
                self.air_writer.end_stroke()
                action = "Hover / Pen Lifted"
            elif gesture == GestureType.PINCH:
                if is_new_event:
                    c = self.air_writer.cycle_color()
                    action = f"Color: {c}"

        # --- VIRTUAL WHITEBOARD MODE ---
        elif mode == AppMode.WHITEBOARD:
            if gesture == GestureType.INDEX_FINGER:
                self.whiteboard.process_gesture_point(index_norm[0], index_norm[1], "draw")
                action = "Whiteboard Drawing"
            elif gesture == GestureType.TWO_FINGERS:
                self.whiteboard.process_gesture_point(index_norm[0], index_norm[1], "erase")
                action = "Whiteboard Erasing"
            else:
                self.whiteboard.process_gesture_point(index_norm[0], index_norm[1], "hover")
                action = "Whiteboard Hover"

        # --- APPLICATION CONTROL MODE ---
        elif mode == AppMode.APPLICATION_CONTROL:
            if gesture == GestureType.TWO_FINGERS and is_new_event:
                app = self.app_launcher.select_next()
                if app:
                    action = f"Selected: {app['name']}"
                    # Update listbox selection
                    self.root.after(0, lambda: self.app_list_box.selection_clear(0, tk.END))
                    self.root.after(0, lambda: self.app_list_box.selection_set(self.app_launcher.selected_index))

            elif gesture == GestureType.THUMB_UP and is_new_event:
                success, msg = self.app_launcher.launch_selected()
                action = msg

            elif gesture == GestureType.THUMB_DOWN and is_new_event:
                self.set_mode(AppMode.MOUSE_CONTROL)
                action = "Cancelled App Launcher"

        # --- PRESENTATION CONTROL MODE ---
        elif mode == AppMode.PRESENTATION_CONTROL:
            # Swipe detection
            swipe_act = self.presentation.handle_swipe(index_norm[0])
            if swipe_act:
                action = swipe_act
            elif gesture == GestureType.THUMB_UP and is_new_event:
                action = self.presentation.start_presentation()
            elif (gesture == GestureType.FIST or gesture == GestureType.THUMB_DOWN) and is_new_event:
                action = self.presentation.exit_presentation()
            elif gesture == GestureType.TWO_FINGERS and is_new_event:
                action = self.presentation.next_slide()

        # --- IDLE MODE ---
        elif mode == AppMode.IDLE:
            action = "Paused"

        return action

    def _on_ui_tick(self):
        """
        Thread-safe Tkinter refresh loop.
        Updates video preview canvas and status telemetry badges.
        """
        # 1. Update Video Preview
        if hasattr(self, "_last_processed_frame") and self._last_processed_frame is not None:
            try:
                frame_bgr = self._last_processed_frame
                # Resize to fit canvas
                canvas_w = self.video_canvas.winfo_width()
                canvas_h = self.video_canvas.winfo_height()

                if canvas_w > 100 and canvas_h > 100:
                    resized = cv2.resize(frame_bgr, (canvas_w, canvas_h))
                else:
                    resized = cv2.resize(frame_bgr, (self.display_width, self.display_height))

                rgb_frame = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb_frame)
                self.preview_photo = ImageTk.PhotoImage(image=img)
                if self.canvas_image_id is None:
                    self.canvas_image_id = self.video_canvas.create_image(0, 0, image=self.preview_photo, anchor=tk.NW)
                else:
                    self.video_canvas.itemconfig(self.canvas_image_id, image=self.preview_photo)
            except Exception as e:
                logger.error(f"Video canvas render exception: {e}")

        # 2. Update Virtual Whiteboard Window (if open)
        if self.whiteboard_window is not None and tk.Toplevel.winfo_exists(self.whiteboard_window):
            if self.whiteboard_canvas_label is not None:
                try:
                    wb_display = self.whiteboard.get_render_frame()
                    wb_rgb = cv2.cvtColor(wb_display, cv2.COLOR_BGR2RGB)
                    # Resize to fit window
                    ww = self.whiteboard_canvas_label.winfo_width()
                    wh = self.whiteboard_canvas_label.winfo_height()
                    if ww > 50 and wh > 50:
                        wb_rgb = cv2.resize(wb_rgb, (ww, wh))
                    wb_img = Image.fromarray(wb_rgb)
                    self.whiteboard_photo = ImageTk.PhotoImage(image=wb_img)
                    self.whiteboard_canvas_label.config(image=self.whiteboard_photo)
                except Exception as e:
                    logger.debug(f"Whiteboard render exception: {e}")

        # 3. Update Status Pills
        if self.ui_state["camera_connected"]:
            self.pill_cam.config(text="● Camera: Connected", fg="#10B981")
        else:
            self.pill_cam.config(text="○ Camera: Offline", fg="#F43F5E")

        if self.ui_state["hand_detected"]:
            self.pill_hand.config(text="● Hand: Active", fg="#10B981")
        else:
            self.pill_hand.config(text="○ Hand: Searching", fg="#94A3B8")

        # 4. Update Detected Gesture & Action
        curr_g = self.ui_state["gesture"]
        self.lbl_gesture_emoji.config(text=GESTURE_EMOJIS.get(curr_g, "⚪"))
        self.lbl_gesture_name.config(text=curr_g.value.upper())

        ratio = int(self.ui_state["stability_ratio"] * 100)
        self.stability_bar["value"] = ratio
        pct = int(self.ui_state["gesture_confidence"] * 100)
        self.lbl_confidence.config(text=f"Confidence: {pct}% | Stability: {ratio}%")

        self.lbl_action.config(text=self.ui_state["action_desc"])

        # 5. Update Telemetry
        if self.debug_mode_flag:
            self.lbl_telemetry_fps.config(text=f"FPS: {self.ui_state['fps']:.1f}")
            ix, iy = self.ui_state["index_pos"]
            tx, ty = self.ui_state["thumb_pos"]
            self.lbl_telemetry_index.config(text=f"Index: ({ix:.2f}, {iy:.2f})")
            self.lbl_telemetry_thumb.config(text=f"Thumb: ({tx:.2f}, {ty:.2f})")

        # Re-schedule next tick
        self.root.after(25, self._on_ui_tick)

    def on_closing(self):
        """Releases camera, stops background workers, and closes application cleanly."""
        logger.info("Application closing initiated.")
        self.worker_running = False
        if self.worker_thread is not None and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=1.0)

        self.camera.stop()
        self.tracker.close()
        self.root.destroy()
        logger.info("GestureLink closed cleanly.")

"""
GestureLink - Settings & Calibration UI
Modal dialog for configuring camera, cursor smoothing, sensitivity, gesture thresholds, and applications.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Callable, Optional
from config import AppConfig, save_config, DEFAULT_APPS
from utils.logger import get_logger

logger = get_logger("SettingsUI")


class SettingsDialog(tk.Toplevel):
    """
    Modern modal settings and calibration dialog window.
    """

    def __init__(self, parent, config: AppConfig, on_save_callback: Optional[Callable[[AppConfig], None]] = None):
        super().__init__(parent)
        self.title("GestureLink - Settings & Calibration")
        self.geometry("640x680")
        self.minsize(580, 560)
        self.configure(bg="#0F172A")
        self.transient(parent)
        self.grab_set()

        self.config = config
        self.on_save_callback = on_save_callback

        self._init_ui()

    def _init_ui(self):
        # Configure styles
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook", background="#0F172A", borderwidth=0)
        style.configure("TNotebook.Tab", background="#1E293B", foreground="#E2E8F0", padding=[16, 8], font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#06B6D4")], foreground=[("selected", "#0F172A")])

        # Header Title
        header = tk.Frame(self, bg="#0F172A")
        header.pack(fill=tk.X, padx=20, pady=(16, 10))

        tk.Label(
            header, text="SETTINGS & CALIBRATION", font=("Segoe UI", 15, "bold"),
            bg="#0F172A", fg="#38BDF8"
        ).pack(anchor="w")

        tk.Label(
            header, text="Tune touchless sensitivity, gesture thresholds, and configured applications.",
            font=("Segoe UI", 9), bg="#0F172A", fg="#94A3B8"
        ).pack(anchor="w")

        # Notebook Tabs
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Tab 1: Mouse & Gestures
        tab_mouse = tk.Frame(notebook, bg="#1E293B")
        notebook.add(tab_mouse, text="Mouse & Gestures")
        self._build_mouse_tab(tab_mouse)

        # Tab 2: Applications Manager
        tab_apps = tk.Frame(notebook, bg="#1E293B")
        notebook.add(tab_apps, text="Application Launcher")
        self._build_apps_tab(tab_apps)

        # Bottom Action Bar
        bottom_bar = tk.Frame(self, bg="#0F172A")
        bottom_bar.pack(fill=tk.X, padx=20, pady=(10, 16))

        btn_reset = tk.Button(
            bottom_bar, text="Reset to Defaults", font=("Segoe UI", 9, "bold"),
            bg="#334155", fg="#F1F5F9", activebackground="#475569", activeforeground="#FFF",
            relief=tk.FLAT, padx=14, pady=6, cursor="hand2", command=self._reset_defaults
        )
        btn_reset.pack(side=tk.LEFT)

        btn_cancel = tk.Button(
            bottom_bar, text="Cancel", font=("Segoe UI", 9),
            bg="#1E293B", fg="#94A3B8", activebackground="#334155", activeforeground="#FFF",
            relief=tk.FLAT, padx=14, pady=6, cursor="hand2", command=self.destroy
        )
        btn_cancel.pack(side=tk.RIGHT, padx=(8, 0))

        btn_save = tk.Button(
            bottom_bar, text="Save Settings", font=("Segoe UI", 9, "bold"),
            bg="#06B6D4", fg="#0F172A", activebackground="#22D3EE", activeforeground="#000",
            relief=tk.FLAT, padx=18, pady=6, cursor="hand2", command=self._save_settings
        )
        btn_save.pack(side=tk.RIGHT)

    def _build_mouse_tab(self, parent):
        container = tk.Frame(parent, bg="#1E293B", padx=20, pady=15)
        container.pack(fill=tk.BOTH, expand=True)

        # Cursor Smoothing
        self.slider_smoothing, self.lbl_smoothing = self._create_slider(
            container, "Cursor Smoothing", 0.1, 0.95, self.config.cursor_smoothing, 0.05,
            "Higher = smoother movement; Lower = sharper/instant response."
        )

        # Cursor Sensitivity
        self.slider_sensitivity, self.lbl_sensitivity = self._create_slider(
            container, "Cursor Sensitivity", 0.5, 3.0, self.config.cursor_sensitivity, 0.1,
            "Cursor movement speed multiplier across your screen."
        )

        # Interaction Margin
        self.slider_margin, self.lbl_margin = self._create_slider(
            container, "Interaction Zone Margin", 0.05, 0.30, self.config.interaction_margin_x, 0.01,
            "Padding from webcam edge to reach full screen comfortably."
        )

        # Pinch Threshold
        self.slider_pinch, self.lbl_pinch = self._create_slider(
            container, "Pinch Click Threshold", 0.02, 0.12, self.config.pinch_threshold, 0.005,
            "Fingertip proximity required to register a left-click pinch."
        )

        # Scroll Sensitivity
        self.slider_scroll, self.lbl_scroll = self._create_slider(
            container, "Scroll Sensitivity", 0.5, 3.0, self.config.scroll_sensitivity, 0.1,
            "Speed multiplier for two-finger page scrolling."
        )

        # Stability Frames
        self.slider_stability, self.lbl_stability = self._create_slider(
            container, "Gesture Stability Frames", 2, 10, self.config.gesture_stability_frames, 1.0,
            "Consecutive frames required to confirm gesture changes."
        )

    def _create_slider(self, parent, label_text, min_val, max_val, curr_val, resolution, hint_text=""):
        frame = tk.Frame(parent, bg="#1E293B")
        frame.pack(fill=tk.X, pady=6)

        top_row = tk.Frame(frame, bg="#1E293B")
        top_row.pack(fill=tk.X)

        tk.Label(top_row, text=label_text, font=("Segoe UI", 9, "bold"), bg="#1E293B", fg="#F8FAFC").pack(side=tk.LEFT)
        val_label = tk.Label(top_row, text=f"{curr_val:.2f}" if resolution < 1.0 else f"{int(curr_val)}",
                             font=("Segoe UI", 9, "bold"), bg="#1E293B", fg="#38BDF8")
        val_label.pack(side=tk.RIGHT)

        slider = tk.Scale(
            frame, from_=min_val, to=max_val, resolution=resolution, orient=tk.HORIZONTAL,
            bg="#1E293B", fg="#94A3B8", activebackground="#06B6D4", troughcolor="#334155",
            highlightthickness=0, showvalue=False,
            command=lambda v: val_label.config(text=f"{float(v):.2f}" if resolution < 1.0 else f"{int(float(v))}")
        )
        slider.set(curr_val)
        slider.pack(fill=tk.X, pady=(2, 0))

        if hint_text:
            tk.Label(frame, text=hint_text, font=("Segoe UI", 8), bg="#1E293B", fg="#64748B").pack(anchor="w")

        return slider, val_label

    def _build_apps_tab(self, parent):
        container = tk.Frame(parent, bg="#1E293B", padx=20, pady=15)
        container.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            container, text="Configured Applications for Touchless Launcher Mode:",
            font=("Segoe UI", 9, "bold"), bg="#1E293B", fg="#F8FAFC"
        ).pack(anchor="w", pady=(0, 6))

        # Listbox for apps
        list_frame = tk.Frame(container, bg="#0F172A", relief=tk.FLAT)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.app_listbox = tk.Listbox(
            list_frame, font=("Segoe UI", 9), bg="#0F172A", fg="#F8FAFC",
            selectbackground="#06B6D4", selectforeground="#0F172A",
            highlightthickness=0, relief=tk.FLAT
        )
        self.app_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=6)

        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.app_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.app_listbox.config(yscrollcommand=scrollbar.set)

        # Populate current apps
        self.current_apps = [dict(a) for a in self.config.applications]
        self._refresh_apps_listbox()

        # Action buttons for apps
        btn_frame = tk.Frame(container, bg="#1E293B")
        btn_frame.pack(fill=tk.X)

        btn_add = tk.Button(
            btn_frame, text="+ Add Application", font=("Segoe UI", 8, "bold"),
            bg="#334155", fg="#38BDF8", activebackground="#475569", relief=tk.FLAT,
            padx=10, pady=5, cursor="hand2", command=self._add_app_dialog
        )
        btn_add.pack(side=tk.LEFT, padx=(0, 6))

        btn_remove = tk.Button(
            btn_frame, text="- Remove Selected", font=("Segoe UI", 8),
            bg="#334155", fg="#F43F5E", activebackground="#475569", relief=tk.FLAT,
            padx=10, pady=5, cursor="hand2", command=self._remove_selected_app
        )
        btn_remove.pack(side=tk.LEFT)

    def _refresh_apps_listbox(self):
        self.app_listbox.delete(0, tk.END)
        for app in self.current_apps:
            icon = app.get("icon", "🚀")
            name = app.get("name", "Unknown")
            path = app.get("path", "")
            self.app_listbox.insert(tk.END, f"{icon}  {name}  ({path})")

    def _add_app_dialog(self):
        # Open file dialog to choose executable
        filepath = filedialog.askopenfilename(
            title="Select Application Executable",
            filetypes=[("Executables", "*.exe"), ("All Files", "*.*")]
        )
        if filepath:
            filename = filepath.split("/")[-1].replace(".exe", "").capitalize()
            self.current_apps.append({
                "name": filename,
                "path": filepath,
                "icon": "⚡",
                "type": "executable"
            })
            self._refresh_apps_listbox()

    def _remove_selected_app(self):
        sel = self.app_listbox.curselection()
        if sel:
            idx = sel[0]
            del self.current_apps[idx]
            self._refresh_apps_listbox()

    def _reset_defaults(self):
        if messagebox.askyesno("Reset to Defaults", "Are you sure you want to revert all settings to factory defaults?"):
            default_cfg = AppConfig()
            self.slider_smoothing.set(default_cfg.cursor_smoothing)
            self.slider_sensitivity.set(default_cfg.cursor_sensitivity)
            self.slider_margin.set(default_cfg.interaction_margin_x)
            self.slider_pinch.set(default_cfg.pinch_threshold)
            self.slider_scroll.set(default_cfg.scroll_sensitivity)
            self.slider_stability.set(default_cfg.gesture_stability_frames)
            self.current_apps = [dict(a) for a in DEFAULT_APPS]
            self._refresh_apps_listbox()

    def _save_settings(self):
        # Apply slider values
        self.config.cursor_smoothing = float(self.slider_smoothing.get())
        self.config.cursor_sensitivity = float(self.slider_sensitivity.get())
        self.config.interaction_margin_x = float(self.slider_margin.get())
        self.config.interaction_margin_y = float(self.slider_margin.get()) * 1.2
        self.config.pinch_threshold = float(self.slider_pinch.get())
        self.config.scroll_sensitivity = float(self.slider_scroll.get())
        self.config.gesture_stability_frames = int(self.slider_stability.get())
        self.config.applications = list(self.current_apps)

        save_config(self.config)

        if self.on_save_callback:
            self.on_save_callback(self.config)

        logger.info("Settings dialog saved changes.")
        self.destroy()

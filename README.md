# GestureLink – Vision-Based Touchless Laptop Control System

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-5.0%2B-green.svg)](https://opencv.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Tasks%20%26%20Solutions-orange.svg)](https://developers.google.com/mediapipe)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%2F%2011-0078D6.svg)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

**GestureLink** is an advanced, real-time, touchless desktop control system that transforms any standard laptop webcam into an intuitive spatial input interface. Using local computer vision and deep learning landmark detection, users can navigate the operating system, move the mouse cursor, click, drag, scroll, write in the air, sketch on a virtual whiteboard, browse and launch desktop applications, and control slide presentations—**completely touchless without touching a mouse or keyboard**.

---

## 🌟 Key Features

- 🎯 **High-Precision Cursor Navigation**: Sub-millimeter tracking with adaptive exponential smoothing (EMA) and jitter-filtering deadzones.
- 🖐️ **8 Natural Hand Gestures**: Open Palm, Index Finger, Two Fingers, Pinch, Fist, Thumb Up, Thumb Down, and OK Gesture.
- 🛡️ **Gesture Stability & Safety Engine**: Multi-frame temporal confirmation, debouncing, universal cooldowns, PyAutoGUI fail-safe protection, and an instant Emergency Stop kill-switch (`ESC`).
- ✍️ **3D Air Writing**: Draw glowing color strokes directly in the air on live camera feed, featuring stroke undo, dynamic eraser, and PNG export.
- 📋 **Virtual Whiteboard**: Dedicated high-resolution digital canvas for sketching, teaching, or presentations, controllable entirely via air gestures.
- 🚀 **Windows Application Launcher**: Gesture-driven circular menu to browse and safely launch desktop software (Notepad, Calculator, File Explorer, Browser, Paint, Task Manager, or custom user executables).
- 📊 **Touchless Presentation Controller**: Seamless slide navigation for PowerPoint, Google Slides, and PDF viewers using directional hand gestures and swipe velocity detection.
- 🎛️ **Live Calibration & Settings**: Interactive control center with live sensitivity sliders, margin tuning, pinch thresholds, and JSON-backed persistence (`settings.json`).
- 🔒 **100% Offline & Private**: Zero cloud dependencies, zero external APIs, zero accounts required. All computer vision models execute locally on your CPU/GPU.

---

## 🏗️ System Architecture

```
                    ┌─────────────────────────┐
                    │     Laptop Webcam       │
                    └───────────┬─────────────┘
                                │ (640x480 @ 30fps)
                                ▼
                    ┌─────────────────────────┐
                    │     Camera Manager      │ (DirectShow Thread)
                    └───────────┬─────────────┘
                                │ Mirrored Frame
                                ▼
                    ┌─────────────────────────┐
                    │   MediaPipe Tracker     │ (21 3D Landmarks)
                    └───────────┬─────────────┘
                                │ Palm Scale & Relative Angles
                                ▼
                    ┌─────────────────────────┐
                    │   Gesture Recognizer    │ (8 Classifiers)
                    └───────────┬─────────────┘
                                │ Raw Detection
                                ▼
                    ┌─────────────────────────┐
                    │ Gesture Stability Engine│ (N-Frame Verification + Debounce)
                    └───────────┬─────────────┘
                                │ Stabilized Event
                                ▼
                    ┌─────────────────────────┐
                    │      Mode Manager       │
                    └───────────┬─────────────┘
         ┌──────────────────────┼──────────────────────┐
         ▼                      ▼                      ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  Mouse Control   │  │   Air Writing    │  │   App Launcher   │
│  Cursor / Click  │  │  Digital Canvas  │  │  Windows Process │
└──────────────────┘  └──────────────────┘  └──────────────────┘
         │                      │                      │
         └──────────────────────┼──────────────────────┘
                                ▼
                    ┌─────────────────────────┐
                    │  Presentation Controller│
                    │   Slide Navigation (F5) │
                    └─────────────────────────┘
```

---

## 📁 Project Directory Structure

```
GestureLink/
│
├── main.py                     # Application entry point & lifecycle manager
├── config.py                   # AppConfig dataclass, settings validation, JSON storage
├── settings.json               # Local persistent configuration file
├── test_system.py              # Automated 12-stage test suite
├── requirements.txt            # Python package dependencies
├── README.md                   # Comprehensive project documentation
│
├── core/
│   ├── __init__.py
│   ├── camera.py               # Threaded camera capture, mirroring, reconnect & fallback
│   ├── hand_tracking.py        # MediaPipe 21-landmark tracking & rotation-invariant finger states
│   ├── gesture_recognition.py  # 8 geometric gesture classifiers & confidence metrics
│   └── gesture_engine.py       # Stability window buffer, debouncing, cooldowns & mode manager
│
├── controls/
│   ├── __init__.py
│   ├── mouse_control.py        # Cursor smoothing, interaction zone mapping, clicks & scroll
│   ├── keyboard_control.py     # Safe whitelisted keyboard shortcut execution
│   └── app_launcher.py         # Configurable application launcher for Windows
│
├── features/
│   ├── __init__.py
│   ├── air_writing.py          # Continuous stroke rendering, eraser, undo & PNG export
│   ├── virtual_whiteboard.py   # Dedicated digital whiteboard with undo/redo & gesture cursor
│   └── presentation_control.py # Slide deck navigation, swipe velocity & slideshow control
│
├── ui/
│   ├── __init__.py
│   ├── dashboard.py            # Modern dark desktop UI with live video canvas & HUD telemetry
│   ├── settings.py             # Modal calibration dialog with sliders & app management
│   └── overlays.py             # Futuristic HUD overlays, interaction box & animated click ripples
│
├── utils/
│   ├── __init__.py
│   ├── logger.py               # Rotating file and console logger
│   └── helpers.py              # Euclidean math, angles, EMA smoothing & OpenCV HUD drawing
│
├── assets/
│   ├── icons/
│   │   └── gesturelink_icon.png
│   └── models/
│       └── hand_landmarker.task # Offline MediaPipe Tasks model bundle (7.8 MB)
│
├── logs/
│   └── gesturelink.log         # Application execution log
│
└── captures/                   # Saved air drawings and whiteboard snapshots
```

---

## ✋ Supported Gestures Reference

| Gesture | Emoji | Finger Pattern | Mouse Mode Action | Air Writing Mode | Presentation Mode | App Launcher Mode |
|:---|:---:|:---|:---|:---|:---|:---|
| **Open Palm** | 🖐️ | All 5 fingers extended | Pause / Stop action | Pen Lifted (Hover) | Pause action | Return / Idle |
| **Index Finger** | ☝️ | Index extended, others closed | Move Mouse Cursor | Draw Smooth Stroke | - | - |
| **Pinch** | 🤏 | Thumb & Index tips close | Left Click / Hold to Drag | Cycle Pen Color | - | - |
| **Two Fingers** | ✌️ | Index + Middle extended | Vertical Page Scroll | Eraser Tool | Next Slide (tap) | Select Next App |
| **OK Gesture** | 👌 | Pinch + Middle/Ring/Pinky open | Double Click | - | - | - |
| **Fist** | ✊ | All 5 fingers closed | Toggle Fullscreen | - | Exit Slideshow (ESC) | - |
| **Thumb Up** | 👍 | Thumb up, 4 fingers curled | Confirm Action | - | Start Slideshow (F5) | Launch Selected App |
| **Thumb Down** | 👎 | Thumb down, 4 fingers curled | Cancel Action | - | Exit Slideshow (ESC) | Cancel Selection |

---

## 💻 System Modes

1. **🖱️ Mouse Control Mode (`MOUSE_CONTROL`)**
   - **Pointer**: Point with index finger (☝️) to move cursor smoothly across screen.
   - **Left Click**: Pinch thumb and index tips together (🤏).
   - **Drag & Drop**: Hold pinch for >0.4 seconds to grab; release pinch to drop.
   - **Double Click**: Make OK gesture (👌).
   - **Scrolling**: Show two fingers (✌️) and move hand up to scroll up, down to scroll down.

2. **✍️ Air Writing Mode (`AIR_WRITING`)**
   - **Draw**: Index finger (☝️) traces smooth digital lines in the air.
   - **Hover**: Open palm (🖐️) lifts pen without drawing.
   - **Eraser**: Two fingers (✌️) erases nearby strokes.
   - **Colors**: Pinch (🤏) or toolbar button cycles through Neon Cyan, Emerald, Sunburst, Magenta, and White.
   - **Export**: Save your air drawing as a PNG image with a single click.

3. **📋 Virtual Whiteboard Mode (`WHITEBOARD`)**
   - Opens a dedicated 1280x720 whiteboard window.
   - Complete undo/redo stack.
   - Full touchless drawing with index finger and erasing with two fingers.

4. **🚀 Application Launcher Mode (`APPLICATION_CONTROL`)**
   - Displays a visual carousel of your favourite desktop apps.
   - **Browse**: Two fingers (✌️) cycles to the next application.
   - **Launch**: Thumb Up (👍) opens the selected software immediately.
   - **Cancel**: Thumb Down (👎) reverts to Mouse Control.

5. **📊 Presentation Mode (`PRESENTATION_CONTROL`)**
   - **Next Slide**: Quick hand swipe to the right or two fingers (✌️).
   - **Previous Slide**: Quick hand swipe to the left.
   - **Start Slideshow**: Thumb Up (👍) triggers `F5`.
   - **Exit Slideshow**: Fist (✊) or Thumb Down (👎) triggers `Escape`.

6. **⏸️ Idle Mode (`IDLE`)**
   - Temporarily suspends desktop inputs while continuing to track hand telemetry safely.

---

## 🚀 Installation & Setup (Windows 10 / 11)

### Prerequisites

- **Python 3.10, 3.11, or 3.12** installed on your system.
- An integrated laptop webcam or USB external webcam.

### 1. Clone or Open Project Directory

```powershell
cd c:\Users\HP\OneDrive\Desktop\GestureLink
```

### 2. Create and Activate Virtual Environment (Recommended)

```powershell
# Create virtual environment
python -m venv venv

# Activate on Windows PowerShell
venv\Scripts\Activate.ps1

# (Or in Command Prompt: venv\Scripts\activate.bat)
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

*Required packages:*
- `opencv-python>=4.8.0`
- `mediapipe>=0.10.0`
- `pyautogui>=0.9.54`
- `numpy>=1.24.0`
- `pillow>=10.0.0`

---

## 🏃 Running the Application

Launch the desktop system with:

```powershell
python main.py
```

### Running Automated Verification Tests

To verify all 12 modules, geometric algorithms, camera pipelines, and gesture classifiers:

```powershell
python -m unittest test_system.py -v
```

---

## ⚙️ Calibration & Settings Guide

Click the **Settings & Calibration** button on the bottom bar to open the calibration dialog:

- **Cursor Smoothing (0.10 – 0.95)**: Adjusts the exponential moving average alpha. Higher values provide buttery smooth, cinematic cursor movement; lower values give immediate, twitch-responsive cursor response.
- **Cursor Sensitivity (0.5 – 3.0)**: Multiplies physical hand movement across your desktop resolution.
- **Interaction Zone Margin (0.05 – 0.30)**: Normalised boundary padding. Allows comfortable reach to all 4 screen corners without overextending your arm beyond the camera frame.
- **Pinch Threshold (0.02 – 0.12)**: Distance between thumb tip and index tip required to trigger left click.
- **Scroll Sensitivity (0.2 – 4.0)**: Adjusts page scrolling speed during two-finger vertical gestures.
- **Gesture Stability Frames (2 – 10)**: Consecutive frame confirmation buffer to eliminate gesture flickering.
- **App Launcher Customization**: Add any `.exe` application path from your system into the touchless launch carousel.

Settings are saved automatically in `settings.json` and persist across sessions.

---

## 🛡️ Safety System & Fail-Safes

Because GestureLink controls physical mouse and keyboard inputs, comprehensive safety features are built-in:

1. **Prominent Emergency Stop Button**: Click the bright red button on the UI or press **`ESC`** at any time to instantly lock all automation.
2. **Physical Mouse Fail-Safe**: Moving your physical mouse to the top-left corner of the screen immediately halts PyAutoGUI.
3. **Gesture Cooldowns**: Every single-stroke action (click, double-click, slide change, app launch) enforces a hardware cooldown period to prevent accidental repeats.
4. **Zero Shell Execution**: No dangerous system commands or terminal shells are ever executed via gestures.
5. **No File Deletion**: Gestures cannot delete or modify system files.

---

## 📷 Camera Permissions & DirectShow

On Windows 10/11, ensure camera access is enabled:
1. Open **Windows Settings** → **Privacy & Security** → **Camera**.
2. Ensure **Camera access** is toggled **On**.
3. Ensure **Let desktop apps access your camera** is toggled **On**.
4. If another application (Zoom, Teams, Discord) is locking the webcam, GestureLink will automatically display an informative fallback test screen without crashing.

---

## ❓ Troubleshooting

| Issue | Cause | Solution |
|:---|:---|:---|
| `Camera 0 unavailable` | Webcam is in use by another app or permissions denied | Close other camera apps; verify Windows camera privacy settings. |
| Cursor feels jerky | Camera FPS is low or room lighting is dim | Ensure good front lighting; increase `Cursor Smoothing` slider in Settings. |
| Difficult to reach screen corners | Interaction zone too large | Increase `Interaction Zone Margin` in Settings (e.g. to 0.18). |
| Pinch triggers accidentally | Pinch threshold too wide | Lower `Pinch Threshold` slider in Settings (e.g. to 0.04). |
| Accidental gesture triggers | Stability threshold too low | Increase `Gesture Stability Frames` to 5 or 6 frames. |

---

## 🔮 Future Improvements

- [ ] Two-handed bimanual control (e.g., left hand zooms, right hand navigates).
- [ ] Custom user gesture recorder with dynamic KNN/SVM landmark training.
- [ ] Touchless audio volume gesture dial.
- [ ] System tray minimisation for background operation.
- [ ] Multi-monitor workspace selection.

---

## 📄 License

This project is licensed under the MIT License - feel free to use, modify, and build upon it for academic and personal projects.

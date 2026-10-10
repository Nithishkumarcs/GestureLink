@echo off
title GestureLink - Vision-Based Touchless Laptop Control System
cd /d "%~dp0"

echo ===================================================================
echo     GestureLink - Vision-Based Touchless Laptop Control System
echo ===================================================================
echo.
echo Launching application, please wait...
echo (Webcam will activate in a moment)
echo.

python main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Application closed with an issue.
    echo Press any key to close this window...
    pause >nul
)

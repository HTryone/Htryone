@echo off
chcp 65001 >nul
cd /d "%~dp0.."
python scripts\watch-dark-mode.py
pause

@echo off
cd /d "%~dp0"
python run_hmi.py
if errorlevel 1 py run_hmi.py
pause

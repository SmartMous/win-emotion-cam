@echo off
cd /d "%~dp0"

set PYTHONIOENCODING=utf-8

".\python\python.exe" -X utf8 main.py
pause

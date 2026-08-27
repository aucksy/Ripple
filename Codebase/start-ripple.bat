@echo off
REM Starts Ripple. Double-click this file.
REM It opens a black window and then your browser. Leave the black window
REM open while you use Ripple; closing it is how you stop Ripple.

setlocal
cd /d "%~dp0"

REM Use the project's own Python if there is one, otherwise the machine's.
set "PY="
if exist ".venv\Scripts\python.exe" set "PY=.venv\Scripts\python.exe"
if defined PY goto run

where python >nul 2>nul
if %errorlevel%==0 set "PY=python"
if defined PY goto run

where py >nul 2>nul
if %errorlevel%==0 set "PY=py"
if defined PY goto run

echo.
echo Python is not on this machine, so Ripple cannot start.
echo Install Python 3.10 or newer, then double-click this file again.
echo.
pause
exit /b 1

:run
echo Starting Ripple. It prints the address to open, and opens your browser.
echo Leave this window open. Closing it stops Ripple.
echo.
"%PY%" run.py
if errorlevel 1 pause

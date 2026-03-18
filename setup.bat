@echo off
REM setup.bat — install deps and register buddy command on Windows
REM Run this once from the ascii_play folder

echo Installing Python dependencies...
pip install numpy imageio imageio-ffmpeg

echo.
echo Done! To use buddy from anywhere, add this folder to your PATH:
echo   1. Press Win+R, type: sysdm.cpl
echo   2. Advanced tab → Environment Variables
echo   3. Under "User variables", find PATH and click Edit
echo   4. Click New and paste: %~dp0
echo   5. Click OK, restart your terminal
echo.
echo Or run it directly right now:
echo   python ascii_play\cli.py video.mp4
echo   buddy.bat video.mp4
echo.
pause

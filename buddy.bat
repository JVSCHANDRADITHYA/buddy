@echo off
REM buddy.bat — terminal video player (Windows)
REM Usage: buddy video.mp4 [options]
REM
REM Setup (run once as admin, or add folder to PATH):
REM   setx PATH "%PATH%;G:\ascii_play"
REM Then restart your terminal and run: buddy video.mp4
REM If this does not work use python manual method

python "%~dp0ascii_play\cli.py" %*

@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\setup.ps1"
pause
REM cmd reads this file while it runs, and the git pull in setup.ps1 may
REM replace it mid-run. Existing lines must therefore stay unchanged; add
REM new lines only at the end.

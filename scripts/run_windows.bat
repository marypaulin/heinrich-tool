@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM Jump to project root (parent of this scripts/ folder)
cd /d "%~dp0\.."

REM Must match $appPort in setup.ps1
set PORT=8502
set URL=http://localhost:%PORT%

REM If app already running, just open browser
powershell -NoProfile -Command ^
  "$p=%PORT%; if ((Test-NetConnection -ComputerName '127.0.0.1' -Port $p).TcpTestSucceeded) { exit 0 } else { exit 1 }" >nul 2>&1
if %errorlevel%==0 (
  start "" "%URL%"
  exit /b 0
)

REM Bring the environment in line with uv.lock (creates it on first run,
REM fast once it matches; uv also fetches the pinned Python if missing)
uv sync --quiet

REM Start Streamlit detached + quiet (so this .bat can finish)
start "" /b cmd /c uv run streamlit run src/heinrich_tool/app.py --server.port %PORT% --server.headless true --browser.gatherUsageStats false ^>nul 2^>nul

REM Wait until the port is listening (at most 20 checks)
set /a ATTEMPTS=0

:wait
set /a ATTEMPTS+=1
REM Open the browser anyway after the last check: app_windows.vbs runs this
REM file hidden, so an error message or a pause would go unseen
if %ATTEMPTS% GTR 20 goto :open
powershell -NoProfile -Command ^
  "$p=%PORT%; if ((Test-NetConnection -ComputerName '127.0.0.1' -Port $p).TcpTestSucceeded) { exit 0 } else { exit 1 }" >nul 2>&1
if %errorlevel%==0 goto :open
timeout /t 1 /nobreak >nul
goto :wait

:open
start "" "%URL%"

endlocal

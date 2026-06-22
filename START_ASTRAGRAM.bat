@echo off
setlocal EnableDelayedExpansion
title ASTRAgram - Live Server
color 0A
cls

:: Prevent QuickEdit mode from freezing the console (prevents "sleeping" when user clicks)
reg add HKCU\Console /v QuickEdit /t REG_DWORD /d 0 /f >nul 2>&1

:: CONFIG
set "ROOT=%~dp0"
set "BACKEND=%ROOT%backend-java"
set "JAR=%BACKEND%\build\libs\backend-java-0.0.1-SNAPSHOT.jar"
set "VENV_PYTHON=%BACKEND%\venv\Scripts\python.exe"
set "PORT=8080"
set "QUIZ_MODEL=llama3.1"

:BOOT
cls
echo.
echo  ==============================================
echo    ASTRAGRAM  --  The Learning OS
echo  ==============================================
echo.
echo  Starting services...
echo.

:: STEP 1 : Find an available port starting from 8080
echo  [1/4]  Finding an available port...
:CHECK_PORT
netstat -aon 2>nul | findstr ":%PORT% " >nul
if %errorlevel%==0 (
    set /a PORT+=1
    goto :CHECK_PORT
)
echo         OK - port %PORT% is free.
echo.

:: STEP 2 : Check Python venv
echo  [2/4]  Checking Python virtual environment...
if not exist "%VENV_PYTHON%" (
    echo.
    echo  ERROR: Python venv not found.
    echo  Path checked: %VENV_PYTHON%
    echo.
    echo  To fix, open a terminal and run:
    echo    cd backend-java
    echo    python -m venv venv
    echo    venv\Scripts\pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)
echo         OK - Python venv found.
echo.

:: STEP 3 : Start Ollama  (required for quizzes)
echo  [3/4]  Starting Ollama AI engine...
taskkill /IM ollama.exe /F >nul 2>&1
ping 127.0.0.1 -n 2 >nul

:: Find Ollama ??? check PATH first, then common install folders
set "OLLAMA_EXE="
where ollama >nul 2>&1
if %errorlevel%==0 (
    set "OLLAMA_EXE=ollama"
    goto :OLLAMA_FOUND
)
if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" (
    set "OLLAMA_EXE=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
    goto :OLLAMA_FOUND
)
if exist "C:\Program Files\Ollama\ollama.exe" (
    set "OLLAMA_EXE=C:\Program Files\Ollama\ollama.exe"
    goto :OLLAMA_FOUND
)

:: Not found
echo         WARNING: Ollama not found.
echo         Quizzes will not work without Ollama + %QUIZ_MODEL%.
echo         Download: https://ollama.com/download
ping 127.0.0.1 -n 4 >nul
goto :START_SERVER

:OLLAMA_FOUND
start /B /MIN "" cmd /c "set OLLAMA_NUM_PARALLEL=4 && "%OLLAMA_EXE%" serve" ^> "%TEMP%\ollama.log" 2^>^&1
ping 127.0.0.1 -n 5 >nul
echo         Ollama running.

:: Pull llama3.1 if missing
"%OLLAMA_EXE%" list 2>nul | findstr /i "llama3.1" >nul 2>&1
if %errorlevel%==0 (
    echo         %QUIZ_MODEL% ready.
) else (
    echo         Pulling %QUIZ_MODEL% model (one-time, may take a few minutes^)...
    "%OLLAMA_EXE%" pull %QUIZ_MODEL%
    if %errorlevel%==0 (
        echo         %QUIZ_MODEL% downloaded.
    ) else (
        echo         Pull failed - check internet. Quizzes may not work.
    )
)
echo.

:: STEP 4 : Launch the server
:START_SERVER
echo  [4/4]  Launching ASTRAgram server on port %PORT%...
echo.

if not exist "%JAR%" (
    echo  ERROR: JAR not found.
    echo  Path: %JAR%
    echo  Fix: cd backend-java ^& gradlew.bat bootJar
    echo.
    pause
    exit /b 1
)

:: Resolve Java ??? try the known JDK first, fall back to PATH
set "JAVA=%PROGRAMFILES%\Eclipse Adoptium\jdk-26.0.1.8-hotspot\bin\java.exe"
if not exist "%JAVA%" set "JAVA=java"

echo  Using Java : %JAVA%
echo  JAR file   : %JAR%
echo.
echo  ==============================================
echo.
echo    YOUR LIVE SERVER IS:
echo.
echo    http://localhost:%PORT%
echo.
echo    Copy and paste the link above into your
echo    browser.
echo.
echo    Keep this window open  --  closing it
echo    will stop the server.
echo.
echo  ==============================================
echo.

:: Browser auto-opener removed

:: Start the server
cd /d "%BACKEND%"
"%JAVA%" -Dserver.port=%PORT% -jar "%JAR%"

:: Script ends when server stops
echo.
echo  Server stopped.
pause

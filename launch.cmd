@echo off
cd /d ".\"

:: Set log level to DEBUG globally (this will affect the whole session)
setx LOG_LEVEL DEBUG

:: Run the Python script and capture any errors
python main.py
if %ERRORLEVEL% neq 0 (
    echo The application has crashed. Press any key to exit...
    pause
) else (
    exit
)

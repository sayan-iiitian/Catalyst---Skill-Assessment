@echo off
REM Catalyst Application Startup Script for Windows

cls
echo ==================================================
echo.   Catalyst - Skill Assessment ^& Learning Plan
echo ==================================================
echo.

REM Check if venv exists
if not exist "venv\" (
    echo [INFO] Virtual environment not found. Creating one...
    python -m venv venv
)

REM Activate venv
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing dependencies...
    pip install -r requirements.txt
)

REM Check .env file
if not exist ".env" (
    echo [INFO] Creating .env file from template...
    copy .env.example .env
    echo [WARNING] Using MOCK LLM (no API key needed^)
    echo [INFO] To use HuggingFace API, edit .env and add your token
)

echo.
echo ==================================================
echo.   Starting Catalyst Application...
echo ==================================================
echo.
echo Application will open at: http://localhost:8501
echo.
echo To stop: Press Ctrl+C
echo.

REM Run Streamlit
streamlit run app.py --logger.level=info

pause

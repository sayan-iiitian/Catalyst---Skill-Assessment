#!/bin/bash
# Catalyst Application Startup Script

echo "=================================================="
echo "  Catalyst - Skill Assessment & Learning Plan"
echo "=================================================="
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "[INFO] Virtual environment not found. Creating one..."
    python -m venv venv
fi

# Activate venv
echo "[INFO] Activating virtual environment..."
source venv/Scripts/activate

# Check if dependencies are installed
if ! python -c "import streamlit" 2>/dev/null; then
    echo "[INFO] Installing dependencies..."
    pip install -r requirements.txt
fi

# Check .env file
if [ ! -f ".env" ]; then
    echo "[INFO] Creating .env file from template..."
    cp .env.example .env
    echo "[WARNING] Using MOCK LLM (no API key needed)"
    echo "[INFO] To use HuggingFace API, edit .env and add your token"
fi

echo ""
echo "=================================================="
echo "  Starting Catalyst Application..."
echo "=================================================="
echo ""
echo "Application will open at: http://localhost:8501"
echo ""
echo "To stop: Press Ctrl+C"
echo ""

# Run Streamlit
streamlit run app.py --logger.level=info

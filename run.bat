@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
) else (
    echo Python virtual environment not found. Create it with: python -m venv .venv
)
streamlit run app/main.py

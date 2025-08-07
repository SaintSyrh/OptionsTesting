@echo off
echo Installing required packages...
pip install -r requirements.txt

echo.
echo Starting Options Pricing Calculator...
echo.
echo Open your browser and go to: http://localhost:8501
echo.
echo Press Ctrl+C to stop the application
echo.

streamlit run streamlit_app.py
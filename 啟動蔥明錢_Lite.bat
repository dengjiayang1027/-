@echo off
cd /d "%~dp0"

echo ==============================
echo   CongMingQian Auto Update
echo ==============================
echo.
echo Checking for updates...

git pull origin main

echo.
echo Starting CongMingQian...
echo.

start "" http://localhost:8501
python -m streamlit run app.py --server.headless true --browser.gatherUsageStats false

pause
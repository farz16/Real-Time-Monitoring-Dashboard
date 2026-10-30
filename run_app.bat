@echo off
title Kumbh-Drishti AI - Crowd Safety Command Center
echo ========================================================
echo   Launching Kumbh-Drishti AI Command Center
echo   AI Research League 2.0 (IMRD Shirpur) & MCA-521
echo ========================================================
echo.
echo Checking & installing required libraries...
pip install -r requirements.txt
echo.
echo Starting Streamlit Web App...
streamlit run app.py
pause

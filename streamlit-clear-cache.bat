@echo off
cd /d "%~dp0"
call venv\Scripts\activate
streamlit cache clear
streamlit run app_main.py --server.runOnSave true
pause
@echo off
taskkill /F /IM python.exe 2>nul
timeout /t 2
cd /d "e:\Project\Fraud Escalate\backend"
start python -m uvicorn main:app --host 0.0.0.0 --port 8000
timeout /t 5
echo Backend restarted

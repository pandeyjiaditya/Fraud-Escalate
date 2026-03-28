#!/bin/bash
cd "e:\Project\Fraud Escalate\backend"
pkill -f "uvicorn" 2>/dev/null
sleep 2
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > ../backend_new.log 2>&1 &
sleep 3
curl -s http://localhost:8000/health

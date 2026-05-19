#!/bin/bash
# Awash Bank Issue Tracker — High-Performance DevOps Startup for Unix/Linux
# Clears port conflicts, seeds database, and boots uvicorn on 127.0.0.1.

echo -e "\033[1;36m==============================================\033[0m"
echo -e "\033[1;36m  Awash Bank Issue Tracker Auto-DevOps Startup \033[0m"
echo -e "\033[1;36m==============================================\033[0m"

# 1. Terminate Port Conflicts
echo -e "\033[1;33m[1/3] Clearing port 8000 conflicts...\033[0m"
PORT_PID=$(lsof -t -i:8000)
if [ ! -z "$PORT_PID" ]; then
    echo "Killing conflicting process ID $PORT_PID bound to port 8000..."
    kill -9 $PORT_PID
    sleep 2
fi

# 2. Seed Database
echo -e "\033[1;33m[2/3] Seeding the database...\033[0m"
cd backend
python3 -m app.seed
cd ..

# 3. Start Uvicorn Server
echo -e "\033[1;33m[3/3] Starting FastAPI Uvicorn on http://127.0.0.1:8000 ...\033[0m"
cd backend
python3 -m uvicorn main:app --host 127.0.0.1 --port 8000

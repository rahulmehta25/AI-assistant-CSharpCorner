#!/bin/bash

echo "Starting AI Career Assistant Platform..."
echo "======================================="

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install/update Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt -q

# Start the API Bridge in background
echo "Starting API Bridge on http://localhost:8000..."
python api_bridge.py &
API_PID=$!

# Wait for API to start
sleep 3

# Navigate to frontend and install dependencies
echo "Setting up frontend..."
cd frontend
npm install

# Start frontend development server
echo "Starting frontend on http://localhost:5173..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "======================================="
echo "Platform is running!"
echo "- API Bridge: http://localhost:8000"
echo "- Frontend: http://localhost:5173"
echo "- API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo "======================================="

# Wait for Ctrl+C
trap "echo 'Stopping services...'; kill $API_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
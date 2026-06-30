#!/bin/bash
# Food Truth Teller - Start both backend and frontend
# Usage: ./start.sh

set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$REPO_DIR/backend"
FRONTEND_DIR="$REPO_DIR/frontend"
ML_DIR="$REPO_DIR/ml"

echo "🌿 Food Truth Teller - Startup Script"
echo "======================================="

# 1. Install backend dependencies
echo ""
echo "📦 Installing backend dependencies..."
pip install flask flask-cors requests scikit-learn numpy joblib python-dotenv -q --ignore-installed blinker 2>/dev/null || true

# 2. Train ML model if not exists
MODEL_PATH="$ML_DIR/models/health_model.pkl"
if [ ! -f "$MODEL_PATH" ]; then
  echo ""
  echo "🤖 Training ML model..."
  cd "$ML_DIR" && python train_simple.py
fi

# 3. Start backend
echo ""
echo "🚀 Starting Flask backend on http://localhost:5000 ..."
cd "$BACKEND_DIR"
FLASK_DEBUG=true python app.py &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# 4. Install frontend deps if needed
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
  echo ""
  echo "📦 Installing frontend dependencies..."
  cd "$FRONTEND_DIR" && npm install --legacy-peer-deps
fi

# 5. Start frontend
echo ""
echo "🖥️  Starting Vite frontend on http://localhost:5173 ..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Backend:  http://localhost:5000/api/health"
echo "  ✅ Frontend: http://localhost:5173"
echo ""
echo "  📱 Mobile testing (ngrok):"
echo "     ngrok http 5173"
echo "     Then access the https:// URL on your phone"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$FRONTEND_DIR"
npm run dev

# Cleanup on exit
trap "kill $BACKEND_PID 2>/dev/null; echo 'Servers stopped.'" EXIT

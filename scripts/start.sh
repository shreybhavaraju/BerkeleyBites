#!/bin/bash

# BerkeleyBites Platform Startup Script
# Starts both the FastAPI backend and React frontend

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the project root directory (parent of scripts folder)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# PID file locations
PID_DIR="$PROJECT_ROOT/scripts/.pids"
BACKEND_PID_FILE="$PID_DIR/backend.pid"
FRONTEND_PID_FILE="$PID_DIR/frontend.pid"

# Create PID directory if it doesn't exist
mkdir -p "$PID_DIR"

# Log file locations
LOG_DIR="$PROJECT_ROOT/scripts/logs"
mkdir -p "$LOG_DIR"
BACKEND_LOG="$LOG_DIR/backend.log"
FRONTEND_LOG="$LOG_DIR/frontend.log"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   BerkeleyBites Platform Startup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if already running
if [ -f "$BACKEND_PID_FILE" ] && kill -0 $(cat "$BACKEND_PID_FILE") 2>/dev/null; then
    echo -e "${YELLOW}Warning: Backend already running (PID: $(cat $BACKEND_PID_FILE))${NC}"
    echo -e "${YELLOW}Run ./stop.sh first to restart${NC}"
    BACKEND_RUNNING=true
else
    BACKEND_RUNNING=false
fi

if [ -f "$FRONTEND_PID_FILE" ] && kill -0 $(cat "$FRONTEND_PID_FILE") 2>/dev/null; then
    echo -e "${YELLOW}Warning: Frontend already running (PID: $(cat $FRONTEND_PID_FILE))${NC}"
    echo -e "${YELLOW}Run ./stop.sh first to restart${NC}"
    FRONTEND_RUNNING=true
else
    FRONTEND_RUNNING=false
fi

# Start Backend
if [ "$BACKEND_RUNNING" = false ]; then
    echo -e "${BLUE}[1/2] Starting Backend (FastAPI)...${NC}"

    cd "$PROJECT_ROOT"

    # Check for virtual environment
    if [ -d "venv" ]; then
        source venv/bin/activate
        echo -e "  ${GREEN}✓${NC} Virtual environment activated"
    elif [ -d ".venv" ]; then
        source .venv/bin/activate
        echo -e "  ${GREEN}✓${NC} Virtual environment activated"
    else
        echo -e "  ${YELLOW}!${NC} No virtual environment found, using system Python"
    fi

    # Check for .env file
    if [ -f ".env" ]; then
        echo -e "  ${GREEN}✓${NC} Environment file found"
    else
        echo -e "  ${YELLOW}!${NC} No .env file found - API keys may be missing"
    fi

    # Start uvicorn in background
    nohup python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload > "$BACKEND_LOG" 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > "$BACKEND_PID_FILE"

    # Wait a moment and check if it started
    sleep 2
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} Backend started (PID: $BACKEND_PID)"
        echo -e "  ${GREEN}✓${NC} API available at: http://localhost:8000"
        echo -e "  ${GREEN}✓${NC} API docs at: http://localhost:8000/docs"
    else
        echo -e "  ${RED}✗${NC} Backend failed to start. Check $BACKEND_LOG"
        rm -f "$BACKEND_PID_FILE"
    fi
else
    echo -e "${BLUE}[1/2] Backend already running, skipping...${NC}"
fi

echo ""

# Start Frontend
if [ "$FRONTEND_RUNNING" = false ]; then
    echo -e "${BLUE}[2/2] Starting Frontend (React + Vite)...${NC}"

    cd "$PROJECT_ROOT/frontend"

    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo -e "  ${YELLOW}!${NC} node_modules not found, installing dependencies..."
        npm install
    fi

    # Start Vite dev server in background
    nohup npm run dev > "$FRONTEND_LOG" 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$FRONTEND_PID_FILE"

    # Wait a moment and check if it started
    sleep 3
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} Frontend started (PID: $FRONTEND_PID)"
        echo -e "  ${GREEN}✓${NC} App available at: http://localhost:5173"
    else
        echo -e "  ${RED}✗${NC} Frontend failed to start. Check $FRONTEND_LOG"
        rm -f "$FRONTEND_PID_FILE"
    fi
else
    echo -e "${BLUE}[2/2] Frontend already running, skipping...${NC}"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}   BerkeleyBites is ready!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "  Frontend:  ${GREEN}http://localhost:5173${NC}"
echo -e "  Backend:   ${GREEN}http://localhost:8000${NC}"
echo -e "  API Docs:  ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo -e "  Logs:"
echo -e "    Backend:  $BACKEND_LOG"
echo -e "    Frontend: $FRONTEND_LOG"
echo ""
echo -e "  To stop: ${YELLOW}./scripts/stop.sh${NC}"
echo ""

#!/bin/bash

# BerkeleyBites Platform Status Script
# Checks the status of backend and frontend services

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# PID file locations
PID_DIR="$PROJECT_ROOT/scripts/.pids"
BACKEND_PID_FILE="$PID_DIR/backend.pid"
FRONTEND_PID_FILE="$PID_DIR/frontend.pid"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   BerkeleyBites Platform Status${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check Backend
echo -e "${BLUE}Backend (FastAPI):${NC}"
if [ -f "$BACKEND_PID_FILE" ]; then
    BACKEND_PID=$(cat "$BACKEND_PID_FILE")
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "  Status: ${GREEN}Running${NC} (PID: $BACKEND_PID)"
        echo -e "  URL:    http://localhost:8000"

        # Check if API is responding
        if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/health | grep -q "200"; then
            echo -e "  Health: ${GREEN}Healthy${NC}"
        else
            echo -e "  Health: ${YELLOW}Not responding${NC}"
        fi
    else
        echo -e "  Status: ${RED}Stopped${NC} (stale PID file)"
    fi
else
    # Check if something is on port 8000 anyway
    PORT_PID=$(lsof -ti:8000 2>/dev/null)
    if [ -n "$PORT_PID" ]; then
        echo -e "  Status: ${YELLOW}Running (untracked)${NC} (PID: $PORT_PID)"
        echo -e "  URL:    http://localhost:8000"
    else
        echo -e "  Status: ${RED}Stopped${NC}"
    fi
fi

echo ""

# Check Frontend
echo -e "${BLUE}Frontend (React + Vite):${NC}"
if [ -f "$FRONTEND_PID_FILE" ]; then
    FRONTEND_PID=$(cat "$FRONTEND_PID_FILE")
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "  Status: ${GREEN}Running${NC} (PID: $FRONTEND_PID)"
        echo -e "  URL:    http://localhost:5173"
    else
        echo -e "  Status: ${RED}Stopped${NC} (stale PID file)"
    fi
else
    # Check if something is on port 5173 anyway
    PORT_PID=$(lsof -ti:5173 2>/dev/null)
    if [ -n "$PORT_PID" ]; then
        echo -e "  Status: ${YELLOW}Running (untracked)${NC} (PID: $PORT_PID)"
        echo -e "  URL:    http://localhost:5173"
    else
        echo -e "  Status: ${RED}Stopped${NC}"
    fi
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "  Start:  ${YELLOW}./scripts/start.sh${NC}"
echo -e "  Stop:   ${YELLOW}./scripts/stop.sh${NC}"
echo ""

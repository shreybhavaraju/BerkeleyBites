#!/bin/bash

# BerkeleyBites Platform Shutdown Script
# Stops both the FastAPI backend and React frontend

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

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   BerkeleyBites Platform Shutdown${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to stop a process
stop_process() {
    local name=$1
    local pid_file=$2

    if [ -f "$pid_file" ]; then
        PID=$(cat "$pid_file")
        if kill -0 $PID 2>/dev/null; then
            echo -e "${BLUE}Stopping $name (PID: $PID)...${NC}"

            # Try graceful shutdown first
            kill $PID 2>/dev/null

            # Wait up to 5 seconds for graceful shutdown
            for i in {1..10}; do
                if ! kill -0 $PID 2>/dev/null; then
                    echo -e "  ${GREEN}✓${NC} $name stopped gracefully"
                    rm -f "$pid_file"
                    return 0
                fi
                sleep 0.5
            done

            # Force kill if still running
            echo -e "  ${YELLOW}!${NC} Graceful shutdown timed out, forcing..."
            kill -9 $PID 2>/dev/null
            sleep 1

            if ! kill -0 $PID 2>/dev/null; then
                echo -e "  ${GREEN}✓${NC} $name force stopped"
                rm -f "$pid_file"
                return 0
            else
                echo -e "  ${RED}✗${NC} Failed to stop $name"
                return 1
            fi
        else
            echo -e "${YELLOW}$name not running (stale PID file)${NC}"
            rm -f "$pid_file"
        fi
    else
        echo -e "${YELLOW}$name not running (no PID file)${NC}"
    fi
}

# Stop Frontend first (it depends on backend)
stop_process "Frontend" "$FRONTEND_PID_FILE"
echo ""

# Stop Backend
stop_process "Backend" "$BACKEND_PID_FILE"
echo ""

# Also kill any orphaned processes on these ports
echo -e "${BLUE}Checking for orphaned processes...${NC}"

# Check port 8000 (backend)
BACKEND_PORT_PID=$(lsof -ti:8000 2>/dev/null)
if [ -n "$BACKEND_PORT_PID" ]; then
    echo -e "  ${YELLOW}!${NC} Found process on port 8000 (PID: $BACKEND_PORT_PID), killing..."
    kill $BACKEND_PORT_PID 2>/dev/null
    sleep 1
    if ! kill -0 $BACKEND_PORT_PID 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} Orphaned backend process stopped"
    fi
fi

# Check port 5173 (frontend)
FRONTEND_PORT_PID=$(lsof -ti:5173 2>/dev/null)
if [ -n "$FRONTEND_PORT_PID" ]; then
    echo -e "  ${YELLOW}!${NC} Found process on port 5173 (PID: $FRONTEND_PORT_PID), killing..."
    kill $FRONTEND_PORT_PID 2>/dev/null
    sleep 1
    if ! kill -0 $FRONTEND_PORT_PID 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} Orphaned frontend process stopped"
    fi
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}   BerkeleyBites stopped${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "  To start again: ${YELLOW}./scripts/start.sh${NC}"
echo ""

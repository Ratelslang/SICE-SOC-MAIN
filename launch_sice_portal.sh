#!/bin/bash
# ============================================================
# SICE SOC PORTAL — LOCAL SERVER LAUNCHER
# Required because service workers (offline caching) do NOT work
# over file:// URLs. This starts a local HTTP server bound to
# 127.0.0.1 only (not exposed to your network) and opens the portal.
# ============================================================

PORTAL_DIR="/home/philip/Desktop/OPS MAIN/SOC CENTRE/SICE PORTAL HUB"
PORT=8743
URL="http://127.0.0.1:${PORT}/SICE_SOC_MAIN.html"
PIDFILE="/tmp/sice_portal_server.pid"

cd "$PORTAL_DIR" || { echo "ERROR: Portal directory not found: $PORTAL_DIR"; exit 1; }

# If a server is already running from a previous launch, reuse it.
if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    echo "Server already running (PID $(cat "$PIDFILE")). Opening browser..."
else
    echo "Starting local server on port ${PORT}..."
    # bind to 127.0.0.1 only — never accessible from the network
    nohup python3 "sice_server.py" > /tmp/sice_portal_server.log 2>&1 &
    echo $! > "$PIDFILE"
    sleep 1
fi

xdg-open "$URL"

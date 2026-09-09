#!/usr/bin/env bash
# SICE SOC Portal launcher. Runs from the folder containing this script,
# starts the local server, and opens the canonical portal route.
set -euo pipefail

PORT="${SICE_PORT:-8743}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
URL="http://127.0.0.1:${PORT}/"
PIDFILE="${TMPDIR:-/tmp}/sice_portal_server_${PORT}.pid"
LOGFILE="${TMPDIR:-/tmp}/sice_portal_server_${PORT}.log"

if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 is required to run the local SICE portal server."
    exit 1
fi

cd "$SCRIPT_DIR"

server_is_healthy() {
    curl --silent --fail --max-time 2 "${URL}health" >/dev/null 2>&1
}

if server_is_healthy; then
    echo "SICE portal server is already available on port ${PORT}."
else
    if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
        echo "A previous portal server is still starting on port ${PORT}."
    else
        echo "Starting SICE portal server on port ${PORT}..."
        nohup python3 "$SCRIPT_DIR/sice_server.py" >"$LOGFILE" 2>&1 &
        echo $! >"$PIDFILE"
    fi

    for _ in {1..10}; do
        sleep 1
        if server_is_healthy; then break; fi
    done

    if ! server_is_healthy; then
        echo "ERROR: The portal server did not start. Review ${LOGFILE}."
        exit 1
    fi
fi

echo "Opening ${URL}"
if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$URL" >/dev/null 2>&1 &
elif command -v open >/dev/null 2>&1; then
    open "$URL"
else
    echo "Open this URL in a browser: ${URL}"
fi

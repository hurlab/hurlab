#!/bin/bash
cd "$(dirname "$0")"
if [ -f .admin_server.pid ]; then
    kill $(cat .admin_server.pid) 2>/dev/null
    rm .admin_server.pid
    echo "Admin server stopped"
else
    echo "No PID file found"
fi

#!/bin/bash
cd "$(dirname "$0")"
PYTHON=/usr/bin/python3.12
nohup $PYTHON admin_server.py > admin_server.log 2>&1 &
echo "Admin server started on port 8180 (PID: $!)"
echo $! > .admin_server.pid

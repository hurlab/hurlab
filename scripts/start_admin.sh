#!/bin/bash
cd "$(dirname "$0")"
PYTHON=/usr/bin/python3.12
# Bind loopback-only. Public access goes through nginx on port 8443, which
# terminates TLS and enforces the UND-only allowlist. The Python-level
# allowlist in admin_server.py remains as defense-in-depth.
export ADMIN_BIND_ADDR=127.0.0.1
nohup $PYTHON admin_server.py > admin_server.log 2>&1 &
echo "Admin server started on port 8180 (PID: $!)"
echo $! > .admin_server.pid

#!/usr/bin/env bash
if [ -d "/run/systemd/system/" ]; then
    lsof -nP -iTCP:18789 -sTCP:LISTEN -t | xargs -r kill -9; sudo systemctl restart openclaw
else
    lsof -nP -iTCP:18789 -sTCP:LISTEN -t | xargs -r kill -9; nohup openclaw gateway run --port 18789 > /tmp/openclaw-gateway.log 2>&1 &
fi
#!/usr/bin/env bash
# Wait for the Raspberry Pi to boot, then SSH into it.
# Reconnects automatically if the Pi reboots or the connection drops.
# Usage: scripts/connect-pi.sh [host]   (default: robokerho, see ~/.ssh/config)
HOST="${1:-robokerho}"
IP="${PI_IP:-172.20.10.2}"

while true; do
    printf 'Waiting for %s (%s) to come online' "$HOST" "$IP"
    until timeout 2 bash -c "echo > /dev/tcp/$IP/22" 2>/dev/null; do
        printf '.'
        sleep 2
    done
    echo " up!"
    ssh "$HOST"
    echo "Connection closed. Press Ctrl+C to quit, or wait to reconnect..."
    sleep 3
done

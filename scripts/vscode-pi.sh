#!/usr/bin/env bash
# Wait for the Raspberry Pi to boot, then open VS Code connected to it via Remote-SSH.
# Keeps running: after the Pi goes offline and boots again, VS Code is opened again.
# Usage: scripts/vscode-pi.sh [host] [remote-folder]   (host from ~/.ssh/config)
HOST="${1:-robokerho}"
DIR="${2:-/home/robokerho}"
IP="${PI_IP:-172.20.10.2}"

pi_up() { timeout 2 bash -c "echo > /dev/tcp/$IP/22" 2>/dev/null; }

while true; do
    until pi_up; do sleep 3; done
    echo "$HOST ($IP) is up, opening VS Code"
    code --remote "ssh-remote+$HOST" "$DIR"
    while pi_up; do sleep 5; done
    echo "$HOST went offline, waiting for it to boot"
done

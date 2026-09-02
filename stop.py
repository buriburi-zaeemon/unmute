#!/usr/bin/env python3
"""
SignBridge Shutdown Script
Finds and terminates any running SignBridge server processes on the specified port.
"""

import os
import sys
import subprocess
import argparse
import re


def find_pids_on_port(port: int):
    """Finds all Process IDs listening on the given TCP port."""
    pids = set()
    if os.name == "nt":
        try:
            output = subprocess.check_output(f"netstat -ano | findstr :{port}", shell=True, text=True)
            for line in output.strip().splitlines():
                parts = re.split(r"\s+", line.strip())
                if len(parts) >= 5 and parts[1].endswith(f":{port}") and parts[3] == "LISTENING":
                    pid = int(parts[4])
                    if pid > 0:
                        pids.add(pid)
        except subprocess.CalledProcessError:
            pass
    else:
        try:
            output = subprocess.check_output(["lsof", "-t", f"-i:{port}"], text=True)
            for line in output.strip().splitlines():
                if line.strip().isdigit():
                    pids.add(int(line.strip()))
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    return list(pids)


def kill_pid(pid: int):
    """Terminates a process by its PID."""
    if os.name == "nt":
        subprocess.run(f"taskkill /F /PID {pid}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        subprocess.run(["kill", "-9", str(pid)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def main():
    parser = argparse.ArgumentParser(description="Stop SignBridge ASL Translation Server")
    parser.add_argument("--port", type=int, default=8090, help="Port to check and free (default: 8090)")
    args = parser.parse_args()

    print("=" * 55)
    print(f"[*] Checking for SignBridge server running on port {args.port}...")
    
    pids = find_pids_on_port(args.port)

    if not pids:
        print(f"[+] No active server found listening on port {args.port}.")
        print("=" * 55)
        return

    for pid in pids:
        print(f"[*] Terminating process (PID: {pid})...")
        kill_pid(pid)

    # Double check
    remaining = find_pids_on_port(args.port)
    if not remaining:
        print(f"[+] Successfully stopped server. Port {args.port} is now free.")
    else:
        print(f"[-] Warning: Some processes on port {args.port} may still be running: {remaining}")
    print("=" * 55)


if __name__ == "__main__":
    main()

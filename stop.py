#!/usr/bin/env python3
"""
Unmute Shutdown Script
Finds and terminates any running Unmute server processes on the specified port.
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
    parser = argparse.ArgumentParser(description="Stop UNMUTE Real-Time Sign Language Translation Server")
    parser.add_argument("--port", type=int, default=8000, help="Port to check and free (default: 8000)")
    parser.add_argument("--all", action="store_true", help="Check both standard ports (8000 and 8090)")
    args = parser.parse_args()

    ports_to_check = [args.port]
    if args.all or args.port in (8000, 8090):
        ports_to_check = list(dict.fromkeys([args.port, 8000, 8090]))

    print("=" * 55)
    print(f"[*] Checking for UNMUTE server instances on ports: {ports_to_check}...")
    
    found_any = False
    for port in ports_to_check:
        pids = find_pids_on_port(port)
        if pids:
            found_any = True
            for pid in pids:
                print(f"[*] Terminating UNMUTE process on port {port} (PID: {pid})...")
                kill_pid(pid)
            time.sleep(0.5)
            remaining = find_pids_on_port(port)
            if not remaining:
                print(f"[+] Successfully stopped server on port {port}.")
            else:
                print(f"[-] Warning: Some processes on port {port} may still be running: {remaining}")

    if not found_any:
        print("[+] No active UNMUTE server processes found.")

    print("=" * 55)


if __name__ == "__main__":
    main()

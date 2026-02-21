"""Startup script for the Crypto Dashboard."""
import subprocess
import sys
import os
import time
import signal
from pathlib import Path

# ANSI colors
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

def print_header():
    """Print startup header."""
    print(f"""
{CYAN}============================================================
           Crypto Market Dashboard v2.0
           Macro -> Crypto -> Sector -> Action
============================================================{RESET}
""")

def start_backend():
    """Start the FastAPI backend."""
    print(f"{YELLOW}>>> Starting backend server...{RESET}")
    backend_path = Path(__file__).parent / "backend"
    
    proc = subprocess.Popen(
        [sys.executable, "main.py"],
        cwd=backend_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1,
        encoding='utf-8',
        errors='replace'
    )
    return proc

def start_frontend():
    """Start the React frontend."""
    print(f"{YELLOW}>>> Starting frontend development server...{RESET}")
    frontend_path = Path(__file__).parent / "frontend"
    
    # Use shell=True on Windows for npm
    use_shell = os.name == 'nt'
    cmd = "npm run dev" if use_shell else ["npm", "run", "dev"]
    
    proc = subprocess.Popen(
        cmd,
        cwd=frontend_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1,
        shell=use_shell,
        encoding='utf-8',
        errors='replace'
    )
    return proc

def print_urls():
    """Print access URLs."""
    time.sleep(3)  # Wait for servers to start
    print(f"""
{GREEN}=== Dashboard is running! ==={RESET}

{CYAN}Access URLs:{RESET}
  Dashboard:  http://localhost:3000
  API Docs:   http://localhost:8000/docs
  Health:     http://localhost:8000/api/health

{CYAN}Press Ctrl+C to stop{RESET}
""")

def main():
    """Main entry point."""
    print_header()
    
    # Check if npm is available
    npm_cmd = "npm"
    if os.name == 'nt':  # Windows
        npm_cmd = "npm.cmd"
    
    try:
        subprocess.run([npm_cmd, "--version"], capture_output=True, check=True, shell=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"{RED}ERROR: npm not found. Please install Node.js first.{RESET}")
        sys.exit(1)
    
    # Set UTF-8 encoding for Windows
    if os.name == 'nt':
        os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # Start backend
    backend_proc = start_backend()
    
    # Start frontend
    frontend_proc = start_frontend()
    
    # Print URLs
    print_urls()
    
    def signal_handler(sig, frame):
        print(f"\n{YELLOW}>>> Shutting down...{RESET}")
        backend_proc.terminate()
        frontend_proc.terminate()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Monitor processes
        while True:
            backend_line = backend_proc.stdout.readline()
            if backend_line:
                print(f"[{CYAN}BACKEND{RESET}] {backend_line.strip()}")
            
            frontend_line = frontend_proc.stdout.readline()
            if frontend_line:
                print(f"[{GREEN}FRONTEND{RESET}] {frontend_line.strip()}")
            
            # Check if processes are still running
            if backend_proc.poll() is not None and frontend_proc.poll() is not None:
                break
            
            time.sleep(0.1)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()

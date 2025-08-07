#!/usr/bin/env python3
"""
Options Pricing Calculator - Launcher
This script starts the Streamlit app and opens it in the browser.
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path
import socket
import threading

def print_header():
    """Print launcher header"""
    print("=" * 60)
    print("    OPTIONS PRICING CALCULATOR - LAUNCHER")
    print("=" * 60)
    print()

def check_dependencies():
    """Check if required packages are installed"""
    print("Checking dependencies...")
    
    packages = [
        ("streamlit", "streamlit"),
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("matplotlib", "matplotlib.pyplot"),
        ("scipy", "scipy")
    ]
    
    missing_packages = []
    for package_name, import_name in packages:
        try:
            __import__(import_name)
            print(f"✓ {package_name}")
        except ImportError:
            print(f"✗ {package_name} - MISSING")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\n⚠ Missing packages: {', '.join(missing_packages)}")
        print("Please run the installer first (installer.exe)")
        return False
    
    print("✓ All dependencies found")
    return True

def check_app_files():
    """Check if required application files exist"""
    print("\nChecking application files...")
    
    required_files = [
        "streamlit_app.py",
        "option_pricing.py",
        "requirements.txt"
    ]
    
    missing_files = []
    for file_name in required_files:
        if Path(file_name).exists():
            print(f"✓ {file_name}")
        else:
            print(f"✗ {file_name} - MISSING")
            missing_files.append(file_name)
    
    if missing_files:
        print(f"\n⚠ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✓ All application files found")
    return True

def find_available_port(start_port=8501):
    """Find an available port starting from start_port"""
    port = start_port
    while port < start_port + 100:  # Try 100 ports
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            port += 1
    return None

def wait_for_server(port, timeout=30):
    """Wait for the Streamlit server to start"""
    print(f"Waiting for server to start on port {port}...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                if result == 0:
                    print("✓ Server is ready!")
                    return True
        except:
            pass
        
        print(".", end="", flush=True)
        time.sleep(1)
    
    print("\n⚠ Timeout waiting for server")
    return False

def open_browser(port):
    """Open the browser to the Streamlit app"""
    url = f"http://localhost:{port}"
    print(f"\nOpening browser to: {url}")
    
    try:
        webbrowser.open(url)
        print("✓ Browser opened")
        return True
    except Exception as e:
        print(f"⚠ Could not open browser automatically: {e}")
        print(f"Please manually open: {url}")
        return False

def run_streamlit(port):
    """Run the Streamlit application"""
    print(f"\nStarting Streamlit server on port {port}...")
    
    try:
        # Run streamlit with specific port
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", str(port),
            "--server.headless", "true",
            "--server.fileWatcherType", "none"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        print(f"✓ Streamlit server started (PID: {process.pid})")
        return process
        
    except Exception as e:
        print(f"✗ Failed to start Streamlit: {e}")
        return None

def main():
    """Main launcher function"""
    print_header()
    
    # Check dependencies
    if not check_dependencies():
        print("\n✗ LAUNCH FAILED: Missing dependencies")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Check application files
    if not check_app_files():
        print("\n✗ LAUNCH FAILED: Missing application files")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Find available port
    port = find_available_port()
    if port is None:
        print("\n✗ LAUNCH FAILED: No available ports")
        input("Press Enter to exit...")
        sys.exit(1)
    
    print(f"\n✓ Using port: {port}")
    
    # Start Streamlit server
    process = run_streamlit(port)
    if process is None:
        print("\n✗ LAUNCH FAILED: Could not start server")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Wait for server to be ready
    if wait_for_server(port):
        # Open browser
        open_browser(port)
        
        print("\n" + "=" * 60)
        print("    OPTIONS PRICING CALCULATOR IS RUNNING!")
        print("=" * 60)
        print(f"Server: http://localhost:{port}")
        print("Press Ctrl+C or close this window to stop the server.")
        print("=" * 60)
        
        try:
            # Keep the process running and display output
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
                
                # Also check for errors
                if process.stderr.readable():
                    error = process.stderr.readline()
                    if error:
                        print(f"ERROR: {error.strip()}")
        
        except KeyboardInterrupt:
            print("\n\nShutting down server...")
            process.terminate()
            process.wait()
            print("✓ Server stopped")
    
    else:
        print("\n⚠ Server may not have started correctly")
        print("Please check the console for errors")
        process.terminate()
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
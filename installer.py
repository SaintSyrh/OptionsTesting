#!/usr/bin/env python3
"""
Options Pricing Calculator - Installer
This script installs all required dependencies for the Options Pricing Calculator.
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def print_header():
    """Print installer header"""
    print("=" * 60)
    print("    OPTIONS PRICING CALCULATOR - INSTALLER")
    print("=" * 60)
    print("This installer will set up all required dependencies.")
    print()

def check_python():
    """Check if Python is installed and get version"""
    print("Checking Python installation...")
    try:
        version = sys.version_info
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} found")
        
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print("⚠ WARNING: Python 3.8 or higher recommended")
        return True
    except Exception as e:
        print(f"✗ Python check failed: {e}")
        return False

def check_pip():
    """Check if pip is available"""
    print("Checking pip installation...")
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✓ pip is available")
            return True
        else:
            print("✗ pip not found")
            return False
    except Exception as e:
        print(f"✗ pip check failed: {e}")
        return False

def install_requirements():
    """Install required packages"""
    print("\nInstalling required packages...")
    
    # Check if requirements.txt exists
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("✗ requirements.txt not found")
        return False
    
    try:
        # Upgrade pip first
        print("Upgrading pip...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, timeout=120)
        print("✓ pip upgraded")
        
        # Install requirements
        print("Installing packages from requirements.txt...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✓ All packages installed successfully")
            return True
        else:
            print(f"✗ Installation failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ Installation timed out")
        return False
    except Exception as e:
        print(f"✗ Installation failed: {e}")
        return False

def verify_installation():
    """Verify that all packages can be imported"""
    print("\nVerifying installation...")
    
    packages = [
        ("streamlit", "streamlit"),
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("matplotlib", "matplotlib.pyplot"),
        ("scipy", "scipy")
    ]
    
    all_good = True
    for package_name, import_name in packages:
        try:
            __import__(import_name)
            print(f"✓ {package_name}")
        except ImportError:
            print(f"✗ {package_name} - FAILED")
            all_good = False
    
    return all_good

def create_desktop_shortcut():
    """Create desktop shortcut (Windows only)"""
    if sys.platform == "win32":
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            path = os.path.join(desktop, "Options Pricing Calculator.lnk")
            target = os.path.join(os.getcwd(), "launcher.exe")
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = target
            shortcut.WorkingDirectory = os.getcwd()
            shortcut.IconLocation = target
            shortcut.save()
            
            print("✓ Desktop shortcut created")
            return True
        except ImportError:
            print("⚠ Could not create desktop shortcut (winshell not available)")
            return False
        except Exception as e:
            print(f"⚠ Could not create desktop shortcut: {e}")
            return False
    else:
        print("⚠ Desktop shortcuts only supported on Windows")
        return False

def main():
    """Main installer function"""
    print_header()
    
    # Check system requirements
    if not check_python():
        print("\n✗ INSTALLATION FAILED: Python not found")
        input("Press Enter to exit...")
        sys.exit(1)
    
    if not check_pip():
        print("\n✗ INSTALLATION FAILED: pip not found")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Install packages
    if not install_requirements():
        print("\n✗ INSTALLATION FAILED: Could not install packages")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Verify installation
    if not verify_installation():
        print("\n⚠ INSTALLATION WARNING: Some packages may not be working correctly")
        choice = input("Continue anyway? (y/N): ").lower()
        if choice not in ['y', 'yes']:
            sys.exit(1)
    
    # Try to create desktop shortcut
    create_desktop_shortcut()
    
    print("\n" + "=" * 60)
    print("    INSTALLATION COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("You can now run the Options Pricing Calculator using:")
    print("1. Double-click 'launcher.exe' (if available)")
    print("2. Run 'run_streamlit.bat'")
    print("3. Use command: streamlit run streamlit_app.py")
    print()
    print("The application will open in your default web browser.")
    print("=" * 60)
    
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
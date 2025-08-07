#!/usr/bin/env python3
"""
Build script to create Windows executables for the Options Pricing Calculator
This script uses PyInstaller to create standalone .exe files
"""

import subprocess
import sys
import os
from pathlib import Path
import shutil

def print_header():
    """Print build script header"""
    print("=" * 60)
    print("    EXECUTABLE BUILDER")
    print("=" * 60)
    print("Building Windows executables for Options Pricing Calculator...")
    print()

def check_pyinstaller():
    """Check if PyInstaller is installed, install if not"""
    print("Checking PyInstaller...")
    try:
        import PyInstaller
        print("✓ PyInstaller found")
        return True
    except ImportError:
        print("PyInstaller not found, installing...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                          check=True, timeout=120)
            print("✓ PyInstaller installed")
            return True
        except Exception as e:
            print(f"✗ Failed to install PyInstaller: {e}")
            return False

def build_installer_exe():
    """Build installer.exe"""
    print("\nBuilding installer.exe...")
    
    try:
        cmd = [
            "pyinstaller",
            "--onefile",
            "--console",
            "--name=installer",
            "--distpath=.",
            "--workpath=build_temp",
            "--specpath=build_temp",
            "installer.py"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✓ installer.exe built successfully")
            return True
        else:
            print(f"✗ Failed to build installer.exe: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Failed to build installer.exe: {e}")
        return False

def build_launcher_exe():
    """Build launcher.exe"""
    print("\nBuilding launcher.exe...")
    
    try:
        cmd = [
            "pyinstaller",
            "--onefile",
            "--console",
            "--name=launcher",
            "--distpath=.",
            "--workpath=build_temp",
            "--specpath=build_temp",
            "launcher.py"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✓ launcher.exe built successfully")
            return True
        else:
            print(f"✗ Failed to build launcher.exe: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Failed to build launcher.exe: {e}")
        return False

def cleanup_build_files():
    """Clean up temporary build files"""
    print("\nCleaning up build files...")
    
    try:
        build_dirs = ["build_temp", "__pycache__"]
        for dir_name in build_dirs:
            if Path(dir_name).exists():
                shutil.rmtree(dir_name)
                print(f"✓ Removed {dir_name}")
        
        # Remove .spec files
        spec_files = Path(".").glob("*.spec")
        for spec_file in spec_files:
            if spec_file.name not in ["installer.spec", "launcher.spec"]:
                spec_file.unlink()
                print(f"✓ Removed {spec_file.name}")
        
    except Exception as e:
        print(f"⚠ Cleanup warning: {e}")

def create_readme():
    """Create a README file for the executables"""
    readme_content = """# Options Pricing Calculator - Executables

## Quick Start

1. **First Time Setup**: Double-click `installer.exe`
   - This will install all required Python packages
   - Only needs to be run once

2. **Launch Application**: Double-click `launcher.exe`
   - This will start the application and open it in your browser
   - Use this every time you want to run the calculator

## Files

- `installer.exe` - One-time setup installer
- `launcher.exe` - Application launcher
- `streamlit_app.py` - Main application file
- `option_pricing.py` - Options pricing calculations
- `requirements.txt` - Python package requirements

## Troubleshooting

If you encounter issues:

1. Make sure Python 3.8+ is installed on your system
2. Run `installer.exe` first if you haven't already
3. Check that all application files are in the same folder
4. Try running `run_streamlit.bat` as an alternative

## Manual Installation (Alternative)

If the executables don't work, you can install manually:

```batch
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Support

For issues or questions, check that all required files are present:
- streamlit_app.py
- option_pricing.py
- requirements.txt
- installer.exe
- launcher.exe
"""
    
    try:
        with open("README_Executables.txt", "w", encoding="utf-8") as f:
            f.write(readme_content)
        print("✓ Created README_Executables.txt")
    except Exception as e:
        print(f"⚠ Could not create README: {e}")

def main():
    """Main build function"""
    print_header()
    
    # Check PyInstaller
    if not check_pyinstaller():
        print("\n✗ BUILD FAILED: Could not install PyInstaller")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Build executables
    installer_ok = build_installer_exe()
    launcher_ok = build_launcher_exe()
    
    # Clean up
    cleanup_build_files()
    
    # Create documentation
    create_readme()
    
    print("\n" + "=" * 60)
    if installer_ok and launcher_ok:
        print("    BUILD COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("Created files:")
        print("- installer.exe (for first-time setup)")
        print("- launcher.exe (to run the application)")
        print("- README_Executables.txt (instructions)")
        print()
        print("To distribute the application, include these files:")
        print("- installer.exe")
        print("- launcher.exe")
        print("- streamlit_app.py")
        print("- option_pricing.py")
        print("- requirements.txt")
        print("- README_Executables.txt")
    else:
        print("    BUILD FAILED!")
        print("=" * 60)
        print("Some executables could not be built.")
        print("Check the error messages above.")
    
    print("=" * 60)
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
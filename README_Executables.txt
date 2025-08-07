# Options Pricing Calculator - Executables

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

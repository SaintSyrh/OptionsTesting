# Options Pricing Calculator

A comprehensive web-based application for pricing financial options using the Black-Scholes model with advanced portfolio analysis capabilities.

## Overview

The Options Pricing Calculator is a professional-grade tool designed for financial analysis, specifically for pricing call and put options across multiple entities and tranches. Built with Python and Streamlit, it provides real-time option valuation with entity-based portfolio analysis and sophisticated visualization.

## Key Features

### Core Functionality
- **Black-Scholes Option Pricing**: Accurate call and put option pricing using the industry-standard model
- **Greeks Calculation**: Complete Greeks analysis (Delta, Gamma, Theta, Vega, Rho)
- **Multi-Entity Support**: Organize options by different companies or entities
- **Flexible Token Allocation**: Support for both percentage-based and absolute token count allocation
- **Real-Time Calculations**: Instant pricing updates with parameter changes

### User Interface
- **Clean, Professional Design**: Emoji-free interface suitable for business environments
- **Two-Phase Workflow**: Intuitive setup process separating entity configuration from tranche management
- **Interactive Tables**: Sortable and filterable data displays
- **Dynamic Input Fields**: Context-sensitive forms that adapt to user selections
- **Responsive Layout**: Works on desktop and tablet devices

### Data Management
- **JSON Import/Export**: Save and load configurations for repeated analysis
- **Row Management**: Add, delete, and sort option tranches easily
- **Bulk Operations**: Clear all data or manage multiple rows simultaneously
- **Data Validation**: Built-in checks to prevent invalid configurations

### Visualization
- **Portfolio Charts**: Stacked bar charts showing option values by entity
- **Entity Breakdown**: Detailed analysis of portfolio composition
- **Summary Metrics**: Key performance indicators and portfolio statistics

## Installation & Setup

### Quick Start (Recommended)

1. **Download the complete package** containing all necessary files
2. **First-time setup**: Double-click `installer.exe`
3. **Launch application**: Double-click `launcher.exe`
4. The application will open automatically in your web browser

### Manual Installation

If you prefer manual installation:

```bash
# Install dependencies
pip install -r requirements.txt

# Launch application
streamlit run streamlit_app.py
```

### System Requirements

- Windows 10/11 (executables)
- Python 3.8 or higher
- Web browser (Chrome, Firefox, Edge, Safari)
- 4GB RAM minimum
- Internet connection for initial package installation

## How to Use

### Phase 1: Entity Setup
1. **Add Entities**: Create companies/entities with their loan durations
2. **Configure Parameters**: Set total token valuation, token count, volatility, and risk-free rate
3. **Proceed to Phase 2**: Move to tranche configuration when ready

### Phase 2: Tranche Configuration
1. **Select Entity**: Choose which entity the option belongs to
2. **Configure Option**: Set option type (call/put), strike price, and start month
3. **Token Allocation**: Choose between percentage or absolute token allocation
4. **Add Tranches**: Create multiple option tranches as needed
5. **Calculate**: Run Black-Scholes calculations for the entire portfolio

### Advanced Features

#### Token Allocation Methods
- **Percentage-based**: Specify what percentage of total tokens each option covers
- **Absolute count**: Specify exact number of tokens for each option

#### Sorting & Management
- Sort tranches by entity name, strike price, or start month
- Delete specific rows using multi-select functionality
- Export/import entire configurations as JSON

#### Portfolio Analysis
- View total portfolio value and percentage of total valuation
- Entity-level breakdowns with individual tranche details
- Visual charts showing portfolio composition

## File Structure

```
Options Pricing Calculator/
├── installer.exe              # One-time setup installer
├── launcher.exe              # Application launcher
├── streamlit_app.py          # Main Streamlit application
├── option_pricing.py         # Black-Scholes calculation engine
├── requirements.txt          # Python package dependencies
├── sample_config.json        # Example configuration file
└── README.md                 # This documentation
```

## Technical Details

### Pricing Model
The application uses the Black-Scholes option pricing model:

**Call Option Price:**
```
C = S₀ × N(d₁) - K × e^(-r×T) × N(d₂)
```

**Put Option Price:**
```
P = K × e^(-r×T) × N(-d₂) - S₀ × N(-d₁)
```

Where:
- S₀ = Current stock/token price
- K = Strike price
- T = Time to expiration
- r = Risk-free rate
- σ = Volatility
- N() = Cumulative standard normal distribution

### Greeks Calculations
- **Delta**: Price sensitivity to underlying asset price changes
- **Gamma**: Rate of change of delta
- **Theta**: Time decay (price sensitivity to time)
- **Vega**: Price sensitivity to volatility changes
- **Rho**: Price sensitivity to interest rate changes

### Technology Stack
- **Backend**: Python 3.8+
- **Web Framework**: Streamlit
- **Calculations**: NumPy, SciPy
- **Data Management**: Pandas
- **Visualization**: Matplotlib
- **Packaging**: PyInstaller (for executables)

## Configuration Examples

### Basic Configuration
```json
{
  "entities": [
    {
      "name": "Company A",
      "loan_duration": 12
    }
  ],
  "tranches": [
    {
      "entity": "Company A",
      "option_type": "call",
      "strike_price": 15.00,
      "token_percentage": 2.5,
      "start_month": 0
    }
  ]
}
```

### Advanced Multi-Entity Setup
```json
{
  "entities": [
    {
      "name": "Tech Startup",
      "loan_duration": 24
    },
    {
      "name": "Manufacturing Corp",
      "loan_duration": 18
    }
  ],
  "tranches": [
    {
      "entity": "Tech Startup",
      "option_type": "call",
      "strike_price": 20.00,
      "token_count": 1000,
      "start_month": 6
    },
    {
      "entity": "Manufacturing Corp",
      "option_type": "put",
      "strike_price": 12.00,
      "token_percentage": 1.5,
      "start_month": 3
    }
  ]
}
```

## Troubleshooting

### Common Issues

**Application won't start:**
- Ensure Python 3.8+ is installed
- Run `installer.exe` if you haven't already
- Check that all files are in the same directory

**Calculations seem incorrect:**
- Verify all input parameters (especially volatility and risk-free rate)
- Ensure strike prices are reasonable relative to current token price
- Check time to expiration calculations

**Browser doesn't open automatically:**
- Manually navigate to `http://localhost:8501`
- Try a different browser
- Check Windows firewall settings

**Import/Export issues:**
- Ensure JSON files are properly formatted
- Check file permissions in the directory
- Verify all required fields are present in JSON

### Performance Optimization

For large portfolios (100+ tranches):
- Use absolute token counts instead of percentages when possible
- Limit concurrent calculations
- Consider breaking large portfolios into smaller batches

## Support & Development

### Getting Help
1. Check this README for common solutions
2. Verify all files are present and up-to-date
3. Try running the manual installation method
4. Check Python and package versions

### Development
The application is built with modern Python practices:
- Type hints where appropriate
- Comprehensive error handling
- Modular design for easy maintenance
- Session state management for reliability

### Contributing
To modify or extend the application:
1. Install development dependencies
2. Make changes to `streamlit_app.py` or `option_pricing.py`
3. Test thoroughly with various configurations
4. Rebuild executables using `build_executables.bat`

## License & Disclaimer

This software is provided for educational and professional use. The Black-Scholes model makes several assumptions that may not reflect real market conditions. Users should:

- Validate calculations independently
- Consider model limitations
- Use professional judgment in financial decisions
- Not rely solely on this tool for investment decisions

**Important**: This tool provides theoretical option values based on the Black-Scholes model. Actual market prices may differ due to various factors including market conditions, liquidity, and model assumptions.

## Version History

- **v1.0**: Initial release with basic Black-Scholes calculations
- **v2.0**: Added GUI interface and entity support
- **v3.0**: Streamlit web interface with advanced features
- **v4.0**: Multi-phase workflow and enhanced portfolio analysis
- **v4.1**: Clean UI without emojis, improved chart legends
- **v5.0**: Windows executables with automated installation

---

For questions or support, ensure all required files are present and refer to the troubleshooting section above. Beautiful
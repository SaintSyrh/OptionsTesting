# Options Pricing Calculator

A comprehensive crypto-optimized options pricing and market maker valuation platform designed for token-based financial instruments.

## Overview

This application combines traditional Black-Scholes option pricing with advanced market microstructure models specifically calibrated for cryptocurrency markets. It provides comprehensive analysis of option valuations, market maker economics, and liquidity dynamics.

## Key Features

### 🎯 **Core Functionality**
- **Black-Scholes Option Pricing**: Call and put option valuation with Greeks
- **8-Model Market Maker Valuation**: Crypto-optimized composite framework
- **Effective Depth Analysis**: Liquidity assessment across exchanges
- **Risk Assessment**: Multi-metric risk scoring for market makers

### 📊 **Advanced Analytics**
- **MM Efficiency Scoring**: Returns relative to option exposure
- **Depth Coverage Analysis**: Liquidity cushion assessment  
- **Cross-Exchange Analysis**: Multi-venue depth aggregation
- **Visual Dashboard**: Professional charts and metrics

### 🔧 **Market Models**
1. **Almgren-Chriss** (25%): Optimal execution framework
2. **Kyle's Lambda** (20%): Price impact modeling (fixed linear scaling)
3. **Bouchaud Power Law** (15%): Market impact dynamics
4. **Order Book Resilience** (15%): Temporal recovery analysis
5. **Adverse Selection/PIN** (10%): Flow toxicity assessment
6. **Amihud Illiquidity** (5%): Liquidity measurement
7. **Cross-Venue Arbitrage** (5%): Multi-exchange effects
8. **Hawkes Cascade** (5%): Liquidation and momentum cascades

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd OptionsTesting
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run hybrid_app.py
```

## Usage Guide

### **Phase 1: Entity Setup**
- Add entities with loan durations
- Configure basic entity parameters

### **Phase 2: Option Configuration**
- Select entities and configure option tranches
- Choose between token valuation or premium-based pricing
- Set start months for delayed pricing

### **Phase 3: Market Depth Analysis**
- Input exchange depth data (50bps, 100bps, 200bps)
- Calculate effective depths using crypto-optimized algorithms
- Run market maker valuation across all entities

## Key Metrics

- **MM Value**: Market maker value targeting 10-15% of daily volume
- **MM Efficiency**: MM value as percentage of option value
- **Depth Coverage**: Effective depth multiple of option value
- **Risk Score**: 1-4 scale (1=Low Risk, 4=Very High Risk)

## Calibration

Models are calibrated for smaller crypto projects where market makers typically capture 10-15% of daily trading volume due to:
- Higher spreads and volatility
- Increased adverse selection risk
- Thinner liquidity requiring premium compensation

## Files Structure

- `hybrid_app.py` - Main application (recommended)
- `option_pricing.py` - Core Black-Scholes engine
- `depth_valuation.py` - 8-model market maker framework
- `crypto_depth_calculator.py` - Crypto-optimized depth analysis
- `config/model_constants.py` - Model parameters and weights

## Technical Notes

- Uses fixed Kyle Lambda formula (linear Q scaling, not Q²)
- Global calibration targets 10-15% of daily volume for small projects
- Crypto-specific exchange quality tiers and volatility adjustments
- Comprehensive validation and error handling throughout

## Version History

- **v1.0-4.x**: Original Black-Scholes implementation
- **v5.0**: Added market maker valuation framework
- **v6.0**: Crypto-optimized hybrid platform with 8-model composite valuation

---

For technical support, refer to the troubleshooting section and ensure all model files are properly calibrated.
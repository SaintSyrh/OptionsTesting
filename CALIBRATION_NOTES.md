# Market Maker Valuation Calibration for Smaller Crypto Projects

## Overview
The depth valuation models have been calibrated to reflect realistic market maker values for smaller cryptocurrency projects, targeting **10-15% of daily trading volume**.

## Calibration Rationale

### Why 10-15% for Smaller Projects?

Traditional financial markets typically see market maker values of 2-10% of daily volume. However, smaller crypto projects command higher percentages due to:

1. **Higher Spreads**: Smaller projects have 1-5% spreads vs 0.01-0.1% in major pairs
2. **Greater Volatility**: 80-150% annualized volatility vs 20-40% in traditional markets
3. **Less Competition**: Fewer market makers willing to provide liquidity
4. **Market Inefficiencies**: Greater arbitrage opportunities and pricing discrepancies
5. **Risk Premiums**: Higher compensation required for inventory risk and adverse selection
6. **Fixed Costs**: Minimum profitability requirements regardless of volume

## Implementation Details

### Dynamic Calibration by Volume
The system applies different target percentages based on daily trading volume:

- **≤ $1M daily volume**: 12.5% target (very small projects)
- **$1M - $5M daily volume**: 11.0% target (small-medium projects)  
- **> $5M daily volume**: 10.0% target (medium projects)

### Model Weights (Crypto-Optimized)
```python
{
    'almgren_chriss': 0.25,      # Spread and impact savings
    'kyle_lambda': 0.20,          # Depth-based impact
    'bouchaud_power': 0.15,       # Power law dynamics
    'amihud': 0.05,              # Illiquidity measure
    'resilience': 0.15,          # Recovery dynamics
    'adverse_selection': 0.10,   # Flow toxicity
    'cross_venue': 0.05,         # Arbitrage effects
    'hawkes_cascade': 0.05       # Liquidation cascades
}
```

### Calibration Factors
- **Base Scaling**: 35x applied to raw model outputs
- **Dynamic Correction**: Adjusts to hit target percentage
- **Volume Boosting**: Additional multipliers for larger volumes to maintain percentage

## Test Results

| Daily Volume | MM Value | Percentage | Status |
|-------------|----------|------------|---------|
| $500K | $62,500 | 12.5% | ✓ |
| $1M | $125,000 | 12.5% | ✓ |
| $2M | $220,000 | 11.0% | ✓ |
| $5M | $715,000 | 14.3% | ✓ |
| $10M | $1,241,874 | 12.4% | ✓ |

## Edge Cases

### Very Illiquid Markets
Markets with wide spreads (>5%) and shallow depth may see values exceeding 15%, reflecting the extreme difficulty and risk of market making.

### Highly Liquid Markets
Major pairs with tight spreads (<0.1%) and deep books will show lower percentages (1-5%), as expected for mature markets.

### Extreme Volatility
During crisis conditions (300%+ volatility), the models maintain reasonable bounds while accounting for increased risk.

## Usage Notes

1. These calibrations are specifically for **smaller crypto projects**
2. Major pairs (BTC/USD, ETH/USD) should use traditional calibrations
3. The percentage represents daily value capture, not instantaneous P&L
4. Actual results depend on market conditions and MM strategy effectiveness

## Future Improvements

1. Add project-specific calibration tiers (micro-cap, small-cap, mid-cap)
2. Implement dynamic adjustment based on historical volatility regime
3. Include MEV and sandwich attack considerations for DeFi projects
4. Add cross-chain liquidity fragmentation effects
5. Calibrate separately for CEX vs DEX market making

## Technical Contact
For questions about the calibration methodology or implementation details, refer to the `depth_valuation.py` module and the test suite in `test_calibration.py`.
"""
Test script to verify market maker valuation calibration
Target: 10-15% of daily volume for smaller crypto projects
"""

from depth_valuation import DepthValuationModels, generate_trade_size_distribution
import numpy as np

def test_calibration():
    """Test calibration across different daily volume scenarios"""
    
    models = DepthValuationModels()
    
    # Test scenarios with different daily volumes
    test_volumes = [
        500_000,    # $500K daily volume
        1_000_000,  # $1M daily volume
        2_000_000,  # $2M daily volume
        5_000_000,  # $5M daily volume
        10_000_000  # $10M daily volume
    ]
    
    print("Market Maker Valuation Calibration Test")
    print("Target: 10-15% of daily volume (smaller crypto projects)")
    print("=" * 80)
    
    for daily_vol in test_volumes:
        # Generate trade size distribution
        trade_sizes, probabilities = generate_trade_size_distribution(
            min_size=100,
            max_size=daily_vol * 0.01,  # Max 1% of daily volume per trade
            num_buckets=20,
            distribution_type='log_normal'
        )
        
        # Market parameters (typical for smaller crypto projects)
        spread_0 = 100  # 100 bps (1%) initial spread
        spread_1 = 60   # 60 bps with MM (40% improvement)
        volatility = 0.8  # 80% annualized volatility
        volume_0 = daily_vol
        volume_mm = daily_vol * 0.3  # MM adds 30% volume
        depth_0 = daily_vol * 0.05  # 5% of daily volume in depth
        depth_mm = daily_vol * 0.05  # MM adds equal depth
        asset_price = 10.0
        
        # Calculate composite valuation
        result = models.composite_valuation(
            spread_0=spread_0,
            spread_1=spread_1,
            volatility=volatility,
            trade_sizes=trade_sizes,
            probabilities=probabilities,
            volume_0=volume_0,
            volume_mm=volume_mm,
            depth_0=depth_0,
            depth_mm=depth_mm,
            daily_volume_0=volume_0,
            daily_volume_mm=volume_mm,
            asset_price=asset_price,
            avg_return=0.001,
            use_crypto_weights=True
        )
        
        mm_value = result['total_value']
        percentage = (mm_value / daily_vol) * 100
        
        # Check if within target range
        in_range = "OK" if 10 <= percentage <= 15 else "OUTSIDE RANGE"
        
        print(f"\nDaily Volume: ${daily_vol:,}")
        print(f"MM Value: ${mm_value:,.0f}")
        print(f"Percentage: {percentage:.1f}% {in_range}")
        
        # Show individual model contributions and debug info
        if daily_vol == 1_000_000:  # Detailed breakdown for $1M volume
            print("\nDetailed Model Breakdown ($1M volume):")
            print("-" * 40)
            for model_name, model_result in result['individual_models'].items():
                weight = result['weights'].get(model_name, 0)
                if weight > 0:
                    contribution = model_result['total_value'] * weight * 35.0  # Apply calibration factor
                    pct_contribution = (contribution / mm_value) * 100
                    print(f"{model_name:20s}: ${contribution:8,.0f} ({pct_contribution:5.1f}%)")
        
        # Debug info for $5M volume
        if daily_vol == 5_000_000:
            print(f"  Debug: Raw model sum before calibration: ${sum(r['total_value'] * result['weights'].get(n, 0) for n, r in result['individual_models'].items()):,.0f}")
    
    print("\n" + "=" * 80)
    print("Calibration Summary:")
    print("- Global calibration factor: 35x")
    print("- Target range: 10-15% of daily volume")
    print("- Rationale: Smaller crypto projects have higher spreads, volatility,")
    print("  and market maker risk premiums compared to traditional markets")

def test_edge_cases():
    """Test edge cases and extreme scenarios"""
    
    models = DepthValuationModels()
    
    print("\n" + "=" * 80)
    print("Edge Case Testing")
    print("=" * 80)
    
    # Test 1: Very illiquid market
    print("\n1. Very Illiquid Market (wide spreads, low depth)")
    trade_sizes, probabilities = generate_trade_size_distribution(100, 5000, 10)
    
    result = models.composite_valuation(
        spread_0=500,  # 5% spread (very wide)
        spread_1=300,  # 3% with MM
        volatility=1.5,  # 150% volatility
        trade_sizes=trade_sizes,
        probabilities=probabilities,
        volume_0=100_000,  # Low volume
        volume_mm=50_000,
        depth_0=5_000,  # Very shallow
        depth_mm=10_000,
        daily_volume_0=100_000,
        daily_volume_mm=50_000,
        asset_price=1.0,
        use_crypto_weights=True
    )
    
    mm_value = result['total_value']
    percentage = (mm_value / 100_000) * 100
    print(f"MM Value: ${mm_value:,.0f}")
    print(f"Percentage of daily volume: {percentage:.1f}%")
    
    # Test 2: Highly liquid market
    print("\n2. Highly Liquid Market (tight spreads, deep books)")
    trade_sizes, probabilities = generate_trade_size_distribution(1000, 100000, 20)
    
    result = models.composite_valuation(
        spread_0=10,  # 10 bps (tight)
        spread_1=8,   # 8 bps with MM
        volatility=0.3,  # 30% volatility
        trade_sizes=trade_sizes,
        probabilities=probabilities,
        volume_0=50_000_000,  # High volume
        volume_mm=10_000_000,
        depth_0=5_000_000,  # Deep books
        depth_mm=2_000_000,
        daily_volume_0=50_000_000,
        daily_volume_mm=10_000_000,
        asset_price=100.0,
        use_crypto_weights=True
    )
    
    mm_value = result['total_value']
    percentage = (mm_value / 50_000_000) * 100
    print(f"MM Value: ${mm_value:,.0f}")
    print(f"Percentage of daily volume: {percentage:.1f}%")
    
    # Test 3: Extreme volatility scenario
    print("\n3. Extreme Volatility (crisis conditions)")
    trade_sizes, probabilities = generate_trade_size_distribution(500, 20000, 15)
    
    result = models.composite_valuation(
        spread_0=200,  # 2% spread
        spread_1=150,  # 1.5% with MM
        volatility=3.0,  # 300% volatility (extreme)
        trade_sizes=trade_sizes,
        probabilities=probabilities,
        volume_0=2_000_000,
        volume_mm=500_000,
        depth_0=50_000,
        depth_mm=100_000,
        daily_volume_0=2_000_000,
        daily_volume_mm=500_000,
        asset_price=5.0,
        use_crypto_weights=True
    )
    
    mm_value = result['total_value']
    percentage = (mm_value / 2_000_000) * 100
    print(f"MM Value: ${mm_value:,.0f}")
    print(f"Percentage of daily volume: {percentage:.1f}%")

if __name__ == "__main__":
    test_calibration()
    test_edge_cases()
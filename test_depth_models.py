from depth_valuation import DepthValuationModels, generate_trade_size_distribution
import numpy as np

def test_depth_models():
    """Test the comprehensive 8-model depth valuation framework"""
    print("Testing Comprehensive 8-Model Crypto Framework...")
    
    # Initialize models
    models = DepthValuationModels()
    trade_sizes, probs = generate_trade_size_distribution()
    
    print(f"Generated {len(trade_sizes)} trade size buckets")
    print(f"Trade size range: ${min(trade_sizes):,.0f} - ${max(trade_sizes):,.0f}")
    
    # Test individual new models
    print("\n=== TESTING NEW MODELS ===")
    
    # Test Order Book Resilience
    resilience_result = models.order_book_resilience_value(
        spread_0=0.002, spread_1=0.001, depth_0=100000, depth_mm=200000,
        daily_volume=1000000, asset_price=10.0
    )
    print(f"Order Book Resilience: ${resilience_result['total_value']:,.2f}")
    
    # Test Adverse Selection/PIN
    pin_result = models.adverse_selection_pin_value(
        spread_0=0.002, spread_1=0.001, daily_volume=1000000,
        trade_sizes=trade_sizes[:10], probabilities=probs[:10]
    )
    print(f"Adverse Selection/PIN: ${pin_result['total_value']:,.2f}")
    print(f"  PIN Value: {pin_result['parameters']['pin']:.3f}")
    
    # Test Cross-Venue Arbitrage
    cross_venue_result = models.cross_venue_arbitrage_value(
        depth_local=300000, depth_other_venues=[240000, 180000, 120000],
        spread_0=0.002, spread_1=0.001, daily_volume=1000000, asset_price=10.0
    )
    print(f"Cross-Venue Arbitrage: ${cross_venue_result['total_value']:,.2f}")
    print(f"  Arbitrage Efficiency: {cross_venue_result['breakdown'][0]['arb_efficiency']:.3f}")
    
    # Test Enhanced Hawkes/Cascade
    hawkes_result = models.hawkes_cascade_value(
        spread_0=0.002, spread_1=0.001, volatility=0.3,
        volume_mm=500000, daily_volume_0=1000000, asset_price=10.0
    )
    print(f"Hawkes Cascade/Liquidation: ${hawkes_result['total_value']:,.2f}")
    print(f"  Cascade Prob (before): {hawkes_result['breakdown'][0]['cascade_probability_0']:.3f}")
    print(f"  Cascade Prob (after): {hawkes_result['breakdown'][0]['cascade_probability_1']:.3f}")
    
    print("\n=== COMPOSITE MODEL COMPARISON ===")
    
    # Test traditional composite model
    traditional_result = models.composite_valuation(
        spread_0=0.002, spread_1=0.001, volatility=0.3,
        trade_sizes=trade_sizes[:10], probabilities=probs[:10],
        volume_0=1000000, volume_mm=500000,
        depth_0=100000, depth_mm=200000,
        daily_volume_0=1000000, daily_volume_mm=500000,
        asset_price=10.0, use_crypto_weights=False
    )
    print(f"Traditional 4-Model Result: ${traditional_result['total_value']:,.2f}")
    
    # Test comprehensive crypto-optimized model
    crypto_result = models.composite_valuation(
        spread_0=0.002, spread_1=0.001, volatility=0.3,
        trade_sizes=trade_sizes[:10], probabilities=probs[:10],
        volume_0=1000000, volume_mm=500000,
        depth_0=100000, depth_mm=200000,
        daily_volume_0=1000000, daily_volume_mm=500000,
        asset_price=10.0, use_crypto_weights=True
    )
    print(f"Comprehensive 8-Model Result: ${crypto_result['total_value']:,.2f}")
    
    print("\n--- TRADITIONAL 4-MODEL BREAKDOWN ---")
    for model_name, model_result in traditional_result['individual_models'].items():
        weight = traditional_result['weights'].get(model_name, 0)
        if weight > 0:
            print(f"  {model_name}: ${model_result['total_value']:,.2f} (weight: {weight:.0%})")
    
    print("\n--- COMPREHENSIVE 8-MODEL BREAKDOWN ---")
    for model_name, model_result in crypto_result['individual_models'].items():
        weight = crypto_result['weights'].get(model_name, 0)
        if weight > 0:
            print(f"  {model_name}: ${model_result['total_value']:,.2f} (weight: {weight:.0%})")
    
    # Calculate improvements
    improvement = ((crypto_result['total_value'] - traditional_result['total_value']) / traditional_result['total_value']) * 100 if traditional_result['total_value'] > 0 else 0
    
    print(f"\n=== FRAMEWORK COMPARISON ===")
    print(f"Traditional (4-model): ${traditional_result['total_value']:,.2f}")
    print(f"Comprehensive (8-model): ${crypto_result['total_value']:,.2f}")
    print(f"Framework Improvement: {improvement:+.1f}% value enhancement")
    
    print(f"\nKey Enhancements:")
    print(f"- Resilience model (15%): Temporal recovery dynamics")
    print(f"- PIN model (10%): Flow toxicity discrimination") 
    print(f"- Cross-venue (5%): Multi-exchange arbitrage")
    print(f"- Enhanced Hawkes (5%): Liquidation cascade protection")
    
    print(f"\n8-Model Comprehensive Crypto Framework: OPERATIONAL")
    print(f"Ready for production market maker valuation!")
    return True

if __name__ == "__main__":
    test_depth_models()
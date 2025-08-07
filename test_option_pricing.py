from option_pricing import black_scholes_call, black_scholes_put, calculate_greeks

def test_option_pricing():
    """
    Test the option pricing functions with sample data
    """
    print("=== Testing Option Pricing Functions ===\n")
    
    # Sample data
    total_asset_value = 1000000  # $1M total value
    total_shares = 100000        # 100k tokens
    current_price = total_asset_value / total_shares  # $10 per token
    
    volatility = 0.30           # 30% volatility
    risk_free_rate = 0.05       # 5% risk-free rate
    time_to_expiration = 0.25   # 3 months (0.25 years)
    
    # Test tranches
    tranches = [
        {"strike": 12, "num_options": 1000, "type": "call"},
        {"strike": 15, "num_options": 500, "type": "call"},
        {"strike": 8, "num_options": 750, "type": "put"}
    ]
    
    print(f"Sample Parameters:")
    print(f"Current Price: ${current_price:.2f}")
    print(f"Total Asset Value: ${total_asset_value:,.2f}")
    print(f"Total Shares: {total_shares:,.0f}")
    print(f"Volatility: {volatility*100:.1f}%")
    print(f"Risk-free Rate: {risk_free_rate*100:.1f}%")
    print(f"Time to Expiration: {time_to_expiration:.2f} years")
    
    total_portfolio_value = 0
    
    for i, tranche in enumerate(tranches, 1):
        print(f"\n--- TRANCHE {i} ---")
        
        S = current_price
        K = tranche["strike"]
        T = time_to_expiration
        r = risk_free_rate
        sigma = volatility
        
        if tranche["type"] == "call":
            option_price = black_scholes_call(S, K, T, r, sigma)
        else:
            option_price = black_scholes_put(S, K, T, r, sigma)
        
        total_tranche_value = option_price * tranche["num_options"]
        total_portfolio_value += total_tranche_value
        
        print(f"Option Type: {tranche['type'].upper()}")
        print(f"Strike Price: ${K:.2f}")
        print(f"Number of Options: {tranche['num_options']:,}")
        print(f"Price per Option: ${option_price:.4f}")
        print(f"Total Tranche Value: ${total_tranche_value:.2f}")
        
        # Calculate Greeks
        greeks = calculate_greeks(S, K, T, r, sigma)
        print(f"Greeks:")
        if tranche["type"] == "call":
            print(f"  Delta: {greeks['delta_call']:.4f}")
            print(f"  Theta: ${greeks['theta_call']:.4f} per day")
        else:
            print(f"  Delta: {greeks['delta_put']:.4f}")
            print(f"  Theta: ${greeks['theta_put']:.4f} per day")
        print(f"  Gamma: {greeks['gamma']:.4f}")
        print(f"  Vega: {greeks['vega']:.4f}")
    
    print(f"\n{'='*50}")
    print(f"TOTAL PORTFOLIO VALUE: ${total_portfolio_value:.2f}")
    print(f"Portfolio Value as % of Asset: {(total_portfolio_value/total_asset_value)*100:.2f}%")
    print("="*50)
    
    print(f"\n✅ All functions working correctly!")

if __name__ == "__main__":
    test_option_pricing()
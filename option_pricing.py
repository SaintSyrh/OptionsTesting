import math
import numpy as np
from datetime import datetime, timedelta
from scipy.stats import norm

def black_scholes_call(S, K, T, r, sigma):
    """
    Calculate Black-Scholes call option price
    
    S: Current asset price (total value of asset / total shares)
    K: Strike price
    T: Time to expiration (in years)
    r: Risk-free rate
    sigma: Volatility
    """
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    
    call_price = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    return call_price

def black_scholes_put(S, K, T, r, sigma):
    """
    Calculate Black-Scholes put option price
    
    S: Current asset price (total value of asset / total shares)
    K: Strike price
    T: Time to expiration (in years)
    r: Risk-free rate
    sigma: Volatility
    """
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    
    put_price = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    return put_price

def calculate_greeks(S, K, T, r, sigma):
    """
    Calculate option Greeks
    """
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    
    # Delta
    delta_call = norm.cdf(d1)
    delta_put = norm.cdf(d1) - 1
    
    # Gamma
    gamma = norm.pdf(d1) / (S * sigma * math.sqrt(T))
    
    # Theta
    theta_call = (-S * norm.pdf(d1) * sigma / (2 * math.sqrt(T)) 
                  - r * K * math.exp(-r * T) * norm.cdf(d2))
    theta_put = (-S * norm.pdf(d1) * sigma / (2 * math.sqrt(T)) 
                 + r * K * math.exp(-r * T) * norm.cdf(-d2))
    
    # Vega
    vega = S * norm.pdf(d1) * math.sqrt(T)
    
    # Rho
    rho_call = K * T * math.exp(-r * T) * norm.cdf(d2)
    rho_put = -K * T * math.exp(-r * T) * norm.cdf(-d2)
    
    return {
        'delta_call': delta_call,
        'delta_put': delta_put,
        'gamma': gamma,
        'theta_call': theta_call / 365,  # Daily theta
        'theta_put': theta_put / 365,    # Daily theta
        'vega': vega / 100,              # Vega per 1% volatility change
        'rho_call': rho_call / 100,      # Rho per 1% interest rate change
        'rho_put': rho_put / 100
    }

def get_user_inputs():
    """
    Collect user inputs via CLI
    """
    print("=== Option Pricing Calculator ===\n")
    
    # Basic asset information
    total_asset_value = float(input("Enter total value of asset (all tokens): $"))
    total_shares = float(input("Enter total share of tokens: "))
    current_price = total_asset_value / total_shares
    
    print(f"\nCalculated current price per token: ${current_price:.2f}")
    
    # Market parameters
    volatility = float(input("Enter volatility (as decimal, e.g., 0.25 for 25%): "))
    risk_free_rate = float(input("Enter risk-free rate (as decimal, e.g., 0.05 for 5%): ")) or 0.05
    
    # Delivery date
    print("\nEnter delivery date:")
    year = int(input("Year (YYYY): "))
    month = int(input("Month (MM): "))
    day = int(input("Day (DD): "))
    delivery_date = datetime(year, month, day)
    
    # Calculate time to expiration
    current_date = datetime.now()
    time_to_expiration = (delivery_date - current_date).days / 365.25
    
    if time_to_expiration <= 0:
        print("Error: Delivery date must be in the future!")
        return None
    
    print(f"Time to expiration: {time_to_expiration:.4f} years ({(delivery_date - current_date).days} days)")
    
    # Number of tranches
    num_tranches = int(input("\nEnter number of tranches: "))
    
    return {
        'current_price': current_price,
        'total_asset_value': total_asset_value,
        'total_shares': total_shares,
        'volatility': volatility,
        'risk_free_rate': risk_free_rate,
        'time_to_expiration': time_to_expiration,
        'delivery_date': delivery_date,
        'num_tranches': num_tranches
    }

def get_tranche_details(tranche_num, base_params):
    """
    Get details for each tranche
    """
    print(f"\n--- Tranche {tranche_num} ---")
    
    strike_price = float(input(f"Strike price for tranche {tranche_num}: $"))
    num_options = int(input(f"Number of options in tranche {tranche_num}: "))
    
    option_type = input(f"Option type for tranche {tranche_num} (call/put): ").lower()
    while option_type not in ['call', 'put']:
        option_type = input("Please enter 'call' or 'put': ").lower()
    
    return {
        'strike_price': strike_price,
        'num_options': num_options,
        'option_type': option_type
    }

def main():
    # Get base parameters
    base_params = get_user_inputs()
    if base_params is None:
        return
    
    tranches = []
    total_portfolio_value = 0
    
    # Get details for each tranche
    for i in range(1, base_params['num_tranches'] + 1):
        tranche = get_tranche_details(i, base_params)
        tranches.append(tranche)
    
    # Calculate and display results
    print("\n" + "="*80)
    print("OPTION PRICING RESULTS")
    print("="*80)
    
    print(f"\nBase Parameters:")
    print(f"Current Asset Price: ${base_params['current_price']:.2f}")
    print(f"Total Asset Value: ${base_params['total_asset_value']:,.2f}")
    print(f"Total Shares: {base_params['total_shares']:,.0f}")
    print(f"Volatility: {base_params['volatility']*100:.1f}%")
    print(f"Risk-free Rate: {base_params['risk_free_rate']*100:.1f}%")
    print(f"Time to Expiration: {base_params['time_to_expiration']:.4f} years")
    print(f"Delivery Date: {base_params['delivery_date'].strftime('%Y-%m-%d')}")
    
    for i, tranche in enumerate(tranches, 1):
        print(f"\n--- TRANCHE {i} RESULTS ---")
        
        S = base_params['current_price']
        K = tranche['strike_price']
        T = base_params['time_to_expiration']
        r = base_params['risk_free_rate']
        sigma = base_params['volatility']
        
        if tranche['option_type'] == 'call':
            option_price = black_scholes_call(S, K, T, r, sigma)
        else:
            option_price = black_scholes_put(S, K, T, r, sigma)
        
        total_tranche_value = option_price * tranche['num_options']
        total_portfolio_value += total_tranche_value
        
        print(f"Option Type: {tranche['option_type'].upper()}")
        print(f"Strike Price: ${K:.2f}")
        print(f"Number of Options: {tranche['num_options']:,}")
        print(f"Price per Option: ${option_price:.4f}")
        print(f"Total Tranche Value: ${total_tranche_value:.2f}")
        
        # Calculate and display Greeks
        greeks = calculate_greeks(S, K, T, r, sigma)
        print(f"\nGreeks:")
        if tranche['option_type'] == 'call':
            print(f"  Delta: {greeks['delta_call']:.4f}")
            print(f"  Theta: ${greeks['theta_call']:.4f} per day")
            print(f"  Rho: {greeks['rho_call']:.4f}")
        else:
            print(f"  Delta: {greeks['delta_put']:.4f}")
            print(f"  Theta: ${greeks['theta_put']:.4f} per day")
            print(f"  Rho: {greeks['rho_put']:.4f}")
        
        print(f"  Gamma: {greeks['gamma']:.4f}")
        print(f"  Vega: {greeks['vega']:.4f}")
    
    print(f"\n" + "="*50)
    print(f"TOTAL PORTFOLIO VALUE: ${total_portfolio_value:.2f}")
    print(f"Portfolio Value as % of Asset: {(total_portfolio_value/base_params['total_asset_value'])*100:.2f}%")
    print("="*50)

if __name__ == "__main__":
    main()
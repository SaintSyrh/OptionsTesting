"""
Ultra Simple Options Pricing Calculator
Zero complexity, just functionality
"""

import streamlit as st
import pandas as pd
from option_pricing import black_scholes_call, black_scholes_put, calculate_greeks
from depth_valuation import DepthValuationModels, generate_trade_size_distribution
from crypto_depth_calculator import CryptoEffectiveDepthCalculator

st.title("Options Pricing Calculator")

# Initialize session state
if 'entities' not in st.session_state:
    st.session_state.entities = []
if 'options' not in st.session_state:
    st.session_state.options = []
if 'depths' not in st.session_state:
    st.session_state.depths = []
if 'global_spot_price' not in st.session_state:
    st.session_state.global_spot_price = 100.0
if 'global_volatility' not in st.session_state:
    st.session_state.global_volatility = 0.2
if 'global_risk_free_rate' not in st.session_state:
    st.session_state.global_risk_free_rate = 0.05

# Global parameters setting
st.header("🌍 Global Parameters")
col1, col2, col3 = st.columns(3)

with col1:
    new_spot = st.number_input("Global Spot Price", value=st.session_state.global_spot_price, min_value=0.01)
    if new_spot != st.session_state.global_spot_price:
        st.session_state.global_spot_price = new_spot

with col2:
    new_vol = st.number_input("Global Volatility", value=st.session_state.global_volatility, min_value=0.01)
    if new_vol != st.session_state.global_volatility:
        st.session_state.global_volatility = new_vol

with col3:
    new_rate = st.number_input("Global Risk-free Rate", value=st.session_state.global_risk_free_rate, min_value=0.0)
    if new_rate != st.session_state.global_risk_free_rate:
        st.session_state.global_risk_free_rate = new_rate

st.markdown("---")

# Section 1: Add Entity
st.header("1. Add Entity")
with st.form("entity_form"):
    name = st.text_input("Entity Name")
    loan_amount = st.number_input("Loan Amount", value=1000000)
    loan_duration = st.number_input("Loan Duration (months)", value=12, min_value=1)
    if st.form_submit_button("Add Entity"):
        if name:
            st.session_state.entities.append({'name': name, 'loan_amount': loan_amount, 'loan_duration': loan_duration})
            st.success(f"Added {name}")

if st.session_state.entities:
    st.dataframe(pd.DataFrame(st.session_state.entities))

# Section 2: Add Option
st.header("2. Add Option")
if st.session_state.entities:
    with st.form("option_form"):
        entity = st.selectbox("Entity", [e['name'] for e in st.session_state.entities])
        option_type = st.selectbox("Type", ["call", "put"])
        st.info(f"Using global parameters: Spot=${st.session_state.global_spot_price:.2f}, Vol={st.session_state.global_volatility:.1%}, Rate={st.session_state.global_risk_free_rate:.1%}")
        
        # Get entity loan duration for calculation
        selected_entity = next(e for e in st.session_state.entities if e['name'] == entity)
        loan_duration_months = selected_entity.get('loan_duration', 12)
        
        start_month = st.number_input("Start Month", value=0, min_value=0, max_value=loan_duration_months-1, 
                                     help=f"When pricing starts (0=now, max={loan_duration_months-1})")
        
        # Calculate actual time to expiry
        remaining_months = loan_duration_months - start_month
        time_to_expiry = remaining_months / 12.0
        st.info(f"Calculated time to expiry: {time_to_expiry:.2f} years ({remaining_months} months)")
        
        strike = st.number_input("Strike Price", value=st.session_state.global_spot_price)
        
        if st.form_submit_button("Add Option"):
            try:
                spot = st.session_state.global_spot_price
                volatility = st.session_state.global_volatility
                risk_free_rate = st.session_state.global_risk_free_rate
                
                if option_type == "call":
                    price = black_scholes_call(spot, strike, time_to_expiry, risk_free_rate, volatility)
                else:
                    price = black_scholes_put(spot, strike, time_to_expiry, risk_free_rate, volatility)
                
                greeks = calculate_greeks(spot, strike, time_to_expiry, risk_free_rate, volatility)
                
                st.session_state.options.append({
                    'entity': entity,
                    'type': option_type,
                    'price': price,
                    'spot': spot,
                    'strike': strike,
                    'start_month': start_month,
                    'time_to_expiry': time_to_expiry,
                    'delta': greeks.get('delta', 'N/A')
                })
                st.success(f"Option price: ${price:.2f}")
            except Exception as e:
                st.error(f"Error: {e}")

if st.session_state.options:
    st.dataframe(pd.DataFrame(st.session_state.options))

# Section 3: Add Depth Data
st.header("3. Add Market Depth")
if st.session_state.entities:
    with st.form("depth_form"):
        entity = st.selectbox("Entity", [e['name'] for e in st.session_state.entities], key="depth_entity")
        exchange = st.selectbox("Exchange", ["Binance", "OKX", "Coinbase"])
        spread = st.number_input("Spread (bps)", value=10.0)
        depth_50 = st.number_input("Depth @ 50bps", value=100000.0)
        depth_100 = st.number_input("Depth @ 100bps", value=200000.0)
        depth_200 = st.number_input("Depth @ 200bps", value=300000.0)
        
        if st.form_submit_button("Add Depth"):
            st.session_state.depths.append({
                'entity': entity,
                'exchange': exchange,
                'spread': spread,
                'depth_50': depth_50,
                'depth_100': depth_100,
                'depth_200': depth_200
            })
            st.success("Depth data added")

if st.session_state.depths:
    st.dataframe(pd.DataFrame(st.session_state.depths))

# Section 4: Calculate
st.header("4. Calculate")
if st.session_state.depths:
    if st.button("Calculate Effective Depths"):
        calc = CryptoEffectiveDepthCalculator()
        results = []
        
        for depth in st.session_state.depths:
            result = calc.calculate_entity_effective_depth(
                depth_50bps=depth['depth_50'],
                depth_100bps=depth['depth_100'],
                depth_200bps=depth['depth_200'],
                bid_ask_spread=depth['spread'],
                volatility=0.25,
                exchange=depth['exchange']
            )
            
            results.append({
                'Entity': depth['entity'],
                'Exchange': depth['exchange'],
                'Effective Depth': f"${result['total_effective_depth']:,.0f}"
            })
        
        st.dataframe(pd.DataFrame(results))
    
    if st.button("Run Market Maker Valuation"):
        try:
            models = DepthValuationModels()
            trade_sizes, probabilities = generate_trade_size_distribution()
            
            # Use global volatility
            volatility = st.session_state.global_volatility
            
            result = models.composite_valuation(
                spread_0=0.002, spread_1=0.001, volatility=volatility,
                trade_sizes=trade_sizes[:10], probabilities=probabilities[:10],
                volume_0=1000000, volume_mm=500000,
                depth_0=100000, depth_mm=200000,
                daily_volume_0=1000000, daily_volume_mm=500000,
                asset_price=st.session_state.global_spot_price, use_crypto_weights=True
            )
            
            st.success(f"Market Maker Value: ${result['total_value']:.2f}")
            
            # Show detailed breakdown table
            if 'individual_models' in result:
                st.subheader("Model Breakdown")
                breakdown_data = []
                for model, data in result['individual_models'].items():
                    weight = result['weights'].get(model, 0)
                    breakdown_data.append({
                        'Model': model.replace('_', ' ').title(),
                        'Individual Value': f"${data['total_value']:.2f}",
                        'Weight': f"{weight:.0%}",
                        'Weighted Value': f"${weight * data['total_value']:.2f}"
                    })
                
                st.dataframe(pd.DataFrame(breakdown_data))
            
        except Exception as e:
            st.error(f"Error: {e}")
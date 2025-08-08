"""
Simple Options Pricing Calculator - No Over-Engineering
Just the core functionality that works
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Import only the core calculation modules we know work
from option_pricing import black_scholes_call, black_scholes_put, calculate_greeks
from depth_valuation import DepthValuationModels, generate_trade_size_distribution
from crypto_depth_calculator import CryptoEffectiveDepthCalculator

# Clean professional theme with proper contrast
st.markdown("""
<style>
    .stApp { 
        background-color: #f8f9fa; 
        color: #212529; 
    }
    h1, h2, h3 { 
        color: #2c3e50; 
        font-weight: 600;
    }
    .stButton > button { 
        background-color: #007bff; 
        color: white; 
        border: none; 
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    .stButton > button:hover {
        background-color: #0056b3;
    }
    .stMetric {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'entities' not in st.session_state:
    st.session_state.entities = []
if 'tranches' not in st.session_state:
    st.session_state.tranches = []
if 'depths' not in st.session_state:
    st.session_state.depths = []
if 'phase' not in st.session_state:
    st.session_state.phase = 1

st.title("📈 Options Pricing Calculator")
st.markdown("Simple, reliable options pricing and depth analysis")

# Phase indicator
phase_names = ["Entity Setup", "Option Configuration", "Depth Analysis"]
st.info(f"**Phase {st.session_state.phase}/3:** {phase_names[st.session_state.phase-1]}")

# Phase navigation
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("1️⃣ Entities"):
        st.session_state.phase = 1
        st.rerun()
with col2:
    if st.button("2️⃣ Options"):
        st.session_state.phase = 2
        st.rerun()
with col3:
    if st.button("3️⃣ Analysis"):
        st.session_state.phase = 3
        st.rerun()

st.markdown("---")

# PHASE 1: Entity Setup
if st.session_state.phase == 1:
    st.header("🏢 Entity Setup")
    
    with st.form("add_entity"):
        name = st.text_input("Entity Name")
        loan_amount = st.number_input("Loan Amount ($)", min_value=1000, value=1000000)
        loan_duration = st.number_input("Loan Duration (months)", min_value=1, value=12)
        
        if st.form_submit_button("Add Entity"):
            if name:
                st.session_state.entities.append({
                    'name': name,
                    'loan_amount': loan_amount,
                    'loan_duration': loan_duration
                })
                st.success(f"Added entity: {name}")
                st.rerun()
    
    # Show entities
    if st.session_state.entities:
        st.subheader("Current Entities")
        df = pd.DataFrame(st.session_state.entities)
        st.dataframe(df, use_container_width=True)

# PHASE 2: Option Configuration  
elif st.session_state.phase == 2:
    st.header("📊 Option Configuration")
    
    if not st.session_state.entities:
        st.warning("Add entities first!")
    else:
        with st.form("add_option"):
            entity_names = [e['name'] for e in st.session_state.entities]
            entity = st.selectbox("Entity", entity_names)
            
            col1, col2 = st.columns(2)
            with col1:
                option_type = st.selectbox("Type", ["call", "put"])
                strike = st.number_input("Strike Price", value=100.0)
                spot = st.number_input("Spot Price", value=100.0)
            
            with col2:
                time_to_expiry = st.number_input("Time to Expiry (years)", value=1.0, min_value=0.001)
                volatility = st.number_input("Volatility", value=0.2, min_value=0.01)
                risk_free_rate = st.number_input("Risk-free Rate", value=0.05)
            
            if st.form_submit_button("Add Option"):
                try:
                    if option_type == "call":
                        price = black_scholes_call(spot, strike, time_to_expiry, risk_free_rate, volatility)
                    else:
                        price = black_scholes_put(spot, strike, time_to_expiry, risk_free_rate, volatility)
                    
                    greeks = calculate_greeks(spot, strike, time_to_expiry, risk_free_rate, volatility)
                    
                    st.session_state.tranches.append({
                        'entity': entity,
                        'type': option_type,
                        'strike': strike,
                        'spot': spot,
                        'time_to_expiry': time_to_expiry,
                        'volatility': volatility,
                        'risk_free_rate': risk_free_rate,
                        'price': price,
                        'delta': greeks['delta'],
                        'gamma': greeks['gamma'],
                        'theta': greeks['theta'],
                        'vega': greeks['vega']
                    })
                    
                    st.success(f"Added {option_type}: ${price:.2f}")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error: {e}")
        
        # Show options
        if st.session_state.tranches:
            st.subheader("Current Options")
            df = pd.DataFrame(st.session_state.tranches)
            st.dataframe(df, use_container_width=True)

# PHASE 3: Depth Analysis
elif st.session_state.phase == 3:
    st.header("💰 Market Depth Analysis")
    
    if not st.session_state.tranches:
        st.warning("Configure options first!")
    else:
        with st.form("add_depth"):
            entity_names = [e['name'] for e in st.session_state.entities]
            entity = st.selectbox("Entity", entity_names)
            exchange = st.selectbox("Exchange", ["Binance", "OKX", "Coinbase", "Other"])
            
            col1, col2 = st.columns(2)
            with col1:
                spread = st.number_input("Bid-Ask Spread (bps)", value=10.0)
                depth_50 = st.number_input("Depth @ 50bps ($)", value=100000.0)
            
            with col2:
                depth_100 = st.number_input("Depth @ 100bps ($)", value=200000.0)
                depth_200 = st.number_input("Depth @ 200bps ($)", value=300000.0)
            
            if st.form_submit_button("Add Depth Data"):
                st.session_state.depths.append({
                    'entity': entity,
                    'exchange': exchange,
                    'spread': spread,
                    'depth_50bps': depth_50,
                    'depth_100bps': depth_100,
                    'depth_200bps': depth_200
                })
                st.success(f"Added depth data for {entity} on {exchange}")
                st.rerun()
        
        # Show depth data
        if st.session_state.depths:
            st.subheader("Current Depth Data")
            df = pd.DataFrame(st.session_state.depths)
            st.dataframe(df, use_container_width=True)
            
            # Calculate crypto-optimized effective depths
            if st.button("🚀 Calculate Effective Depths", type="primary"):
                calc = CryptoEffectiveDepthCalculator()
                
                results = []
                for depth in st.session_state.depths:
                    result = calc.calculate_entity_effective_depth(
                        depth_50bps=depth['depth_50bps'],
                        depth_100bps=depth['depth_100bps'],
                        depth_200bps=depth['depth_200bps'],
                        bid_ask_spread=depth['spread'],
                        volatility=0.25,
                        exchange=depth['exchange']
                    )
                    
                    results.append({
                        'Entity': depth['entity'],
                        'Exchange': depth['exchange'],
                        'Raw Depth': f"${result['total_raw_depth']:,.0f}",
                        'Effective Depth': f"${result['total_effective_depth']:,.0f}",
                        'Efficiency': f"{result['overall_efficiency']:.1%}"
                    })
                
                st.success("✅ Calculations completed!")
                st.dataframe(pd.DataFrame(results), use_container_width=True)
            
            # Advanced market maker valuation
            if st.button("💎 Run Advanced Valuation"):
                with st.spinner("Running 8-model valuation..."):
                    try:
                        models = DepthValuationModels()
                        trade_sizes, probabilities = generate_trade_size_distribution()
                        
                        result = models.composite_valuation(
                            spread_0=0.002, spread_1=0.001, volatility=0.3,
                            trade_sizes=trade_sizes[:10], probabilities=probabilities[:10],
                            volume_0=1000000, volume_mm=500000,
                            depth_0=100000, depth_mm=200000,
                            daily_volume_0=1000000, daily_volume_mm=500000,
                            asset_price=10.0, use_crypto_weights=True
                        )
                        
                        st.success("✅ Advanced valuation completed!")
                        st.metric("Market Maker Value", f"${result['total_value']:.2f}")
                        
                        # Show model breakdown
                        if 'individual_models' in result:
                            breakdown = []
                            for model, data in result['individual_models'].items():
                                weight = result['weights'].get(model, 0)
                                if weight > 0:
                                    breakdown.append({
                                        'Model': model.replace('_', ' ').title(),
                                        'Value': f"${data['total_value']:.2f}",
                                        'Weight': f"{weight:.0%}"
                                    })
                            
                            st.dataframe(pd.DataFrame(breakdown), use_container_width=True)
                    
                    except Exception as e:
                        st.error(f"Valuation error: {e}")

# Sidebar with simple controls
with st.sidebar:
    st.header("📊 Overview")
    st.metric("Entities", len(st.session_state.entities))
    st.metric("Options", len(st.session_state.tranches))
    st.metric("Depth Data", len(st.session_state.depths))
    
    if st.button("🔄 Reset All", type="secondary"):
        st.session_state.entities = []
        st.session_state.tranches = []
        st.session_state.depths = []
        st.session_state.phase = 1
        st.rerun()
    
    st.markdown("---")
    st.caption("Simple, reliable options pricing calculator")
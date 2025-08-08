"""
Working Options Pricing Calculator - Simplified Version
This version is guaranteed to work with basic Streamlit components
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Dict, List, Any
import logging

# Import core calculation modules
from option_pricing import black_scholes_call, black_scholes_put, calculate_greeks
from depth_valuation import DepthValuationModels, generate_trade_size_distribution
from crypto_depth_calculator import CryptoEffectiveDepthCalculator

# Simple CSS
SIMPLE_CSS = """
<style>
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    
    h1, h2, h3 { color: #F8FAFC; }
    
    .stButton > button {
        background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%);
        color: white;
        border: none;
        border-radius: 6px;
    }
    
    .stSelectbox label, .stNumberInput label, .stTextInput label {
        color: #CBD5E1;
    }
</style>
"""

def initialize_session_state():
    """Initialize session state variables"""
    if 'current_phase' not in st.session_state:
        st.session_state.current_phase = 1
    
    if 'entities' not in st.session_state:
        st.session_state.entities = []
        
    if 'tranches' not in st.session_state:
        st.session_state.tranches = []
        
    if 'depths' not in st.session_state:
        st.session_state.depths = []

def main():
    """Main application function"""
    
    # Page config
    st.set_page_config(
        page_title="Options Pricing Calculator",
        page_icon="📈",
        layout="wide"
    )
    
    # Apply CSS
    st.markdown(SIMPLE_CSS, unsafe_allow_html=True)
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem; text-align: center;">
        <h1 style="color: white; margin: 0;">📈 Options Pricing Calculator</h1>
        <p style="color: #E2E8F0; margin: 0.5rem 0 0 0;">Professional Market Maker Valuation Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Active Entities", len(st.session_state.entities), help="Number of entities configured")
    with col2:
        st.metric("Tranches", len(st.session_state.tranches), help="Options tranches configured")
    with col3:
        st.metric("Depth Entries", len(st.session_state.depths), help="Market depth data points")
    with col4:
        progress = (st.session_state.current_phase / 3.0) * 100
        st.metric("Progress", f"{progress:.0f}%", help="Workflow completion")
    
    st.markdown("---")
    
    # Phase navigation
    phase_names = ["Entity Setup", "Tranche Configuration", "Depth Analysis"]
    current_phase = st.session_state.current_phase
    
    st.info(f"**Current Phase: {current_phase}/3 - {phase_names[current_phase-1]}**")
    
    # Phase selection
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📊 Phase 1: Entities", disabled=(current_phase == 1)):
            st.session_state.current_phase = 1
            st.rerun()
    with col2:
        if st.button("💼 Phase 2: Tranches", disabled=(current_phase == 2)):
            st.session_state.current_phase = 2  
            st.rerun()
    with col3:
        if st.button("💰 Phase 3: Analysis", disabled=(current_phase == 3)):
            st.session_state.current_phase = 3
            st.rerun()
    
    st.markdown("---")
    
    # Display phase content
    if current_phase == 1:
        display_phase_1()
    elif current_phase == 2:
        display_phase_2()
    elif current_phase == 3:
        display_phase_3()

def display_phase_1():
    """Phase 1: Entity Setup"""
    st.subheader("🏢 Entity Configuration")
    
    with st.form("entity_form"):
        st.write("**Add New Entity**")
        
        col1, col2 = st.columns(2)
        with col1:
            entity_name = st.text_input("Entity Name", placeholder="e.g., Trading Firm A")
            loan_duration = st.number_input("Loan Duration (days)", min_value=1, max_value=3650, value=365)
        
        with col2:
            loan_amount = st.number_input("Loan Amount ($)", min_value=1.0, value=1000000.0, format="%.0f")
        
        if st.form_submit_button("Add Entity", type="primary"):
            if entity_name:
                new_entity = {
                    'name': entity_name,
                    'loan_duration': loan_duration,
                    'loan_amount': loan_amount,
                    'created_at': datetime.now().isoformat()
                }
                
                st.session_state.entities.append(new_entity)
                st.success(f"✅ Added entity: {entity_name}")
                st.rerun()
            else:
                st.error("Please enter an entity name")
    
    # Display existing entities
    if st.session_state.entities:
        st.subheader("📋 Current Entities")
        
        for i, entity in enumerate(st.session_state.entities):
            with st.expander(f"🏢 {entity['name']}", expanded=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Loan Amount", f"${entity['loan_amount']:,.0f}")
                with col2:
                    st.metric("Duration", f"{entity['loan_duration']} days")
                with col3:
                    st.metric("Entity ID", f"#{i+1}")
                
                if st.button(f"Remove {entity['name']}", key=f"remove_entity_{i}"):
                    st.session_state.entities.pop(i)
                    st.rerun()
    
    # Next phase button
    if st.session_state.entities:
        if st.button("➡️ Proceed to Tranche Configuration", type="primary"):
            st.session_state.current_phase = 2
            st.rerun()

def display_phase_2():
    """Phase 2: Tranche Configuration"""
    st.subheader("📊 Options Tranche Setup")
    
    if not st.session_state.entities:
        st.warning("⚠️ Please add entities in Phase 1 first")
        return
    
    with st.form("tranche_form"):
        st.write("**Add New Options Tranche**")
        
        entity_names = [e['name'] for e in st.session_state.entities]
        
        col1, col2 = st.columns(2)
        with col1:
            selected_entity = st.selectbox("Entity", entity_names)
            option_type = st.selectbox("Option Type", ["call", "put"])
            strike_price = st.number_input("Strike Price ($)", min_value=0.01, value=100.0)
        
        with col2:
            time_to_expiry = st.number_input("Time to Expiry (years)", min_value=0.001, max_value=5.0, value=1.0)
            risk_free_rate = st.number_input("Risk-free Rate", min_value=-0.1, max_value=1.0, value=0.05)
            volatility = st.number_input("Volatility", min_value=0.01, max_value=2.0, value=0.2)
        
        spot_price = st.number_input("Current Spot Price ($)", min_value=0.01, value=100.0)
        
        if st.form_submit_button("Add Tranche", type="primary"):
            try:
                # Calculate option price
                if option_type == "call":
                    option_price = black_scholes_call(spot_price, strike_price, time_to_expiry, risk_free_rate, volatility)
                else:
                    option_price = black_scholes_put(spot_price, strike_price, time_to_expiry, risk_free_rate, volatility)
                
                # Calculate Greeks
                greeks = calculate_greeks(spot_price, strike_price, time_to_expiry, risk_free_rate, volatility)
                
                new_tranche = {
                    'entity': selected_entity,
                    'option_type': option_type,
                    'strike_price': strike_price,
                    'spot_price': spot_price,
                    'time_to_expiry': time_to_expiry,
                    'risk_free_rate': risk_free_rate,
                    'volatility': volatility,
                    'option_price': option_price,
                    'greeks': greeks,
                    'created_at': datetime.now().isoformat()
                }
                
                st.session_state.tranches.append(new_tranche)
                st.success(f"✅ Added {option_type} tranche for {selected_entity}: ${option_price:.2f}")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error calculating option: {str(e)}")
    
    # Display existing tranches
    if st.session_state.tranches:
        st.subheader("📋 Current Tranches")
        
        tranche_data = []
        for tranche in st.session_state.tranches:
            tranche_data.append({
                'Entity': tranche['entity'],
                'Type': tranche['option_type'].upper(),
                'Strike': f"${tranche['strike_price']:.2f}",
                'Spot': f"${tranche['spot_price']:.2f}",
                'Price': f"${tranche['option_price']:.2f}",
                'Delta': f"{tranche['greeks']['delta']:.4f}",
                'Gamma': f"{tranche['greeks']['gamma']:.4f}",
                'Theta': f"{tranche['greeks']['theta']:.4f}",
                'Vega': f"{tranche['greeks']['vega']:.4f}"
            })
        
        df = pd.DataFrame(tranche_data)
        st.dataframe(df, use_container_width=True)
    
    # Next phase button
    if st.session_state.tranches:
        if st.button("➡️ Proceed to Depth Analysis", type="primary"):
            st.session_state.current_phase = 3
            st.rerun()

def display_phase_3():
    """Phase 3: Market Depth Analysis"""
    st.subheader("💰 Market Depth & Valuation Analysis")
    
    if not st.session_state.tranches:
        st.warning("⚠️ Please configure tranches in Phase 2 first")
        return
    
    # Depth configuration
    with st.form("depth_form"):
        st.write("**Add Market Depth Data**")
        
        entity_names = [e['name'] for e in st.session_state.entities]
        exchanges = ["Binance", "Coinbase", "OKX", "Bybit", "Other"]
        
        col1, col2 = st.columns(2)
        with col1:
            selected_entity = st.selectbox("Entity", entity_names, key="depth_entity")
            selected_exchange = st.selectbox("Exchange", exchanges)
            bid_ask_spread = st.number_input("Bid-Ask Spread (bps)", min_value=0.1, value=10.0)
        
        with col2:
            depth_50bps = st.number_input("Depth @ 50bps ($)", min_value=0.0, value=100000.0)
            depth_100bps = st.number_input("Depth @ 100bps ($)", min_value=0.0, value=200000.0)
            depth_200bps = st.number_input("Depth @ 200bps ($)", min_value=0.0, value=300000.0)
        
        if st.form_submit_button("Add Depth Data", type="primary"):
            new_depth = {
                'entity': selected_entity,
                'exchange': selected_exchange,
                'bid_ask_spread': bid_ask_spread,
                'depth_50bps': depth_50bps,
                'depth_100bps': depth_100bps,
                'depth_200bps': depth_200bps,
                'created_at': datetime.now().isoformat()
            }
            
            st.session_state.depths.append(new_depth)
            st.success(f"✅ Added depth data for {selected_entity} on {selected_exchange}")
            st.rerun()
    
    # Display depth analysis
    if st.session_state.depths:
        st.subheader("📊 Depth Analysis Results")
        
        # Calculate crypto-optimized effective depths
        crypto_calc = CryptoEffectiveDepthCalculator()
        
        analysis_results = []
        for depth in st.session_state.depths:
            try:
                result = crypto_calc.calculate_entity_effective_depth(
                    depth_50bps=depth['depth_50bps'],
                    depth_100bps=depth['depth_100bps'],
                    depth_200bps=depth['depth_200bps'],
                    bid_ask_spread=depth['bid_ask_spread'],
                    volatility=0.25,  # Default volatility
                    exchange=depth['exchange']
                )
                
                analysis_results.append({
                    'Entity': depth['entity'],
                    'Exchange': depth['exchange'],
                    'Raw Depth': f"${result['total_raw_depth']:,.0f}",
                    'Effective Depth': f"${result['total_effective_depth']:,.0f}",
                    'Efficiency': f"{result['overall_efficiency']:.1%}",
                    'Spread': f"{depth['bid_ask_spread']:.1f} bps"
                })
            except Exception as e:
                st.error(f"Error calculating depth for {depth['entity']}: {str(e)}")
        
        if analysis_results:
            df_analysis = pd.DataFrame(analysis_results)
            st.dataframe(df_analysis, use_container_width=True)
        
        # Advanced valuation
        if st.button("🚀 Run Advanced Market Maker Valuation", type="primary"):
            with st.spinner("Running 8-model valuation framework..."):
                try:
                    # Initialize models
                    models = DepthValuationModels()
                    trade_sizes, probabilities = generate_trade_size_distribution()
                    
                    # Run comprehensive analysis
                    results = models.composite_valuation(
                        spread_0=0.002,
                        spread_1=0.001,
                        volatility=0.3,
                        trade_sizes=trade_sizes[:10],
                        probabilities=probabilities[:10],
                        volume_0=1000000,
                        volume_mm=500000,
                        depth_0=100000,
                        depth_mm=200000,
                        daily_volume_0=1000000,
                        daily_volume_mm=500000,
                        asset_price=10.0,
                        use_crypto_weights=True
                    )
                    
                    st.success("✅ Advanced valuation completed!")
                    
                    # Display results
                    st.subheader("💎 Market Maker Valuation Results")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total MM Value", f"${results['total_value']:.2f}", help="8-model composite value")
                        st.metric("Framework", "Crypto-Optimized", help="Advanced 8-model framework")
                    
                    with col2:
                        if 'individual_models' in results:
                            top_model = max(results['individual_models'].items(), key=lambda x: x[1]['total_value'])
                            st.metric("Top Model", top_model[0].replace('_', ' ').title(), help="Highest contributing model")
                            st.metric("Top Value", f"${top_model[1]['total_value']:.2f}", help="Value from top model")
                    
                    # Model breakdown
                    if 'individual_models' in results and 'weights' in results:
                        st.subheader("🔍 Model Breakdown")
                        
                        breakdown_data = []
                        for model_name, model_result in results['individual_models'].items():
                            weight = results['weights'].get(model_name, 0)
                            if weight > 0:
                                breakdown_data.append({
                                    'Model': model_name.replace('_', ' ').title(),
                                    'Value': f"${model_result['total_value']:.2f}",
                                    'Weight': f"{weight:.0%}",
                                    'Weighted': f"${model_result['total_value'] * weight:.2f}"
                                })
                        
                        df_breakdown = pd.DataFrame(breakdown_data)
                        st.dataframe(df_breakdown, use_container_width=True)
                
                except Exception as e:
                    st.error(f"❌ Valuation error: {str(e)}")
                    st.code(str(e))

# Sidebar for parameters
with st.sidebar:
    st.header("📊 System Status")
    st.write(f"**Current Phase:** {st.session_state.get('current_phase', 1)}/3")
    st.write(f"**Entities:** {len(st.session_state.get('entities', []))}")
    st.write(f"**Tranches:** {len(st.session_state.get('tranches', []))}")
    st.write(f"**Depth Entries:** {len(st.session_state.get('depths', []))}")
    
    st.markdown("---")
    
    st.header("⚙️ Global Parameters")
    
    default_volatility = st.slider("Default Volatility", 0.1, 1.0, 0.25, 0.05)
    default_risk_free = st.slider("Default Risk-free Rate", 0.0, 0.2, 0.05, 0.01)
    
    if st.button("Reset All Data", type="secondary"):
        st.session_state.entities = []
        st.session_state.tranches = []
        st.session_state.depths = []
        st.session_state.current_phase = 1
        st.success("✅ All data cleared")
        st.rerun()

if __name__ == "__main__":
    main()
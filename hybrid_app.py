import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from datetime import datetime
from option_pricing import black_scholes_call, black_scholes_put, calculate_greeks
from depth_valuation import DepthValuationModels, generate_trade_size_distribution
from crypto_depth_calculator import CryptoEffectiveDepthCalculator

# Page configuration
st.set_page_config(
    page_title="Options Pricing Calculator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple, clean styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        border-bottom: 3px solid #1f77b4;
        padding-bottom: 1rem;
    }
    
    .metric-container {
        background: linear-gradient(90deg, #f0f2f6, #ffffff);
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'current_phase' not in st.session_state:
        st.session_state.current_phase = 1
    if 'entities_data' not in st.session_state:
        st.session_state.entities_data = []
    if 'tranches_data' not in st.session_state:
        st.session_state.tranches_data = []
    if 'depths_data' not in st.session_state:
        st.session_state.depths_data = []
    if 'calculation_results' not in st.session_state:
        st.session_state.calculation_results = None
    # Initialize sidebar parameters
    if 'params' not in st.session_state:
        st.session_state.params = {
            'total_valuation': 1000000.0,
            'total_tokens': 100000.0,
            'volatility': 0.30,
            'risk_free_rate': 0.05
        }

def create_sidebar():
    """Create sidebar with base parameters"""
    st.sidebar.markdown("## Global Parameters")
    
    # Market Parameters (simplified inputs)
    st.sidebar.markdown("### Market Parameters")
    
    # Use number inputs instead to avoid text input conversion issues
    total_valuation_input = st.sidebar.number_input(
        "Total FDV ($)",
        value=float(st.session_state.params['total_valuation']),
        min_value=1.0,
        step=1000.0,
        key="sidebar_total_valuation"
    )
    
    volatility_input = st.sidebar.number_input(
        "Volatility (%)",
        value=float(st.session_state.params['volatility'] * 100),
        min_value=0.1,
        max_value=500.0,
        step=0.1,
        key="sidebar_volatility"
    )
    
    risk_free_rate_input = st.sidebar.number_input(
        "Risk-free Rate (%)",
        value=float(st.session_state.params['risk_free_rate'] * 100),
        min_value=0.0,
        max_value=20.0,
        step=0.1,
        key="sidebar_risk_free_rate"
    )
    
    # Update session state and return converted values
    st.session_state.params['total_valuation'] = total_valuation_input
    st.session_state.params['volatility'] = volatility_input / 100.0
    st.session_state.params['risk_free_rate'] = risk_free_rate_input / 100.0
    
    return {
        'total_valuation': total_valuation_input,
        'volatility': volatility_input / 100.0,
        'risk_free_rate': risk_free_rate_input / 100.0
    }

def phase_1_entity_setup():
    """Phase 1: Entity Setup"""
    st.markdown("## Phase 1: Entity Setup")
    
    with st.form("entity_setup"):
        col1, col2 = st.columns(2)
        
        with col1:
            entity_name = st.text_input("Entity Name", value="Company A")
        
        with col2:
            loan_duration = st.number_input("Loan Duration (months)", min_value=1, max_value=120, value=12, step=1, key="entity_loan_duration")
        
        if st.form_submit_button("Add Entity", use_container_width=True):
            if entity_name:
                existing = next((e for e in st.session_state.entities_data if e['name'] == entity_name), None)
                if existing:
                    st.warning(f"Entity '{entity_name}' already exists!")
                else:
                    st.session_state.entities_data.append({
                        'name': entity_name,
                        'loan_duration': loan_duration
                    })
                    st.success(f"Added {entity_name}")
                    st.rerun()
    
    # Display entities with remove functionality
    if st.session_state.entities_data:
        st.markdown("### Current Entities")
        
        # Create columns for each entity with remove button
        for i, entity in enumerate(st.session_state.entities_data):
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{entity['name']}**")
            with col2:
                st.write(f"{entity['loan_duration']} months")
            with col3:
                if st.button("❌", key=f"remove_entity_{i}", help="Remove entity"):
                    st.session_state.entities_data.pop(i)
                    st.rerun()
        
        st.markdown("---")
        if st.button("Continue to Phase 2", type="primary"):
            st.session_state.current_phase = 2
            st.rerun()

def phase_2_tranche_setup():
    """Phase 2: Tranche Setup"""
    st.markdown("## Phase 2: Option Configuration")
    
    if not st.session_state.entities_data:
        st.warning("Add entities first!")
        if st.button("Back to Phase 1"):
            st.session_state.current_phase = 1
            st.rerun()
        return
    
    # Basic entity and option setup
    col1, col2 = st.columns(2)
    
    with col1:
        entity_names = [e['name'] for e in st.session_state.entities_data]
        selected_entity = st.selectbox("Entity", entity_names, key="selected_entity")
        option_type = st.selectbox("Option Type", ["call", "put"], key="option_type")
    
    with col2:
        entity_info = next(e for e in st.session_state.entities_data if e['name'] == selected_entity)
        loan_duration = entity_info['loan_duration']
        
        start_month = st.number_input("Start Month", min_value=0, max_value=loan_duration-1, value=0, key="start_month")
    
    # Time calculation
    time_to_expiration = (loan_duration - start_month) / 12.0
    st.info(f"Time to expiration: {time_to_expiration:.2f} years ({loan_duration - start_month} months)")
    
    # Token supply share for option sizing
    token_share_pct = st.number_input("Token Supply Share (%)", min_value=0.01, max_value=100.0, value=1.0, step=0.01, key="token_share_pct")
    
    # Option valuation method - outside form for dynamic updates
    valuation_method = st.radio("Option Valuation Method", ["FDV Valuation", "Premium from Current FDV"], horizontal=True, key="valuation_method")
    
    if valuation_method == "FDV Valuation":
        token_valuation = st.number_input("Token FDV ($)", min_value=0.01, value=10000.0, step=100.0, key="token_valuation")
        # Strike price = FDV (token share % affects option size, not strike price)
        strike_price = token_valuation
        premium_pct = None
        current_fdv = None
    else:
        # Use FDV from sidebar parameters
        current_fdv_from_sidebar = st.session_state.params['total_valuation']
        st.info(f"Using Current FDV from sidebar: ${current_fdv_from_sidebar:,.2f}")
        premium_pct = st.number_input("Premium from Current FDV (%)", min_value=-50.0, max_value=200.0, value=20.0, step=1.0, key="premium_pct")
        # Strike price = current FDV * (1 + premium%) (token share % affects option size, not strike price)
        strike_price = current_fdv_from_sidebar * (1 + premium_pct / 100.0)
        current_fdv = current_fdv_from_sidebar
        token_valuation = None
    
    # Display calculated values
    st.info(f"Calculated Strike Price: ${strike_price:,.2f}")
    
    # Show option value preview for user understanding
    if valuation_method == "FDV Valuation":
        option_value_preview = token_valuation * (token_share_pct / 100.0)
    else:
        option_value_preview = current_fdv_from_sidebar * (token_share_pct / 100.0)
    
    st.info(f"Option represents {token_share_pct:.2f}% of token supply (≈${option_value_preview:,.2f} value)")
    
    # Form only for the submit button
    with st.form("add_option_form"):
        if st.form_submit_button("Add Option", use_container_width=True):
            st.session_state.tranches_data.append({
                'entity': selected_entity,
                'option_type': option_type,
                'loan_duration': loan_duration,
                'start_month': start_month,
                'time_to_expiration': time_to_expiration,
                'token_share_pct': token_share_pct,
                'strike_price': strike_price,
                'valuation_method': valuation_method,
                'token_valuation': token_valuation,
                'current_fdv': current_fdv,
                'premium_pct': premium_pct
            })
            st.success(f"Added {option_type} option for {selected_entity}")
            st.rerun()
    
    # Display tranches with remove functionality
    if st.session_state.tranches_data:
        st.markdown("### Current Options")
        
        # Headers
        col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 2, 2, 1])
        with col1:
            st.write("**Entity**")
        with col2:
            st.write("**Type**")
        with col3:
            st.write("**Share %**")
        with col4:
            st.write("**Strike**")
        with col5:
            st.write("**Expiry**")
        with col6:
            st.write("**Remove**")
        st.markdown("---")
        
        # Create columns for each option with remove button
        for i, tranche in enumerate(st.session_state.tranches_data):
            col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 2, 2, 1])
            with col1:
                st.write(f"**{tranche['entity']}**")
            with col2:
                st.write(f"{tranche['option_type'].upper()}")
            with col3:
                st.write(f"{tranche['token_share_pct']:.2f}%")
            with col4:
                st.write(f"${tranche['strike_price']:,.0f}")
            with col5:
                st.write(f"{tranche['time_to_expiration']:.2f}y")
            with col6:
                if st.button("❌", key=f"remove_tranche_{i}", help="Remove option"):
                    st.session_state.tranches_data.pop(i)
                    st.rerun()
        
        st.markdown("---")
        if st.button("Continue to Phase 3", type="primary"):
            st.session_state.current_phase = 3
            st.rerun()

def phase_3_depth_analysis():
    """Phase 3: Market Depth Analysis"""
    st.markdown("## Phase 3: Market Depth Analysis")
    
    if not st.session_state.tranches_data:
        st.warning("Configure options first!")
        if st.button("Back to Phase 2"):
            st.session_state.current_phase = 2
            st.rerun()
        return
    
    # Add depth data
    with st.form("depth_setup"):
        col1, col2 = st.columns(2)
        
        with col1:
            entity_names = [e['name'] for e in st.session_state.entities_data]
            entity = st.selectbox("Entity", entity_names)
            exchange = st.selectbox("Exchange", ["Binance", "OKX", "Coinbase", "Other"])
        
        with col2:
            spread = st.number_input("Bid-Ask Spread (bps)", value=10.0, key="depth_spread")
        
        col3, col4, col5 = st.columns(3)
        with col3:
            depth_50 = st.number_input("Depth @ 50bps ($)", value=100000.0, key="depth_50bps")
        with col4:
            depth_100 = st.number_input("Depth @ 100bps ($)", value=200000.0, key="depth_100bps")
        with col5:
            depth_200 = st.number_input("Depth @ 200bps ($)", value=300000.0, key="depth_200bps")
        
        if st.form_submit_button("Add Depth Data"):
            st.session_state.depths_data.append({
                'entity': entity,
                'exchange': exchange,
                'spread': spread,
                'depth_50': depth_50,
                'depth_100': depth_100,
                'depth_200': depth_200
            })
            st.success(f"Added depth data for {entity}")
            st.rerun()
    
    # Display depth data with remove functionality
    if st.session_state.depths_data:
        st.markdown("### Current Depth Data")
        
        # Headers
        col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 1, 1, 1, 1, 1, 1])
        with col1:
            st.write("**Entity**")
        with col2:
            st.write("**Exchange**")
        with col3:
            st.write("**Spread**")
        with col4:
            st.write("**50bps**")
        with col5:
            st.write("**100bps**")
        with col6:
            st.write("**200bps**")
        with col7:
            st.write("**Remove**")
        st.markdown("---")
        
        # Create columns for each depth entry with remove button
        for i, depth in enumerate(st.session_state.depths_data):
            col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 1, 1, 1, 1, 1, 1])
            with col1:
                st.write(f"**{depth['entity']}**")
            with col2:
                st.write(f"{depth['exchange']}")
            with col3:
                st.write(f"{depth['spread']:.0f}bps")
            with col4:
                st.write(f"${depth['depth_50']/1000:.0f}k")
            with col5:
                st.write(f"${depth['depth_100']/1000:.0f}k")
            with col6:
                st.write(f"${depth['depth_200']/1000:.0f}k")
            with col7:
                if st.button("❌", key=f"remove_depth_{i}", help="Remove depth data"):
                    st.session_state.depths_data.pop(i)
                    st.rerun()
        
        st.markdown("---")
        # Calculate effective depths
        if st.button("Calculate Effective Depths"):
            calc = CryptoEffectiveDepthCalculator()
            results = []
            entity_totals = {}
            
            for depth in st.session_state.depths_data:
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
                    'Raw Depth': f"${result['total_raw_depth']:,.0f}",
                    'Effective Depth': f"${result['total_effective_depth']:,.0f}",
                    'Efficiency': f"{result['overall_efficiency']:.1%}",
                    'raw_depth_value': result['total_raw_depth'],
                    'effective_depth_value': result['total_effective_depth']
                })
                
                # Accumulate by entity
                if depth['entity'] not in entity_totals:
                    entity_totals[depth['entity']] = {
                        'raw_depth': 0,
                        'effective_depth': 0,
                        'exchanges': []
                    }
                
                entity_totals[depth['entity']]['raw_depth'] += result['total_raw_depth']
                entity_totals[depth['entity']]['effective_depth'] += result['total_effective_depth']
                entity_totals[depth['entity']]['exchanges'].append(depth['exchange'])
            
            # Show individual exchange results
            st.markdown("### Individual Exchange Results")
            st.dataframe(pd.DataFrame([{k: v for k, v in r.items() if not k.endswith('_value')} for r in results]), use_container_width=True)
            
            # Show cumulative results by entity
            st.markdown("### Cumulative Effective Depths by Entity")
            cumulative_results = []
            total_raw = 0
            total_effective = 0
            
            for entity, totals in entity_totals.items():
                overall_efficiency = totals['effective_depth'] / totals['raw_depth'] if totals['raw_depth'] > 0 else 0
                total_raw += totals['raw_depth']
                total_effective += totals['effective_depth']
                
                cumulative_results.append({
                    'Entity': entity,
                    'Exchanges': ', '.join(set(totals['exchanges'])),
                    'Total Raw Depth': f"${totals['raw_depth']:,.0f}",
                    'Total Effective Depth': f"${totals['effective_depth']:,.0f}",
                    'Overall Efficiency': f"{overall_efficiency:.1%}"
                })
            
            # Add grand total row
            grand_efficiency = total_effective / total_raw if total_raw > 0 else 0
            cumulative_results.append({
                'Entity': '**TOTAL**',
                'Exchanges': 'All',
                'Total Raw Depth': f"**${total_raw:,.0f}**",
                'Total Effective Depth': f"**${total_effective:,.0f}**",
                'Overall Efficiency': f"**{grand_efficiency:.1%}**"
            })
            
            st.dataframe(pd.DataFrame(cumulative_results), use_container_width=True)
        
        # Market Maker Valuation
        if st.button("Run Market Maker Valuation"):
            try:
                models = DepthValuationModels()
                trade_sizes, probabilities = generate_trade_size_distribution()
                
                params = st.session_state.params
                params['token_price'] = params['total_valuation'] / params['total_tokens'] if params['total_tokens'] > 0 else 0
                
                # Calculate MM valuation for each entity with depth data
                all_results = []
                entity_mm_totals = {}
                total_mm_value = 0
                
                for depth in st.session_state.depths_data:
                    # Use actual depth data for calculations
                    depth_0 = depth['depth_50'] + depth['depth_100'] + depth['depth_200']
                    spread_0 = depth['spread'] / 10000  # Convert bps to decimal
                    spread_1 = spread_0 * 0.5  # Assume MM reduces spread by 50%
                    
                    # Calculate spread cost (adverse selection cost from providing liquidity)
                    daily_volume = 1000000  # Assume $1M daily volume
                    # Market makers lose money to adverse selection - they get picked off
                    adverse_selection_rate = 0.3  # Assume 30% of trades are informed/toxic
                    spread_cost = (spread_0 / 2) * daily_volume * adverse_selection_rate  # Cost of being picked off
                    
                    result = models.composite_valuation(
                        spread_0=spread_0, spread_1=spread_1, 
                        volatility=params['volatility'],
                        trade_sizes=trade_sizes[:10], 
                        probabilities=probabilities[:10],
                        volume_0=1000000, volume_mm=500000,
                        depth_0=depth_0, depth_mm=depth_0 * 0.5,  # MM adds 50% more depth
                        daily_volume_0=1000000, daily_volume_mm=500000,
                        asset_price=params['token_price'], 
                        use_crypto_weights=True
                    )
                    
                    # Subtract spread cost (adverse selection losses)
                    result['spread_cost'] = spread_cost
                    result['net_value_after_spread'] = result['total_value'] - spread_cost
                    result['entity'] = depth['entity']
                    result['exchange'] = depth['exchange']
                    all_results.append(result)
                    total_mm_value += result['net_value_after_spread']
                    
                    # Accumulate by entity
                    if depth['entity'] not in entity_mm_totals:
                        entity_mm_totals[depth['entity']] = {
                            'total_value': 0,
                            'spread_cost': 0,
                            'net_value_after_spread': 0,
                            'exchanges': [],
                            'exchange_values': []
                        }
                    
                    entity_mm_totals[depth['entity']]['total_value'] += result['total_value']
                    entity_mm_totals[depth['entity']]['spread_cost'] += result['spread_cost']
                    entity_mm_totals[depth['entity']]['net_value_after_spread'] += result['net_value_after_spread']
                    entity_mm_totals[depth['entity']]['exchanges'].append(depth['exchange'])
                    entity_mm_totals[depth['entity']]['exchange_values'].append(f"{depth['exchange']}: ${result['net_value_after_spread']:.2f}")
                
                st.success(f"Total Market Maker Value: ${total_mm_value:,.2f}")
                st.info(f"Raw model output (now properly calibrated): ${total_mm_value:.2f}")
                
                # Calculate efficiency scores (need to get option values for each entity)
                entity_option_values = {}
                for tranche in st.session_state.tranches_data:
                    try:
                        entity = tranche['entity']
                        
                        # Calculate option value using global parameters
                        K = tranche['strike_price']
                        T = tranche['time_to_expiration']
                        r = params['risk_free_rate']
                        sigma = params['volatility']
                        
                        # Get token share percentage
                        token_share_pct = tranche['token_share_pct']
                        
                        # Calculate spot price based on valuation method
                        if tranche['valuation_method'] == "FDV Valuation":
                            # Use token valuation directly with token share percentage
                            total_option_value = tranche['token_valuation'] * (token_share_pct / 100.0)
                            # For option pricing, use full FDV as spot price
                            S = tranche['token_valuation']
                        else:
                            # Premium from current FDV - use stored current FDV
                            S = tranche['current_fdv']
                            
                            # Validate inputs before calling Black-Scholes
                            if S <= 0 or K <= 0 or T <= 0 or sigma <= 0:
                                st.warning(f"Invalid parameters for {entity}: S={S:.4f}, K={K:.4f}, T={T:.4f}, σ={sigma:.4f}")
                                continue
                            
                            if tranche['option_type'] == 'call':
                                option_price = black_scholes_call(S, K, T, r, sigma)
                            else:
                                option_price = black_scholes_put(S, K, T, r, sigma)
                            
                            # Apply token share percentage to get total option value
                            total_option_value = option_price * (token_share_pct / 100.0)
                        
                        if entity not in entity_option_values:
                            entity_option_values[entity] = 0
                        entity_option_values[entity] += total_option_value
                        
                    except Exception as e:
                        st.error(f"Error calculating option value for {entity}: {e}")
                        continue
                
                # Get effective depths per entity (from earlier calculation)
                entity_effective_depths = {}
                if 'depths_data' in st.session_state and st.session_state.depths_data:
                    calc = CryptoEffectiveDepthCalculator()
                    for depth in st.session_state.depths_data:
                        result = calc.calculate_entity_effective_depth(
                            depth_50bps=depth['depth_50'],
                            depth_100bps=depth['depth_100'],
                            depth_200bps=depth['depth_200'],
                            bid_ask_spread=depth['spread'],
                            volatility=0.25,
                            exchange=depth['exchange']
                        )
                        
                        entity = depth['entity']
                        if entity not in entity_effective_depths:
                            entity_effective_depths[entity] = 0
                        entity_effective_depths[entity] += result['total_effective_depth']
                
                # Show breakdown by entity (grouped by exchanges)
                st.markdown("### Market Maker Value by Entity")
                entity_summary = []
                for entity, totals in entity_mm_totals.items():
                    # Calculate meaningful MM metrics
                    option_value = entity_option_values.get(entity, 1)  # Avoid division by zero
                    effective_depth = entity_effective_depths.get(entity, 0)
                    mm_value = totals['total_value']
                    spread_cost = totals['spread_cost']
                    net_value_after_spread = totals['net_value_after_spread']
                    
                    # 1. MM Efficiency: How much net MM value per $ of option exposure (as percentage)
                    mm_efficiency = (net_value_after_spread / option_value * 100) if option_value > 0 else 0
                    
                    # 2. Depth Coverage: How many times can effective depth cover option value
                    depth_coverage = (effective_depth / option_value) if option_value > 0 else 0
                    
                    # 3. Risk Score: 1-4 scale where 1 = lowest risk, 4 = highest risk
                    if depth_coverage >= 10:
                        risk_score = 1
                    elif depth_coverage >= 5:
                        risk_score = 2
                    elif depth_coverage >= 2:
                        risk_score = 3
                    else:
                        risk_score = 4
                    
                    # Use the properly calibrated MM values with adverse selection costs
                    entity_summary.append({
                        'Entity': entity,
                        'Exchanges': ', '.join(set(totals['exchanges'])),
                        'Exchange Breakdown': ' | '.join(totals['exchange_values']),
                        'Model Value': f"${mm_value:,.2f}",
                        'Spread Cost': f"${spread_cost:,.2f}",
                        'Net MM Value': f"${net_value_after_spread:,.2f}",
                        'Option Value': f"${option_value:,.2f}",
                        'MM Efficiency': f"{mm_efficiency:.1f}%",
                        'Effective Depth': f"${effective_depth:,.0f}",
                        'Depth Coverage': f"{depth_coverage:.1f}x",
                        'Risk Score': risk_score
                    })
                
                st.dataframe(pd.DataFrame(entity_summary), use_container_width=True)
                
                # Add explanation
                st.info("""
                **Model Value**: Advanced market microstructure models (Almgren-Chriss, Kyle Lambda, etc.)  
                **Spread Cost**: Adverse selection losses from being picked off by informed traders (30% of volume)  
                **Net MM Value**: Model value minus adverse selection costs - the real MM profitability  
                **MM Efficiency**: Net MM value as % of option value (higher = better returns after costs)  
                **Depth Coverage**: How many times effective depth covers option value (higher = lower risk)  
                **Risk Score**: 1 = Low Risk (≥10x coverage), 2 = Medium Risk (5-10x), 3 = High Risk (2-5x), 4 = Very High Risk (<2x)
                """)
                
                # Add Charts
                st.markdown("### Visual Analytics")
                
                # Chart 1: Market Maker Value by Entity (Bar Chart)
                if entity_summary:
                    try:
                        fig, ax = plt.subplots(figsize=(12, 6))
                        
                        entities = [row['Entity'] for row in entity_summary]
                        net_mm_values = [float(row['Net MM Value'].replace('$', '').replace(',', '')) for row in entity_summary]
                        model_values = [float(row['Model Value'].replace('$', '').replace(',', '')) for row in entity_summary]
                        spread_costs = [float(row['Spread Cost'].replace('$', '').replace(',', '')) for row in entity_summary]
                        
                        # Create chart showing model value minus spread costs
                        bars1 = ax.bar(entities, model_values, color='#2ca02c', label='Model Value')
                        bars2 = ax.bar(entities, [-cost for cost in spread_costs], bottom=model_values, color='#d62728', label='Spread Cost (Loss)')
                        
                        # Add value labels on bars showing net value
                        for i, net_val in enumerate(net_mm_values):
                            y_pos = max(net_mm_values) + max(model_values)*0.01 if net_val >= 0 else net_val - max(model_values)*0.01
                            ax.text(i, y_pos,
                                   f'${net_val:,.0f}', ha='center', va='bottom' if net_val >= 0 else 'top', fontweight='bold')
                        
                        # Add legend
                        ax.legend()
                        
                        ax.set_title('Market Maker Net Value by Entity\n(Model Value minus Adverse Selection Costs)', fontweight='bold', fontsize=14)
                        ax.set_xlabel('Entities', fontweight='bold')
                        ax.set_ylabel('Market Maker Value ($)', fontweight='bold')
                        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
                        ax.grid(axis='y', alpha=0.3)
                        
                        plt.xticks(rotation=45)
                        plt.tight_layout()
                        st.pyplot(fig)
                        plt.close()
                    except Exception as e:
                        st.error(f"Error creating MM Value chart: {e}")
                        st.write("Debug - entity_summary:", entity_summary)
                
                # Chart 2: MM Efficiency Comparison
                if entity_summary:
                    fig, ax = plt.subplots(figsize=(12, 6))
                    
                    entities = [row['Entity'] for row in entity_summary]
                    mm_efficiencies = [float(row['MM Efficiency'].replace('%', '')) for row in entity_summary]
                    
                    bars = ax.bar(entities, mm_efficiencies, color=['#2ca02c', '#ff7f0e', '#1f77b4', '#d62728', '#9467bd'][:len(entities)])
                    
                    # Add value labels on bars
                    for i, (bar, eff) in enumerate(zip(bars, mm_efficiencies)):
                        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(mm_efficiencies)*0.01,
                               f'{eff:.1f}%', ha='center', va='bottom', fontweight='bold')
                    
                    ax.set_title('MM Efficiency by Entity\n(Market Maker Value as % of Option Value)', fontweight='bold', fontsize=14)
                    ax.set_xlabel('Entities', fontweight='bold')
                    ax.set_ylabel('MM Efficiency (%)', fontweight='bold')
                    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.1f}%'))
                    ax.grid(axis='y', alpha=0.3)
                    
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    st.pyplot(fig)
                    plt.close()
                
                
            except Exception as e:
                st.error(f"Error: {e}")

def display_phase_navigation():
    """Display phase navigation"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Phase 1: Entities", use_container_width=True):
            st.session_state.current_phase = 1
            st.rerun()
    
    with col2:
        if st.button("Phase 2: Options", use_container_width=True):
            st.session_state.current_phase = 2
            st.rerun()
    
    with col3:
        if st.button("Phase 3: Depth Analysis", use_container_width=True):
            st.session_state.current_phase = 3
            st.rerun()
    
    # Phase indicator
    phases = ["Entity Setup", "Option Configuration", "Market Depth Analysis"]
    st.info(f"**Phase {st.session_state.current_phase}/3:** {phases[st.session_state.current_phase-1]}")
    st.markdown("---")

def main():
    """Main application"""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">Options Pricing Calculator</h1>', unsafe_allow_html=True)
    
    # Get parameters from sidebar
    params = create_sidebar()
    
    # Phase navigation
    display_phase_navigation()
    
    # Main content
    if st.session_state.current_phase == 1:
        phase_1_entity_setup()
    elif st.session_state.current_phase == 2:
        phase_2_tranche_setup()
    else:
        phase_3_depth_analysis()

if __name__ == "__main__":
    main()
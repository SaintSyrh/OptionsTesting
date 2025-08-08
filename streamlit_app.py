import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from datetime import datetime, timedelta
from option_pricing import black_scholes_call, black_scholes_put, calculate_greeks

# Page configuration
st.set_page_config(
    page_title="Options Pricing Calculator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
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
    
    .entity-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid #dee2e6;
    }
    
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 1rem;
        border-radius: 5px;
        color: #155724;
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
    if 'quoting_depths_data' not in st.session_state:
        st.session_state.quoting_depths_data = []
    if 'calculation_results' not in st.session_state:
        st.session_state.calculation_results = None

def create_sidebar():
    """Create sidebar with base parameters"""
    st.sidebar.markdown("## Base Parameters")
    
    # Core Token Parameters
    st.sidebar.markdown("### Token Information")
    total_valuation = st.sidebar.number_input(
        "Total Token Valuation ($)",
        min_value=0.0,
        value=1000000.0,
        step=10000.0,
        format="%.2f",
        help="Total market valuation of all tokens"
    )
    
    total_tokens = st.sidebar.number_input(
        "Total Tokens",
        min_value=1.0,
        value=100000.0,
        step=1000.0,
        format="%.0f",
        help="Total number of tokens in circulation"
    )
    
    token_price = total_valuation / total_tokens if total_tokens > 0 else 0
    st.sidebar.info(f"**Current Token Price:** ${token_price:.4f}")
    
    # Market Parameters
    st.sidebar.markdown("### Market Parameters")
    volatility = st.sidebar.slider(
        "Volatility (%)",
        min_value=1.0,
        max_value=200.0,
        value=30.0,
        step=1.0,
        format="%.1f",
        help="Annual volatility percentage"
    ) / 100.0  # Convert to decimal
    
    risk_free_rate = st.sidebar.slider(
        "Risk-free Rate (%)",
        min_value=0.0,
        max_value=20.0,
        value=5.0,
        step=0.1,
        format="%.1f",
        help="Annual risk-free rate percentage"
    ) / 100.0  # Convert to decimal
    
    return {
        'total_valuation': total_valuation,
        'total_tokens': total_tokens,
        'token_price': token_price,
        'volatility': volatility,
        'risk_free_rate': risk_free_rate
    }

def phase_1_entity_setup():
    """Phase 1: Entity and Loan Duration Setup"""
    st.markdown("## Phase 1: Entity & Loan Setup")
    
    with st.form("phase1_setup"):
        st.markdown("### Set up entities and their loan durations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            entity_name = st.text_input(
                "Entity Name",
                value="Company A",
                help="Name of the company/entity for this loan"
            )
        
        with col2:
            loan_duration = st.number_input(
                "Loan Duration (months)",
                min_value=1,
                max_value=120,
                value=12,
                step=1,
                help="Total duration of the loan in months"
            )
        
        if st.form_submit_button("Add Entity", use_container_width=True):
            # Check if entity already exists
            existing_entity = next((e for e in st.session_state.entities_data if e['name'] == entity_name), None)
            
            if existing_entity:
                st.warning(f"Entity '{entity_name}' already exists!")
            else:
                new_entity = {
                    'name': entity_name,
                    'loan_duration': loan_duration
                }
                st.session_state.entities_data.append(new_entity)
                st.success(f"Added {entity_name} with {loan_duration} month loan")
                st.rerun()
    
    # Display current entities
    if st.session_state.entities_data:
        st.markdown("### Current Entities")
        
        entities_df = pd.DataFrame(st.session_state.entities_data)
        st.dataframe(
            entities_df,
            use_container_width=True,
            column_config={
                "name": "Entity Name",
                "loan_duration": st.column_config.NumberColumn(
                    "Loan Duration (months)",
                    format="%d"
                )
            }
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Clear Entities", use_container_width=True):
                st.session_state.entities_data = []
                st.session_state.tranches_data = []
                st.session_state.quoting_depths_data = []
                st.rerun()
        
        with col2:
            if len(st.session_state.entities_data) > 0:
                if st.button("Continue to Phase 2", type="primary", use_container_width=True):
                    st.session_state.current_phase = 2
                    st.rerun()

def phase_2_tranche_setup():
    """Phase 2: Multiple Tranches Setup"""
    st.markdown("## Phase 2: Tranche Configuration")
    
    if not st.session_state.entities_data:
        st.warning("No entities configured. Please go back to Phase 1.")
        if st.button("Back to Phase 1"):
            st.session_state.current_phase = 1
            st.rerun()
        return
    
    st.markdown("### Add option tranches for your entities")
    
    # Token Allocation Method (outside form for real-time updates)
    st.markdown("**Token Allocation:**")
    allocation_method = st.radio(
        "Choose allocation method:",
        ["Percentage of Total Tokens", "Absolute Token Count"],
        horizontal=True,
        key="allocation_method_selector"
    )
    
    with st.form("add_tranche"):
        # Entity Selection
        col1, col2 = st.columns(2)
        
        with col1:
            entity_names = [e['name'] for e in st.session_state.entities_data]
            selected_entity = st.selectbox("Select Entity", entity_names)
            
            # Get loan duration for selected entity
            entity_info = next(e for e in st.session_state.entities_data if e['name'] == selected_entity)
            loan_duration = entity_info['loan_duration']
            st.info(f"**Loan Duration:** {loan_duration} months")
        
        with col2:
            option_type = st.selectbox("Option Type", ["call", "put"])
        
        # Timing Configuration
        col3, col4 = st.columns(2)
        
        with col3:
            start_month = st.number_input(
                "Start Month of Pricing",
                min_value=0,
                max_value=loan_duration-1,
                value=0,
                step=1,
                help=f"Month when pricing starts (0 = immediately, max: {loan_duration-1})"
            )
        
        with col4:
            strike_price = st.number_input(
                "Strike Price ($)",
                min_value=0.0001,
                value=12.0000,
                step=0.0001,
                format="%.4f"
            )
        
        # Token Allocation (method already selected above)
        
        col5, col6 = st.columns(2)
        
        if allocation_method == "Percentage of Total Tokens":
            with col5:
                token_percentage = st.number_input(
                    "Percentage of Tokens (%)",
                    min_value=0.001,
                    max_value=100.0,
                    value=1.0,
                    step=0.1,
                    format="%.3f",
                    help="Enter the percentage of total tokens for this tranche"
                )
            with col6:
                # Calculate absolute tokens (will be done in calculation)
                st.info("Absolute token count will be calculated automatically")
                token_count = None
        else:
            with col5:
                token_count = st.number_input(
                    "Number of Tokens",
                    min_value=1,
                    value=1000,
                    step=100,
                    help="Enter the exact number of tokens for this tranche"
                )
            with col6:
                # Calculate percentage (will be done in calculation)
                st.info("Percentage will be calculated automatically")
                token_percentage = None
        
        # Time calculations
        time_to_expiration = (loan_duration - start_month) / 12.0
        st.info(f"**Time to Expiration:** {time_to_expiration:.2f} years (from month {start_month} to {loan_duration})")
        
        if st.form_submit_button("Add Tranche", use_container_width=True):
            new_tranche = {
                'entity': selected_entity,
                'option_type': option_type,
                'loan_duration': loan_duration,
                'start_month': start_month,
                'time_to_expiration': time_to_expiration,
                'strike_price': strike_price,
                'allocation_method': allocation_method,
                'token_percentage': token_percentage,
                'token_count': token_count
            }
            st.session_state.tranches_data.append(new_tranche)
            
            if allocation_method == "Percentage of Total Tokens":
                st.success(f"Added {option_type} option for {selected_entity} ({token_percentage}% of tokens)")
            else:
                st.success(f"Added {option_type} option for {selected_entity} ({token_count:,} tokens)")
            st.rerun()

def display_phase_navigation():
    """Display phase navigation"""
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        if st.session_state.current_phase > 1:
            prev_phase = st.session_state.current_phase - 1
            if st.button(f"Phase {prev_phase}", use_container_width=True):
                st.session_state.current_phase = prev_phase
                st.rerun()
    
    with col2:
        # Phase indicator
        if st.session_state.current_phase == 1:
            st.markdown("**Phase 1: Entity Setup** → Phase 2: Tranche Setup → Phase 3: Quoting Depths")
        elif st.session_state.current_phase == 2:
            st.markdown("Phase 1: Entity Setup → **Phase 2: Tranche Setup** → Phase 3: Quoting Depths")
        else:
            st.markdown("Phase 1: Entity Setup → Phase 2: Tranche Setup → **Phase 3: Quoting Depths**")
    
    with col3:
        can_advance = False
        if st.session_state.current_phase == 1 and len(st.session_state.entities_data) > 0:
            can_advance = True
        elif st.session_state.current_phase == 2 and len(st.session_state.tranches_data) > 0:
            can_advance = True
        
        if can_advance and st.session_state.current_phase < 3:
            next_phase = st.session_state.current_phase + 1
            if st.button(f"Phase {next_phase}", use_container_width=True):
                st.session_state.current_phase = next_phase
                st.rerun()

def phase_3_quoting_depths():
    """Phase 3: Quoting Depths Configuration"""
    st.markdown("## Phase 3: Quoting Depths")
    
    if not st.session_state.tranches_data:
        st.warning("No tranches configured. Please complete Phase 2 first.")
        if st.button("Back to Phase 2"):
            st.session_state.current_phase = 2
            st.rerun()
        return
    
    st.markdown("### Configure exchange quoting depths for each entity")
    st.info("Each entity must provide liquidity depth information across different exchanges.")
    
    # Get unique entities from tranches
    entities = list(set(tranche['entity'] for tranche in st.session_state.tranches_data))
    
    # Predefined exchanges
    exchanges = [
        "Binance", "OKX", "Coinbase", "Bybit", "KuCoin", 
        "MEXC", "Gate", "Bitvavo", "Bitget", "Other"
    ]
    
    with st.form("quoting_depths_form"):
        st.markdown("**Add Quoting Depth Entry**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            selected_entity = st.selectbox("Select Entity", entities)
        
        with col2:
            selected_exchange = st.selectbox("Exchange", exchanges)
        
        # Quoting depth inputs
        st.markdown("**Market Depth Information**")
        col3, col4, col5, col6 = st.columns(4)
        
        with col3:
            bid_ask_spread = st.number_input(
                "Bid/Ask Spread (bps)",
                min_value=0.0,
                max_value=1000.0,
                value=10.0,
                step=0.1,
                format="%.1f",
                help="Bid-ask spread in basis points"
            )
        
        with col4:
            depth_50bps = st.number_input(
                "Depth @ 50bps ($)",
                min_value=0.0,
                value=50000.0,
                step=1000.0,
                format="%.0f",
                help="Liquidity depth at 50 basis points"
            )
        
        with col5:
            depth_100bps = st.number_input(
                "Depth @ 100bps ($)",
                min_value=0.0,
                value=100000.0,
                step=1000.0,
                format="%.0f",
                help="Liquidity depth at 100 basis points"
            )
        
        with col6:
            depth_200bps = st.number_input(
                "Depth @ 200bps ($)",
                min_value=0.0,
                value=200000.0,
                step=1000.0,
                format="%.0f",
                help="Liquidity depth at 200 basis points"
            )
        
        if st.form_submit_button("Add Quoting Depth", use_container_width=True):
            # Check if this entity-exchange combination already exists
            existing_entry = next((
                entry for entry in st.session_state.quoting_depths_data 
                if entry['entity'] == selected_entity and entry['exchange'] == selected_exchange
            ), None)
            
            if existing_entry:
                st.warning(f"Entry for {selected_entity} on {selected_exchange} already exists. Please delete the existing entry first.")
            else:
                new_entry = {
                    'entity': selected_entity,
                    'exchange': selected_exchange,
                    'bid_ask_spread': bid_ask_spread,
                    'depth_50bps': depth_50bps,
                    'depth_100bps': depth_100bps,
                    'depth_200bps': depth_200bps
                }
                st.session_state.quoting_depths_data.append(new_entry)
                st.success(f"Added quoting depth for {selected_entity} on {selected_exchange}")
                st.rerun()

def display_quoting_depths_table():
    """Display current quoting depths in an editable table"""
    if st.session_state.quoting_depths_data:
        st.markdown("### Current Quoting Depths")
        
        # Sorting options
        col1, col2 = st.columns([1, 2])
        
        with col1:
            sort_option = st.selectbox(
                "Sort by:",
                ["Original Order", "Entity (A-Z)", "Exchange (A-Z)", "Bid/Ask Spread"],
                key="depths_sort_option"
            )
        
        # Sort the data based on selection
        sorted_data = st.session_state.quoting_depths_data.copy()
        
        if sort_option == "Entity (A-Z)":
            sorted_data.sort(key=lambda x: x['entity'])
        elif sort_option == "Exchange (A-Z)":
            sorted_data.sort(key=lambda x: x['exchange'])
        elif sort_option == "Bid/Ask Spread":
            sorted_data.sort(key=lambda x: x['bid_ask_spread'])
        
        # Create DataFrame
        df = pd.DataFrame(sorted_data)
        df['Row #'] = range(1, len(df) + 1)
        
        # Reorder columns
        cols = ['Row #', 'entity', 'exchange', 'bid_ask_spread', 'depth_50bps', 'depth_100bps', 'depth_200bps']
        df = df[cols]
        
        # Display table
        st.dataframe(
            df,
            use_container_width=True,
            column_config={
                "Row #": st.column_config.NumberColumn("Row #", format="%d", width="small"),
                "entity": "Entity",
                "exchange": "Exchange",
                "bid_ask_spread": st.column_config.NumberColumn("B/A Spread (bps)", format="%.1f"),
                "depth_50bps": st.column_config.NumberColumn("Depth @ 50bps ($)", format="$%.0f"),
                "depth_100bps": st.column_config.NumberColumn("Depth @ 100bps ($)", format="$%.0f"),
                "depth_200bps": st.column_config.NumberColumn("Depth @ 200bps ($)", format="$%.0f")
            }
        )
        
        # Row deletion section
        st.markdown("### Delete Specific Rows")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if len(sorted_data) > 0:
                row_options = []
                for i, entry in enumerate(sorted_data, 1):
                    row_options.append(f"Row {i}: {entry['entity']} - {entry['exchange']} (Spread: {entry['bid_ask_spread']:.1f}bps)")
                
                selected_rows = st.multiselect(
                    "Select rows to delete:",
                    options=range(len(row_options)),
                    format_func=lambda x: row_options[x],
                    key="depths_rows_to_delete"
                )
        
        with col2:
            if st.button("Delete Selected Rows", type="secondary", use_container_width=True):
                if selected_rows:
                    # Remove selected rows (in reverse order to maintain indices)
                    for row_idx in sorted(selected_rows, reverse=True):
                        entry_to_remove = sorted_data[row_idx]
                        original_idx = next(i for i, e in enumerate(st.session_state.quoting_depths_data) if e == entry_to_remove)
                        st.session_state.quoting_depths_data.pop(original_idx)
                    
                    st.success(f"Deleted {len(selected_rows)} row(s)")
                    st.rerun()
                else:
                    st.warning("Please select rows to delete")
        
        # Management buttons
        st.markdown("### Data Management")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Clear All Depths", use_container_width=True):
                st.session_state.quoting_depths_data = []
                st.rerun()
        
        with col2:
            # Check if all entities have at least one entry
            entities_with_depths = set(entry['entity'] for entry in st.session_state.quoting_depths_data)
            required_entities = set(tranche['entity'] for tranche in st.session_state.tranches_data)
            missing_entities = required_entities - entities_with_depths
            
            if missing_entities:
                st.error(f"Missing quoting depths for: {', '.join(missing_entities)}")
            else:
                st.success("All entities have quoting depth data")
        
        with col3:
            # Summary info
            total_entries = len(st.session_state.quoting_depths_data)
            unique_entities = len(set(e['entity'] for e in st.session_state.quoting_depths_data))
            st.info(f"**{total_entries}** entries\\n**{unique_entities}** entities")

def display_tranches_table():
    """Display current tranches in an editable table"""
    if st.session_state.tranches_data:
        st.markdown("## Current Tranches")
        
        # Sorting and management options
        col1, col2 = st.columns([1, 2])
        
        with col1:
            sort_option = st.selectbox(
                "Sort by:",
                ["Original Order", "Entity (A-Z)", "Entity (Z-A)", "Strike Price", "Start Month"],
                key="sort_option"
            )
        
        with col2:
            st.markdown("**Row Management:**")
        
        # Sort the data based on selection
        sorted_data = st.session_state.tranches_data.copy()
        
        if sort_option == "Entity (A-Z)":
            sorted_data.sort(key=lambda x: x['entity'])
        elif sort_option == "Entity (Z-A)":
            sorted_data.sort(key=lambda x: x['entity'], reverse=True)
        elif sort_option == "Strike Price":
            sorted_data.sort(key=lambda x: x['strike_price'])
        elif sort_option == "Start Month":
            sorted_data.sort(key=lambda x: x['start_month'])
        
        # Create DataFrame with row numbers for selection
        df = pd.DataFrame(sorted_data)
        df['Row #'] = range(1, len(df) + 1)
        
        # Reorder columns to put Row # first
        cols = ['Row #'] + [col for col in df.columns if col != 'Row #']
        df = df[cols]
        
        # Display as table
        st.dataframe(
            df,
            use_container_width=True,
            column_config={
                "Row #": st.column_config.NumberColumn(
                    "Row #",
                    format="%d",
                    width="small"
                ),
                "entity": "Entity",
                "option_type": "Type",
                "loan_duration": st.column_config.NumberColumn(
                    "Loan Duration (months)",
                    format="%d"
                ),
                "start_month": st.column_config.NumberColumn(
                    "Start Month",
                    format="%d"
                ),
                "strike_price": st.column_config.NumberColumn(
                    "Strike Price ($)",
                    format="%.4f"
                ),
                "allocation_method": "Allocation Method",
                "token_percentage": st.column_config.NumberColumn(
                    "Token Share (%)",
                    format="%.3f"
                ),
                "token_count": st.column_config.NumberColumn(
                    "Token Count",
                    format="%.0f"
                ),
                "time_to_expiration": st.column_config.NumberColumn(
                    "Time to Exp (years)",
                    format="%.2f"
                )
            }
        )
        
        # Row deletion section
        st.markdown("### Delete Specific Rows")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Multi-select for row deletion
            if len(sorted_data) > 0:
                row_options = []
                for i, tranche in enumerate(sorted_data, 1):
                    if tranche['allocation_method'] == "Percentage of Total Tokens":
                        allocation_info = f"{tranche['token_percentage']:.1f}%"
                    else:
                        allocation_info = f"{tranche['token_count']:,} tokens"
                    row_options.append(f"Row {i}: {tranche['entity']} - {tranche['option_type'].upper()} @ ${tranche['strike_price']:.2f} ({allocation_info})")
                
                selected_rows = st.multiselect(
                    "Select rows to delete:",
                    options=range(len(row_options)),
                    format_func=lambda x: row_options[x],
                    key="rows_to_delete"
                )
        
        with col2:
            if st.button("Delete Selected Rows", type="secondary", use_container_width=True):
                if selected_rows:
                    # Remove selected rows (in reverse order to maintain indices)
                    for row_idx in sorted(selected_rows, reverse=True):
                        # Find the original index in unsorted data
                        tranche_to_remove = sorted_data[row_idx]
                        original_idx = next(i for i, t in enumerate(st.session_state.tranches_data) if t == tranche_to_remove)
                        st.session_state.tranches_data.pop(original_idx)
                    
                    st.success(f"Deleted {len(selected_rows)} row(s)")
                    st.session_state.calculation_results = None  # Reset calculations
                    st.rerun()
                else:
                    st.warning("Please select rows to delete")
        
        # Management buttons
        st.markdown("### Data Management")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("Clear All", use_container_width=True):
                st.session_state.tranches_data = []
                st.session_state.calculation_results = None
                st.rerun()
        
        with col2:
            if st.button("Export JSON", use_container_width=True):
                export_data = {
                    'entities': st.session_state.entities_data,
                    'tranches': st.session_state.tranches_data,
                    'quoting_depths': st.session_state.quoting_depths_data,
                    'timestamp': datetime.now().isoformat()
                }
                st.download_button(
                    label="Download JSON",
                    data=json.dumps(export_data, indent=2),
                    file_name=f"option_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
        
        with col3:
            uploaded_file = st.file_uploader(
                "Import JSON",
                type="json",
                key="import_json"
            )
            if uploaded_file is not None:
                try:
                    data = json.load(uploaded_file)
                    if 'tranches' in data:
                        st.session_state.tranches_data = data['tranches']
                        if 'entities' in data:
                            st.session_state.entities_data = data['entities']
                        if 'quoting_depths' in data:
                            st.session_state.quoting_depths_data = data['quoting_depths']
                        st.success("Data imported successfully!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error importing file: {e}")
        
        with col4:
            # Summary info
            total_tranches = len(st.session_state.tranches_data)
            unique_entities = len(set(t['entity'] for t in st.session_state.tranches_data))
            st.info(f"**{total_tranches}** tranches\n**{unique_entities}** entities")

def calculate_options(params):
    """Calculate option values and display results"""
    if not st.session_state.tranches_data:
        st.warning("Please add at least one tranche before calculating.")
        return
    
    st.markdown("## Calculate Options")
    
    if st.button("Calculate All Options", type="primary", use_container_width=True):
        with st.spinner("Calculating option values..."):
            results = perform_calculations(params)
            st.session_state.calculation_results = results
            st.success("Calculations completed!")
            st.rerun()

def perform_calculations(params):
    """Perform Black-Scholes calculations"""
    results = {
        'tranches': [],
        'entities': {},
        'total_portfolio_value': 0
    }
    
    for tranche in st.session_state.tranches_data:
        S = params['token_price']
        K = tranche['strike_price']
        T = tranche['time_to_expiration']
        r = params['risk_free_rate']
        sigma = params['volatility']
        
        # Calculate number of tokens and percentage based on allocation method
        if tranche['allocation_method'] == "Percentage of Total Tokens":
            num_tokens = (tranche['token_percentage'] / 100.0) * params['total_tokens']
            token_percentage = tranche['token_percentage']
        else:  # Absolute Token Count
            num_tokens = tranche['token_count']
            token_percentage = (num_tokens / params['total_tokens']) * 100.0
        
        # Calculate option price per token
        if tranche['option_type'] == 'call':
            option_price = black_scholes_call(S, K, T, r, sigma)
        else:
            option_price = black_scholes_put(S, K, T, r, sigma)
        
        # Total value of this tranche
        total_value = option_price * num_tokens
        results['total_portfolio_value'] += total_value
        
        # Calculate Greeks
        greeks = calculate_greeks(S, K, T, r, sigma)
        
        tranche_result = {
            **tranche,
            'num_tokens': num_tokens,
            'token_percentage': token_percentage,
            'option_price_per_token': option_price,
            'total_value': total_value,
            'greeks': greeks
        }
        
        results['tranches'].append(tranche_result)
        
        # Group by entity
        entity = tranche['entity']
        if entity not in results['entities']:
            results['entities'][entity] = []
        results['entities'][entity].append(tranche_result)
    
    return results

def display_results(params):
    """Display calculation results"""
    if st.session_state.calculation_results is None:
        return
    
    results = st.session_state.calculation_results
    
    st.markdown("## Results")
    
    # Portfolio Summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total Portfolio Value",
            f"${results['total_portfolio_value']:,.0f}",
            delta=None
        )
    
    with col2:
        portfolio_percentage = (results['total_portfolio_value'] / params['total_valuation']) * 100
        st.metric(
            "Portfolio as % of Total Valuation",
            f"{portfolio_percentage:.2f}%",
            delta=None
        )
    
    with col3:
        st.metric(
            "Number of Entities",
            len(results['entities']),
            delta=None
        )
    
    # Entity Breakdown
    st.markdown("### Entity Breakdown")
    
    entity_summary = []
    for entity, tranches in results['entities'].items():
        total_value = sum(t['total_value'] for t in tranches)
        entity_percentage = (total_value / params['total_valuation']) * 100
        total_token_share = sum(t['token_percentage'] for t in tranches)
        
        entity_summary.append({
            'Entity': entity,
            'Total Value': f"${total_value:,.0f}",
            '% of Valuation': f"{entity_percentage:.2f}%",
            'Token Share (%)': f"{total_token_share:.3f}%",
            'Tranches': len(tranches)
        })
    
    st.dataframe(pd.DataFrame(entity_summary), use_container_width=True)
    
    # Detailed Results
    with st.expander("Detailed Tranche Results"):
        detailed_df = pd.DataFrame([
            {
                'Entity': t['entity'],
                'Type': t['option_type'].upper(),
                'Loan Duration': f"{t['loan_duration']} months",
                'Start Month': t['start_month'],
                'Strike': f"${t['strike_price']:.4f}",
                'Token Share (%)': f"{t['token_percentage']:.3f}%",
                'Num Tokens': f"{t['num_tokens']:,.0f}",
                'Price/Token': f"${t['option_price_per_token']:.6f}",
                'Total Value': f"${t['total_value']:.2f}",
                'Delta': f"{t['greeks']['delta_call' if t['option_type'] == 'call' else 'delta_put']:.4f}",
                'Gamma': f"{t['greeks']['gamma']:.4f}",
                'Vega': f"{t['greeks']['vega']:.4f}"
            }
            for t in results['tranches']
        ])
        
        st.dataframe(detailed_df, use_container_width=True)
    
    # Charts
    display_charts(results)

def display_charts(results):
    """Create and display matplotlib charts"""
    st.markdown("### Entity Option Values Chart")
    
    if len(results['entities']) == 0:
        return
    
    # Prepare data for stacked bar chart
    entities = list(results['entities'].keys())
    entity_data = {}
    
    for entity, tranches in results['entities'].items():
        entity_data[entity] = [t['total_value'] for t in tranches]
    
    # Create matplotlib figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Generate colors
    colors = plt.cm.Set3(np.linspace(0, 1, max(len(tranches) for tranches in results['entities'].values())))
    
    # Create stacked bars
    bottoms = {entity: 0 for entity in entities}
    
    for entity_idx, (entity, tranches) in enumerate(results['entities'].items()):
        bottom = 0
        entity_total = sum(t['total_value'] for t in tranches)
        
        for tranche_idx, tranche in enumerate(tranches):
            value = tranche['total_value']
            
            # Create bar segment
            bar = ax.bar(entity_idx, value, bottom=bottom, 
                        color=colors[tranche_idx % len(colors)], 
                        alpha=0.8,
                        label=f"Tranche {tranche_idx+1}" if entity_idx == 0 else "")
            
            # Add value label if segment is large enough
            if value > entity_total * 0.05:
                ax.text(entity_idx, bottom + value/2, f'${value:.0f}', 
                       ha='center', va='center', fontweight='bold', 
                       fontsize=9, color='black')
            
            bottom += value
        
        # Add total value at top
        ax.text(entity_idx, entity_total * 1.01, f'${entity_total:.0f}', 
               ha='center', va='bottom', fontweight='bold', fontsize=12)
    
    # Customize chart
    ax.set_xlabel('Entities', fontweight='bold', fontsize=12)
    ax.set_ylabel('Option Value ($)', fontweight='bold', fontsize=12)
    ax.set_title('Option Values by Entity\n(Stacked Individual Option Values)', 
                fontweight='bold', fontsize=14)
    ax.set_xticks(range(len(entities)))
    ax.set_xticklabels(entities, fontsize=11, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    # Format y-axis
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # Add legend
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        ax.legend(handles, labels, bbox_to_anchor=(1.05, 1), loc='upper left', 
                 fontsize=9, title="Tranches", title_fontsize=10)
    
    plt.tight_layout()
    
    # Display in Streamlit
    st.pyplot(fig)
    plt.close()

def main():
    """Main Streamlit application"""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">Options Pricing Calculator</h1>', unsafe_allow_html=True)
    
    # Get base parameters from sidebar
    params = create_sidebar()
    
    # Phase Navigation
    display_phase_navigation()
    
    # Main content based on current phase
    if st.session_state.current_phase == 1:
        # Phase 1: Entity Setup
        phase_1_entity_setup()
        
    elif st.session_state.current_phase == 2:
        # Phase 2: Tranche Setup
        col1, col2 = st.columns([1, 1])
        
        with col1:
            phase_2_tranche_setup()
        
        with col2:
            display_tranches_table()
    
    else:  # Phase 3
        # Phase 3: Quoting Depths
        col1, col2 = st.columns([1, 1])
        
        with col1:
            phase_3_quoting_depths()
        
        with col2:
            display_quoting_depths_table()
        
        # Calculation section (only show if tranches exist and all entities have quoting depths)
        if st.session_state.tranches_data:
            # Check if all entities have quoting depth data
            entities_with_depths = set(entry['entity'] for entry in st.session_state.quoting_depths_data)
            required_entities = set(tranche['entity'] for tranche in st.session_state.tranches_data)
            
            if required_entities.issubset(entities_with_depths):
                calculate_options(params)
                display_results(params)
            else:
                st.warning("Please add quoting depths for all entities before calculating options.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p><strong>Options Pricing Calculator</strong> | Built with Streamlit & Black-Scholes Model</p>
            <p><em>Real-time option valuation with entity-based portfolio analysis</em></p>
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
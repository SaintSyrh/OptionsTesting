"""
Modular Options Pricing Calculator - Refactored with clean architecture
This file serves as the main entry point using modularized components
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Import modular components
from config.settings import APP_TITLE, PAGE_LAYOUT, INITIAL_SIDEBAR_STATE
from config.styles import MAIN_CSS, FOOTER_HTML
from utils.logging_config import get_logger
from utils.error_handling import error_handler_instance, ui_handler, ErrorHandler
from app.session_state import session_manager
from app.calculations import calculation_orchestrator
from ui.sidebar import sidebar_manager
from ui.phase_navigation import phase_nav_manager
from ui.entity_setup import entity_setup_manager

# Existing imports for backward compatibility
from option_pricing import black_scholes_call, black_scholes_put, calculate_greeks
from depth_valuation import DepthValuationModels, generate_trade_size_distribution
from crypto_depth_calculator import CryptoEffectiveDepthCalculator

logger = get_logger(__name__)


class ModularOptionsApp:
    """Main application class with modular components"""
    
    def __init__(self):
        self.session_manager = session_manager
        self.calculation_orchestrator = calculation_orchestrator
        self.sidebar_manager = sidebar_manager
        self.phase_nav_manager = phase_nav_manager
        self.entity_setup_manager = entity_setup_manager
        
        # Initialize session state
        self.session_manager.initialize_session_state()
        logger.info("Modular Options App initialized")
    
    @ui_handler
    def setup_page_config(self) -> None:
        """Setup Streamlit page configuration"""
        st.set_page_config(
            page_title=APP_TITLE,
            layout=PAGE_LAYOUT,
            initial_sidebar_state=INITIAL_SIDEBAR_STATE
        )
        
        # Apply custom CSS
        st.markdown(MAIN_CSS, unsafe_allow_html=True)
        logger.debug("Page configuration and styling applied")
    
    @ui_handler
    def display_header(self) -> None:
        """Display application header"""
        st.markdown(f'<h1 class="main-header">{APP_TITLE}</h1>', unsafe_allow_html=True)
    
    @ui_handler
    def display_footer(self) -> None:
        """Display application footer"""
        st.markdown("---")
        st.markdown(FOOTER_HTML, unsafe_allow_html=True)
    
    def run(self) -> None:
        """Main application run method"""
        try:
            logger.info("Starting Options Pricing Calculator")
            
            # Setup page
            self.setup_page_config()
            self.display_header()
            
            # Get base parameters from sidebar
            params = self.sidebar_manager.create_sidebar()
            logger.debug(f"Base parameters: {params}")
            
            # Display phase navigation
            self.phase_nav_manager.display_phase_navigation()
            
            # Main content based on current phase
            current_phase = self.session_manager.get_current_phase()
            self.display_phase_content(current_phase, params)
            
            # Display footer
            self.display_footer()
            
            logger.debug("Application run completed successfully")
            
        except Exception as e:
            logger.error(f"Error in main application: {e}")
            st.error("An unexpected error occurred. Please check the logs.")
    
    def display_phase_content(self, phase: int, params: Dict[str, float]) -> None:
        """Display content based on current phase"""
        try:
            if phase == 1:
                self.display_phase_1(params)
            elif phase == 2:
                self.display_phase_2(params)
            elif phase == 3:
                self.display_phase_3(params)
            else:
                st.error(f"Invalid phase: {phase}")
                
        except Exception as e:
            logger.error(f"Error displaying phase {phase} content: {e}")
            st.error(f"Error displaying Phase {phase} content")
    
    @ui_handler
    def display_phase_1(self, params: Dict[str, float]) -> None:
        """Display Phase 1: Entity Setup"""
        self.entity_setup_manager.display_phase_1_entity_setup()
    
    @ui_handler
    def display_phase_2(self, params: Dict[str, float]) -> None:
        """Display Phase 2: Tranche Setup"""
        col1, col2 = st.columns([1, 1])
        
        with col1:
            self.display_phase_2_tranche_setup(params)
        
        with col2:
            self.display_tranches_table()
    
    @ui_handler 
    def display_phase_3(self, params: Dict[str, float]) -> None:
        """Display Phase 3: Quoting Depths and Calculations"""
        col1, col2 = st.columns([1, 1])
        
        with col1:
            self.display_phase_3_quoting_depths(params)
        
        with col2:
            self.display_quoting_depths_table()
        
        # Calculation section
        if self.session_manager.get_tranches():
            entities_with_depths = self.session_manager.get_entities_with_depths()
            required_entities = self.session_manager.get_required_entities()
            
            if required_entities.issubset(entities_with_depths):
                # All entities have depths - show calculations
                self.display_calculations_section(params)
            else:
                missing_entities = required_entities - entities_with_depths
                st.warning(f"Please add quoting depths for all entities before calculating options. Missing: {', '.join(missing_entities)}")
    
    def display_phase_2_tranche_setup(self, params: Dict[str, float]) -> None:
        """Display Phase 2 tranche setup (legacy implementation for now)"""
        st.markdown("## Phase 2: Tranche Configuration")
        
        if not self.session_manager.get_entities():
            st.warning("No entities configured. Please go back to Phase 1.")
            if st.button("Back to Phase 1"):
                self.session_manager.set_current_phase(1)
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
                entities = self.session_manager.get_entities()
                entity_names = [e['name'] for e in entities]
                selected_entity = st.selectbox("Select Entity", entity_names)
                
                # Get loan duration for selected entity
                entity_info = next(e for e in entities if e['name'] == selected_entity)
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
            
            # Token Allocation
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
                
                if self.session_manager.add_tranche(new_tranche):
                    if allocation_method == "Percentage of Total Tokens":
                        st.success(f"Added {option_type} option for {selected_entity} ({token_percentage}% of tokens)")
                    else:
                        st.success(f"Added {option_type} option for {selected_entity} ({token_count:,} tokens)")
                    st.rerun()
                else:
                    st.error("Failed to add tranche")
    
    def display_phase_3_quoting_depths(self, params: Dict[str, float]) -> None:
        """Display Phase 3 quoting depths setup (legacy implementation for now)"""
        st.markdown("## Phase 3: Quoting Depths")
        
        if not self.session_manager.get_tranches():
            st.warning("No tranches configured. Please complete Phase 2 first.")
            if st.button("Back to Phase 2"):
                self.session_manager.set_current_phase(2)
                st.rerun()
            return
        
        st.markdown("### Configure exchange quoting depths for each entity")
        st.info("Each entity must provide liquidity depth information across different exchanges.")
        
        # Get unique entities from tranches
        tranches = self.session_manager.get_tranches()
        entities = list(set(tranche['entity'] for tranche in tranches))
        
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
            
            # Bid/Ask Spread
            st.markdown("**Market Depth Information**")
            col3, col4 = st.columns(2)
            
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
                # Get entity's loan value for percentage calculations
                entities_data = self.session_manager.get_entities()
                entity_info = next(e for e in entities_data if e['name'] == selected_entity)
                entity_tranches = [t for t in tranches if t['entity'] == selected_entity]
                
                if entity_tranches:
                    # Calculate total entity loan value (simplified)
                    total_entity_value = sum(
                        (t.get('token_percentage', 0) / 100.0 if t.get('token_percentage') else 
                         (t.get('token_count', 0) / 100000.0)) * 1000000  # Rough estimate
                        for t in entity_tranches
                    )
                    st.info(f"**Entity Loan Value:** ${total_entity_value:,.0f} (estimated)")
                else:
                    total_entity_value = 1000000  # Default fallback
                    st.info("**Entity Loan Value:** Not calculated yet")
            
            # Depth input method selection
            st.markdown("**Depth Quoting Method:**")
            depth_method = st.radio(
                "Choose depth input method:",
                ["Absolute Values ($)", "Percentage of Loan Value (%)"],
                horizontal=True,
                key="depth_method_selector"
            )
            
            # Depth inputs based on method
            st.markdown("**Liquidity Depths:**")
            col5, col6, col7 = st.columns(3)
            
            if depth_method == "Absolute Values ($)":
                with col5:
                    depth_50bps = st.number_input(
                        "Depth @ 50bps ($)",
                        min_value=0.0,
                        value=50000.0,
                        step=1000.0,
                        format="%.0f",
                        help="Absolute liquidity depth at 50 basis points"
                    )
                    depth_50bps_pct = None
                
                with col6:
                    depth_100bps = st.number_input(
                        "Depth @ 100bps ($)",
                        min_value=0.0,
                        value=100000.0,
                        step=1000.0,
                        format="%.0f",
                        help="Absolute liquidity depth at 100 basis points"
                    )
                    depth_100bps_pct = None
                
                with col7:
                    depth_200bps = st.number_input(
                        "Depth @ 200bps ($)",
                        min_value=0.0,
                        value=200000.0,
                        step=1000.0,
                        format="%.0f",
                        help="Absolute liquidity depth at 200 basis points"
                    )
                    depth_200bps_pct = None
            
            else:  # Percentage method
                with col5:
                    depth_50bps_pct = st.number_input(
                        "Depth @ 50bps (%)",
                        min_value=0.0,
                        max_value=100.0,
                        value=5.0,
                        step=0.1,
                        format="%.1f",
                        help="Liquidity depth as percentage of loan value"
                    )
                    depth_50bps = (depth_50bps_pct / 100.0) * total_entity_value
                
                with col6:
                    depth_100bps_pct = st.number_input(
                        "Depth @ 100bps (%)",
                        min_value=0.0,
                        max_value=100.0,
                        value=10.0,
                        step=0.1,
                        format="%.1f",
                        help="Liquidity depth as percentage of loan value"
                    )
                    depth_100bps = (depth_100bps_pct / 100.0) * total_entity_value
                
                with col7:
                    depth_200bps_pct = st.number_input(
                        "Depth @ 200bps (%)",
                        min_value=0.0,
                        max_value=100.0,
                        value=20.0,
                        step=0.1,
                        format="%.1f",
                        help="Liquidity depth as percentage of loan value"
                    )
                    depth_200bps = (depth_200bps_pct / 100.0) * total_entity_value
            
            # Show calculated values
            if depth_method == "Percentage of Loan Value (%)":
                st.info(f"**Calculated Depths:** 50bps: ${depth_50bps:,.0f}, 100bps: ${depth_100bps:,.0f}, 200bps: ${depth_200bps:,.0f}")
            
            if st.form_submit_button("Add Quoting Depth", use_container_width=True):
                # Check if this entity-exchange combination already exists
                existing_depths = self.session_manager.get_quoting_depths()
                existing_entry = next((
                    entry for entry in existing_depths 
                    if entry['entity'] == selected_entity and entry['exchange'] == selected_exchange
                ), None)
                
                if existing_entry:
                    st.warning(f"Entry for {selected_entity} on {selected_exchange} already exists. Please delete the existing entry first.")
                else:
                    new_entry = {
                        'entity': selected_entity,
                        'exchange': selected_exchange,
                        'bid_ask_spread': bid_ask_spread,
                        'depth_method': depth_method,
                        'depth_50bps': depth_50bps,
                        'depth_100bps': depth_100bps,
                        'depth_200bps': depth_200bps,
                        'depth_50bps_pct': depth_50bps_pct,
                        'depth_100bps_pct': depth_100bps_pct,
                        'depth_200bps_pct': depth_200bps_pct,
                        'entity_loan_value': total_entity_value
                    }
                    
                    if self.session_manager.add_quoting_depth(new_entry):
                        st.success(f"Added quoting depth for {selected_entity} on {selected_exchange}")
                        st.rerun()
                    else:
                        st.error("Failed to add quoting depth")
    
    def display_calculations_section(self, params: Dict[str, float]) -> None:
        """Display calculations and results section"""
        try:
            # Display depth value analysis
            self.display_depth_value_analysis(params)
            
            # Options calculations
            st.markdown("## Calculate Options")
            
            if st.button("Calculate All Options", type="primary", use_container_width=True):
                with st.spinner("Calculating option values..."):
                    results = self.calculation_orchestrator.perform_options_calculations(params)
                    self.session_manager.set_calculation_results(results)
                    st.success("Calculations completed!")
                    st.rerun()
            
            # Display results if available
            self.display_results(params)
            
        except Exception as e:
            ErrorHandler.handle_error(e, "Calculations Section")
    
    def display_depth_value_analysis(self, params: Dict[str, float]) -> None:
        """Display depth value analysis (legacy implementation for now)"""
        try:
            analysis = self.calculation_orchestrator.calculate_depth_value_analysis(params)
            
            if not analysis:
                return
            
            # Display advanced market maker valuation first
            if analysis.get('advanced_valuation'):
                self.display_advanced_mm_valuation(analysis['advanced_valuation'])
                st.markdown("---")
            
            st.markdown("## Crypto-Optimized Depth Value Analysis")
            st.markdown("*Advanced effective depth calculation using empirically-tuned crypto market factors*")
            
            st.info("🚀 **Now Using:** Crypto-empirical depth calculation with exchange tiers, volatility optimization, spread bonuses, liquidity bonuses, MEV adjustments, and cascade protection!")
            
            # Overall metrics
            overall = analysis['overall_metrics']
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Quoted Value",
                    f"${overall['total_quoted_value']:,.0f}",
                    help="Sum of all liquidity depths across entities and exchanges"
                )
            
            with col2:
                st.metric(
                    "Effective Value",
                    f"${overall['total_effective_value']:,.0f}",
                    help="Adjusted value considering volatility and depth tier drop-offs"
                )
            
            with col3:
                efficiency_pct = overall['overall_efficiency'] * 100
                st.metric(
                    "Overall Efficiency",
                    f"{efficiency_pct:.1f}%",
                    help="Ratio of effective value to quoted value"
                )
            
            with col4:
                vol_adj_pct = overall['volatility_adjustment'] * 100
                st.metric(
                    "Volatility Adjustment",
                    f"{vol_adj_pct:.1f}%",
                    help="Value reduction due to asset volatility"
                )
            
            # Entity-level analysis
            st.markdown("### Entity Analysis")
            
            entity_summary = []
            for entity_name, entity_data in analysis['entity_analyses'].items():
                efficiency = (entity_data['effective_quoted_value'] / entity_data['total_quoted_value'] 
                             if entity_data['total_quoted_value'] > 0 else 0)
                
                entity_summary.append({
                    'Entity': entity_name,
                    'Exchanges': len(entity_data['exchanges']),
                    'Total Quoted ($)': f"${entity_data['total_quoted_value']:,.0f}",
                    'Effective Value ($)': f"${entity_data['effective_quoted_value']:,.0f}",
                    'Efficiency (%)': f"{efficiency*100:.1f}%",
                    'Depth @ 50bps ($)': f"${entity_data['depth_distribution']['50bps']:,.0f}",
                    'Depth @ 100bps ($)': f"${entity_data['depth_distribution']['100bps']:,.0f}",
                    'Depth @ 200bps ($)': f"${entity_data['depth_distribution']['200bps']:,.0f}"
                })
            
            st.dataframe(pd.DataFrame(entity_summary), use_container_width=True)
            
            # Add depth-to-options ratio visualization if option calculations exist
            if self.session_manager.get_calculation_results():
                st.markdown("---")
                ratio_data = self.calculation_orchestrator.calculate_depth_options_ratio(params)
                if ratio_data:
                    self.display_depth_options_graph(ratio_data)
                    
                    # Summary table for depth/options ratios
                    st.markdown("### Depth-to-Options Ratio Summary")
                    ratio_summary = []
                    for entity, data in ratio_data.items():
                        ratio_summary.append({
                            'Entity': entity,
                            'Option Value': f"${data['option_value']:,.0f}",
                            'Total Depth': f"${data['total_depth_value']:,.0f}",
                            'Effective Depth': f"${data['effective_depth_value']:,.0f}",
                            'Market Maker Value': f"${data['market_maker_value']:,.0f}",
                            'Depth/Option Ratio': f"{data['depth_to_option_ratio']:.2f}x",
                            'Effective Ratio': f"{data['effective_depth_to_option_ratio']:.2f}x",
                            'MM/Option Ratio': f"{data['mm_to_option_ratio']:.2f}x",
                            'Depth Coverage %': f"{data['depth_coverage_percentage']:.0f}%",
                            'Effective Coverage %': f"{data['effective_coverage_percentage']:.0f}%",
                            'MM Coverage %': f"{data['mm_coverage_percentage']:.0f}%"
                        })
                    st.dataframe(pd.DataFrame(ratio_summary), use_container_width=True)
            
        except Exception as e:
            ErrorHandler.handle_error(e, "Depth Value Analysis")
    
    # Include remaining legacy implementations for now (to be modularized later)
    def display_tranches_table(self):
        """Display tranches table (legacy implementation)"""
        # This would be extracted to ui.tranche_table module
        tranches = self.session_manager.get_tranches()
        if tranches:
            st.markdown("## Current Tranches")
            df = pd.DataFrame(tranches)
            st.dataframe(df, use_container_width=True)
    
    def display_quoting_depths_table(self):
        """Display quoting depths table (legacy implementation)"""
        # This would be extracted to ui.depths_table module
        depths = self.session_manager.get_quoting_depths()
        if depths:
            st.markdown("### Current Quoting Depths")
            df = pd.DataFrame(depths)
            st.dataframe(df, use_container_width=True)
    
    def display_advanced_mm_valuation(self, advanced_valuation):
        """Display advanced MM valuation (legacy implementation)"""
        # This would be extracted to ui.results_display module
        if not advanced_valuation or not advanced_valuation['entity_valuations']:
            return
        
        st.markdown("## Advanced Market Maker Valuation")
        st.markdown("*Multi-model approach based on Almgren-Chriss, Kyle's Lambda, Bouchaud Power Law, and Amihud frameworks*")
        
        # Display summary metrics
        total_mm_value = sum(entity_data['total_mm_value'] for entity_data in advanced_valuation['entity_valuations'].values())
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total MM Value Generated", f"${total_mm_value:,.0f}")
        with col2:
            num_entities = len(advanced_valuation['entity_valuations'])
            avg_value_per_entity = total_mm_value / num_entities if num_entities > 0 else 0
            st.metric("Average Value per Entity", f"${avg_value_per_entity:,.0f}")
        with col3:
            volatility = advanced_valuation['parameters_used']['volatility']
            st.metric("Market Volatility", f"{volatility:.1%}")
    
    def display_depth_options_graph(self, ratio_data):
        """Display depth options graph (legacy implementation)"""
        # This would be extracted to ui.visualization module
        if not ratio_data:
            return
        
        st.markdown("### Depth-to-Options Value Analysis")
        
        # Simple visualization for now
        entities = list(ratio_data.keys())
        ratios = [ratio_data[entity]['effective_depth_to_option_ratio'] for entity in entities]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(entities, ratios)
        ax.set_xlabel('Entities')
        ax.set_ylabel('Effective Depth-to-Option Ratio')
        ax.set_title('Depth Coverage Ratio per Entity')
        ax.axhline(y=1.0, color='red', linestyle='--', alpha=0.7, label='1:1 Coverage Line')
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    def display_results(self, params):
        """Display calculation results (legacy implementation)"""
        # This would be extracted to ui.results_display module
        results = self.session_manager.get_calculation_results()
        if not results:
            return
        
        st.markdown("## Results")
        
        # Portfolio Summary
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Total Portfolio Value",
                f"${results['total_portfolio_value']:,.0f}"
            )
        
        with col2:
            portfolio_percentage = (results['total_portfolio_value'] / params['total_valuation']) * 100
            st.metric(
                "Portfolio as % of Total Valuation",
                f"{portfolio_percentage:.2f}%"
            )
        
        with col3:
            st.metric(
                "Number of Entities",
                len(results['entities'])
            )


def main():
    """Main application entry point"""
    try:
        app = ModularOptionsApp()
        app.run()
        
    except Exception as e:
        logger.critical(f"Critical error in main application: {e}")
        st.error("A critical error occurred. Please restart the application.")


if __name__ == "__main__":
    main()
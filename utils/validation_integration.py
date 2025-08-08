"""
Validation Integration Module

This module integrates comprehensive financial validation with the Streamlit application,
providing real-time validation feedback and preventing invalid calculations.
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
import logging

from utils.financial_validation import (
    FinancialValidator, ValidationSummary, ValidationFormatter,
    MarketType, AssetClass, validate_basic_option_inputs,
    validate_depth_inputs, validate_mm_inputs
)
from utils.error_handling import error_handler

logger = logging.getLogger(__name__)


class StreamlitValidationHandler:
    """
    Handles validation display and integration within Streamlit applications
    """
    
    def __init__(self, market_type: MarketType = MarketType.CRYPTO):
        self.validator = FinancialValidator(market_type)
        self.formatter = ValidationFormatter()
        self.market_type = market_type
    
    @error_handler("StreamlitValidationHandler.display_validation_results")
    def display_validation_results(self, summary: ValidationSummary, 
                                 title: str = "Validation Results") -> None:
        """Display validation results in Streamlit with appropriate styling"""
        
        # Status header
        status_color = "green" if summary.is_valid else "red"
        status_text = "✅ All validations passed" if summary.is_valid else "❌ Validation issues found"
        
        st.markdown(f"### {title}")
        st.markdown(f"<span style='color: {status_color}; font-weight: bold;'>{status_text}</span>", 
                   unsafe_allow_html=True)
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Checks", summary.total_checks)
        with col2:
            st.metric("Errors", len(summary.errors), 
                     delta=None if len(summary.errors) == 0 else f"-{len(summary.errors)}")
        with col3:
            st.metric("Warnings", len(summary.warnings),
                     delta=None if len(summary.warnings) == 0 else f"-{len(summary.warnings)}")
        with col4:
            st.metric("Info", len(summary.infos))
        
        # Detailed results in expanders
        if summary.errors:
            with st.expander(f"🚨 Errors ({len(summary.errors)})", expanded=True):
                for i, error in enumerate(summary.errors, 1):
                    st.error(f"**{i}.** {error.message}")
                    if error.suggested_range:
                        st.info(f"   💡 **Suggested range:** {error.suggested_range}")
        
        if summary.warnings:
            with st.expander(f"⚠️ Warnings ({len(summary.warnings)})", expanded=len(summary.errors) == 0):
                for i, warning in enumerate(summary.warnings, 1):
                    st.warning(f"**{i}.** {warning.message}")
                    if warning.suggested_range:
                        st.info(f"   💡 **Suggested range:** {warning.suggested_range}")
        
        if summary.infos and len(summary.infos) <= 8:  # Limit info display
            with st.expander(f"ℹ️ Information ({len(summary.infos)})", expanded=False):
                for i, info in enumerate(summary.infos, 1):
                    st.info(f"**{i}.** {info.message}")

    @error_handler("StreamlitValidationHandler.validate_option_parameters")
    def validate_option_parameters(self, params: Dict[str, Any], 
                                 show_results: bool = True) -> ValidationSummary:
        """
        Validate option pricing parameters and optionally display results
        
        Expected params keys:
        - spot_price, strike_price, time_to_expiration, risk_free_rate, volatility, option_type
        """
        try:
            summary = self.validator.validate_black_scholes_parameters(
                spot_price=params.get('spot_price', 0),
                strike_price=params.get('strike_price', 0),
                time_to_expiration=params.get('time_to_expiration', 0),
                risk_free_rate=params.get('risk_free_rate', 0.05),
                volatility=params.get('volatility', 0.2),
                asset_class=params.get('asset_class', AssetClass.CRYPTO_MAJOR),
                option_type=params.get('option_type', 'call')
            )
            
            if show_results:
                self.display_validation_results(summary, "Option Parameters Validation")
            
            return summary
            
        except Exception as e:
            logger.error(f"Error validating option parameters: {e}")
            if show_results:
                st.error(f"Validation error: {e}")
            return ValidationSummary(False, [], [], [], 0)

    @error_handler("StreamlitValidationHandler.validate_depth_parameters")
    def validate_depth_parameters(self, params: Dict[str, Any],
                                show_results: bool = True) -> ValidationSummary:
        """
        Validate market depth parameters and optionally display results
        
        Expected params keys:
        - bid_ask_spread, depth_50bps, depth_100bps, depth_200bps, asset_price, exchange
        """
        try:
            summary = self.validator.validate_depth_parameters(
                bid_ask_spread_bps=params.get('bid_ask_spread', 0),
                depth_50bps=params.get('depth_50bps', 0),
                depth_100bps=params.get('depth_100bps', 0),
                depth_200bps=params.get('depth_200bps', 0),
                asset_price=params.get('asset_price', 1),
                exchange_name=params.get('exchange', 'Unknown')
            )
            
            if show_results:
                self.display_validation_results(summary, "Market Depth Validation")
            
            return summary
            
        except Exception as e:
            logger.error(f"Error validating depth parameters: {e}")
            if show_results:
                st.error(f"Validation error: {e}")
            return ValidationSummary(False, [], [], [], 0)

    @error_handler("StreamlitValidationHandler.validate_mm_parameters") 
    def validate_mm_parameters(self, params: Dict[str, Any],
                             show_results: bool = True) -> ValidationSummary:
        """
        Validate market maker model parameters and optionally display results
        """
        try:
            summary = self.validator.validate_market_maker_parameters(
                daily_volume=params.get('daily_volume', 0),
                asset_price=params.get('asset_price', 1),
                volatility=params.get('volatility', 0.2),
                mm_volume_contribution=params.get('mm_volume_contribution', 0),
                model_params=params.get('model_params')
            )
            
            if show_results:
                self.display_validation_results(summary, "Market Maker Model Validation")
                
            return summary
            
        except Exception as e:
            logger.error(f"Error validating MM parameters: {e}")
            if show_results:
                st.error(f"Validation error: {e}")
            return ValidationSummary(False, [], [], [], 0)

    def create_validation_sidebar(self) -> Dict[str, Any]:
        """Create sidebar section for validation settings"""
        st.sidebar.markdown("---")
        st.sidebar.markdown("## Validation Settings")
        
        # Market type selection
        market_options = {
            "Crypto": MarketType.CRYPTO,
            "Traditional Equity": MarketType.TRADITIONAL_EQUITY,
            "Commodity": MarketType.COMMODITY,
            "FX": MarketType.FX
        }
        
        selected_market = st.sidebar.selectbox(
            "Market Type",
            options=list(market_options.keys()),
            index=0,
            help="Select market type for context-aware validation bounds"
        )
        
        # Asset class selection
        if market_options[selected_market] == MarketType.CRYPTO:
            asset_options = {
                "Major Crypto (BTC, ETH)": AssetClass.CRYPTO_MAJOR,
                "Altcoin": AssetClass.CRYPTO_ALT
            }
        else:
            asset_options = {
                "Large Cap Equity": AssetClass.LARGE_CAP_EQUITY,
                "Small Cap Equity": AssetClass.SMALL_CAP_EQUITY
            }
        
        selected_asset = st.sidebar.selectbox(
            "Asset Class",
            options=list(asset_options.keys()),
            index=0,
            help="Asset class affects volatility bounds and other validation criteria"
        )
        
        # Validation strictness
        strictness = st.sidebar.select_slider(
            "Validation Strictness",
            options=["Permissive", "Standard", "Strict"],
            value="Standard",
            help="Permissive: Warnings only, Standard: Balanced, Strict: Conservative bounds"
        )
        
        # Auto-validation toggle
        auto_validate = st.sidebar.checkbox(
            "Auto-validate inputs",
            value=True,
            help="Automatically validate inputs as they change"
        )
        
        # Update validator if market type changed
        if market_options[selected_market] != self.market_type:
            self.market_type = market_options[selected_market]
            self.validator = FinancialValidator(self.market_type)
        
        return {
            'market_type': market_options[selected_market],
            'asset_class': asset_options[selected_asset],
            'strictness': strictness,
            'auto_validate': auto_validate
        }

    def validate_tranche_data(self, tranches: List[Dict[str, Any]],
                            entities: List[Dict[str, Any]],
                            show_results: bool = True) -> ValidationSummary:
        """Validate all tranches in the portfolio"""
        all_summaries = []
        
        for i, tranche in enumerate(tranches):
            # Extract Black-Scholes parameters from tranche
            params = {
                'spot_price': 10.0,  # Default, could be extracted from entity data
                'strike_price': tranche.get('strike_price', 0),
                'time_to_expiration': tranche.get('time_to_expiration', 0),
                'risk_free_rate': 0.05,  # Could be from global settings
                'volatility': 0.3,  # Could be from global settings or tranche-specific
                'option_type': tranche.get('option_type', 'call'),
                'asset_class': AssetClass.CRYPTO_MAJOR
            }
            
            summary = self.validate_option_parameters(params, show_results=False)
            all_summaries.append(summary)
        
        # Combine all summaries
        combined = self._combine_validation_summaries(all_summaries, "Portfolio Tranches")
        
        if show_results and (combined.errors or combined.warnings):
            self.display_validation_results(combined, "Portfolio Validation")
        
        return combined

    def validate_quoting_depths(self, depths: List[Dict[str, Any]],
                              show_results: bool = True) -> ValidationSummary:
        """Validate all quoting depth entries"""
        all_summaries = []
        
        for i, depth in enumerate(depths):
            params = {
                'bid_ask_spread': depth.get('bid_ask_spread', 0),
                'depth_50bps': depth.get('depth_50bps', 0),
                'depth_100bps': depth.get('depth_100bps', 0), 
                'depth_200bps': depth.get('depth_200bps', 0),
                'asset_price': 10.0,  # Default, could be entity-specific
                'exchange': depth.get('exchange', 'Unknown')
            }
            
            summary = self.validate_depth_parameters(params, show_results=False)
            all_summaries.append(summary)
        
        # Combine all summaries
        combined = self._combine_validation_summaries(all_summaries, "Quoting Depths")
        
        if show_results and (combined.errors or combined.warnings):
            self.display_validation_results(combined, "Depth Validation")
        
        return combined

    def _combine_validation_summaries(self, summaries: List[ValidationSummary], 
                                    context: str) -> ValidationSummary:
        """Combine multiple validation summaries into one"""
        combined = ValidationSummary(True, [], [], [], 0)
        
        for i, summary in enumerate(summaries):
            # Add context to messages
            for error in summary.errors:
                error.message = f"{context} #{i+1}: {error.message}"
                combined.add_result(error)
            
            for warning in summary.warnings:
                warning.message = f"{context} #{i+1}: {warning.message}"
                combined.add_result(warning)
            
            for info in summary.infos:
                info.message = f"{context} #{i+1}: {info.message}"
                combined.add_result(info)
        
        return combined

    def create_validation_dashboard(self, params: Dict[str, Any]) -> None:
        """Create a comprehensive validation dashboard"""
        st.markdown("## 🔍 Comprehensive Validation Dashboard")
        
        # Get entities, tranches, and depths from params or session state
        entities = params.get('entities', st.session_state.get('entities', []))
        tranches = params.get('tranches', st.session_state.get('tranches', []))  
        depths = params.get('quoting_depths', st.session_state.get('quoting_depths', []))
        
        # Create tabs for different validation categories
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Portfolio Overview", 
            "⚙️ Option Parameters", 
            "💹 Market Depth", 
            "🔗 Cross-Validation"
        ])
        
        with tab1:
            self._create_portfolio_validation_tab(entities, tranches, depths)
        
        with tab2:
            self._create_option_validation_tab(tranches, params)
        
        with tab3:
            self._create_depth_validation_tab(depths)
        
        with tab4:
            self._create_cross_validation_tab(tranches, depths, params)

    def _create_portfolio_validation_tab(self, entities: List[Dict], 
                                       tranches: List[Dict], 
                                       depths: List[Dict]) -> None:
        """Create portfolio overview validation tab"""
        st.markdown("### Portfolio Health Overview")
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Entities", len(entities))
            st.metric("Tranches", len(tranches))
            
        with col2:
            if tranches:
                call_count = sum(1 for t in tranches if t.get('option_type') == 'call')
                put_count = len(tranches) - call_count
                st.metric("Calls", call_count)
                st.metric("Puts", put_count)
        
        with col3:
            unique_exchanges = len(set(d.get('exchange', 'Unknown') for d in depths))
            st.metric("Exchanges", unique_exchanges)
            st.metric("Depth Entries", len(depths))
        
        # Validation status overview
        if tranches:
            tranche_summary = self.validate_tranche_data(tranches, entities, show_results=False)
            self._display_validation_status_card("Tranche Validation", tranche_summary)
        
        if depths:
            depth_summary = self.validate_quoting_depths(depths, show_results=False)
            self._display_validation_status_card("Depth Validation", depth_summary)

    def _create_option_validation_tab(self, tranches: List[Dict], 
                                    global_params: Dict[str, Any]) -> None:
        """Create option parameters validation tab"""
        st.markdown("### Option Parameter Validation")
        
        if not tranches:
            st.warning("No tranches configured for validation")
            return
        
        # Global parameter inputs
        st.markdown("#### Global Parameters")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            spot_price = st.number_input(
                "Current Asset Price ($)",
                min_value=0.0001,
                value=global_params.get('spot_price', 10.0),
                step=0.1,
                format="%.4f"
            )
        
        with col2:
            risk_free_rate = st.number_input(
                "Risk-Free Rate (%)",
                min_value=-10.0,
                max_value=50.0,
                value=global_params.get('risk_free_rate', 5.0),
                step=0.1,
                format="%.2f"
            ) / 100
        
        with col3:
            volatility = st.number_input(
                "Volatility (%)",
                min_value=0.1,
                max_value=1000.0,
                value=global_params.get('volatility', 30.0),
                step=0.1,
                format="%.1f"
            ) / 100
        
        # Validate each tranche individually
        st.markdown("#### Individual Tranche Validation")
        
        for i, tranche in enumerate(tranches):
            with st.expander(f"Tranche {i+1}: {tranche.get('entity', 'Unknown')} {tranche.get('option_type', 'call').upper()}", expanded=False):
                params = {
                    'spot_price': spot_price,
                    'strike_price': tranche.get('strike_price', 0),
                    'time_to_expiration': tranche.get('time_to_expiration', 0),
                    'risk_free_rate': risk_free_rate,
                    'volatility': volatility,
                    'option_type': tranche.get('option_type', 'call'),
                    'asset_class': AssetClass.CRYPTO_MAJOR
                }
                
                summary = self.validate_option_parameters(params, show_results=True)

    def _create_depth_validation_tab(self, depths: List[Dict]) -> None:
        """Create market depth validation tab"""
        st.markdown("### Market Depth Validation")
        
        if not depths:
            st.warning("No quoting depths configured for validation")
            return
        
        # Validate each depth entry
        for i, depth in enumerate(depths):
            entity_name = depth.get('entity', 'Unknown')
            exchange_name = depth.get('exchange', 'Unknown')
            
            with st.expander(f"Depth {i+1}: {entity_name} @ {exchange_name}", expanded=False):
                params = {
                    'bid_ask_spread': depth.get('bid_ask_spread', 0),
                    'depth_50bps': depth.get('depth_50bps', 0),
                    'depth_100bps': depth.get('depth_100bps', 0),
                    'depth_200bps': depth.get('depth_200bps', 0),
                    'asset_price': 10.0,  # Could be entity-specific
                    'exchange': exchange_name
                }
                
                summary = self.validate_depth_parameters(params, show_results=True)

    def _create_cross_validation_tab(self, tranches: List[Dict], 
                                   depths: List[Dict],
                                   global_params: Dict[str, Any]) -> None:
        """Create cross-validation tab for portfolio-level checks"""
        st.markdown("### Cross-Validation & Portfolio Consistency")
        
        # Check entity consistency
        if tranches and depths:
            tranche_entities = set(t.get('entity', '') for t in tranches)
            depth_entities = set(d.get('entity', '') for d in depths)
            
            st.markdown("#### Entity Consistency Check")
            
            missing_depths = tranche_entities - depth_entities
            unused_depths = depth_entities - tranche_entities
            
            if missing_depths:
                st.error(f"⚠️ Entities with tranches but no depths: {', '.join(missing_depths)}")
            
            if unused_depths:
                st.warning(f"ℹ️ Entities with depths but no tranches: {', '.join(unused_depths)}")
            
            if not missing_depths and not unused_depths:
                st.success("✅ All entities have consistent tranche and depth data")
        
        # Portfolio risk analysis
        st.markdown("#### Portfolio Risk Analysis")
        
        if tranches:
            # Calculate portfolio statistics
            strikes = [t.get('strike_price', 0) for t in tranches if t.get('strike_price', 0) > 0]
            times = [t.get('time_to_expiration', 0) for t in tranches if t.get('time_to_expiration', 0) > 0]
            
            if strikes and times:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Strike Range", f"${min(strikes):.2f} - ${max(strikes):.2f}")
                    st.metric("Avg Strike", f"${sum(strikes)/len(strikes):.2f}")
                
                with col2:
                    st.metric("Time Range", f"{min(times):.2f} - {max(times):.2f} years")
                    st.metric("Avg Time", f"{sum(times)/len(times):.2f} years")

    def _display_validation_status_card(self, title: str, summary: ValidationSummary) -> None:
        """Display a compact validation status card"""
        status_color = "green" if summary.is_valid else "red"
        status_icon = "✅" if summary.is_valid else "❌"
        
        st.markdown(f"""
        <div style="border: 1px solid {status_color}; border-radius: 5px; padding: 10px; margin: 5px 0;">
            <h4>{status_icon} {title}</h4>
            <p><strong>Errors:</strong> {len(summary.errors)} | 
               <strong>Warnings:</strong> {len(summary.warnings)} | 
               <strong>Total Checks:</strong> {summary.total_checks}</p>
        </div>
        """, unsafe_allow_html=True)


# Global validation handler instance
validation_handler = StreamlitValidationHandler()


def validate_and_warn(validation_func, *args, **kwargs) -> bool:
    """
    Helper function to validate inputs and show warnings without blocking execution
    Returns True if validation passes (no errors), False if there are errors
    """
    try:
        summary = validation_func(*args, **kwargs)
        
        # Show errors as blocking messages
        if summary.errors:
            for error in summary.errors:
                st.error(f"❌ {error.message}")
        
        # Show warnings as warnings
        if summary.warnings:
            for warning in summary.warnings:
                st.warning(f"⚠️ {warning.message}")
        
        return len(summary.errors) == 0
        
    except Exception as e:
        st.error(f"Validation error: {e}")
        return False


def quick_validate_option_form(spot: float, strike: float, time_expiry: float,
                             rate: float, vol: float, option_type: str) -> bool:
    """Quick validation for option form inputs - returns True if valid"""
    params = {
        'spot_price': spot,
        'strike_price': strike, 
        'time_to_expiration': time_expiry,
        'risk_free_rate': rate,
        'volatility': vol,
        'option_type': option_type
    }
    
    return validate_and_warn(validation_handler.validate_option_parameters, params, show_results=False)


def quick_validate_depth_form(spread: float, d50: float, d100: float, 
                            d200: float, price: float, exchange: str) -> bool:
    """Quick validation for depth form inputs - returns True if valid"""
    params = {
        'bid_ask_spread': spread,
        'depth_50bps': d50,
        'depth_100bps': d100,
        'depth_200bps': d200,
        'asset_price': price,
        'exchange': exchange
    }
    
    return validate_and_warn(validation_handler.validate_depth_parameters, params, show_results=False)
"""
UI components for the Options Pricing Calculator.
Separates presentation logic from business logic.
"""

import streamlit as st
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
from datetime import datetime

from config.constants import UI, DEFAULTS, VALIDATION, SUPPORTED_EXCHANGES, OPTION_TYPES, PHASES
from utils.error_handling import (
    EntityDataValidator, OptionDataValidator, display_validation_results,
    with_error_boundary
)


class NavigationComponent:
    """Handles phase navigation and progress indication"""
    
    @staticmethod
    @with_error_boundary("Navigation")
    def render_phase_navigation(current_phase: int) -> Optional[int]:
        """
        Render phase navigation buttons and indicator
        
        Args:
            current_phase: Current phase number (1-3)
        
        Returns:
            New phase number if changed, None otherwise
        """
        col1, col2, col3 = st.columns(3)
        
        new_phase = None
        
        with col1:
            if st.button("Phase 1: Entities", use_container_width=True):
                new_phase = PHASES.ENTITY_SETUP
        
        with col2:
            if st.button("Phase 2: Options", use_container_width=True):
                new_phase = PHASES.OPTION_CONFIG
        
        with col3:
            if st.button("Phase 3: Depth Analysis", use_container_width=True):
                new_phase = PHASES.DEPTH_ANALYSIS
        
        # Phase indicator
        phase_name = PHASES.PHASE_NAMES[current_phase - 1]
        st.info(f"**Phase {current_phase}/{PHASES.TOTAL_PHASES}:** {phase_name}")
        st.markdown("---")
        
        return new_phase
    
    @staticmethod
    @with_error_boundary("Progress Indicator")
    def render_progress_indicator(current_phase: int, entities_count: int, options_count: int, depths_count: int):
        """Render progress indicator showing completion status"""
        progress_data = {
            "Phase": ["1. Entity Setup", "2. Option Config", "3. Depth Analysis"],
            "Status": [
                f"✅ Complete ({entities_count} entities)" if entities_count > 0 else "⏳ Pending",
                f"✅ Complete ({options_count} options)" if options_count > 0 else "⏳ Pending", 
                f"✅ Complete ({depths_count} depths)" if depths_count > 0 else "⏳ Pending"
            ],
            "Current": ["🔄" if current_phase == 1 else "", "🔄" if current_phase == 2 else "", "🔄" if current_phase == 3 else ""]
        }
        
        st.sidebar.markdown("### Progress")
        progress_df = pd.DataFrame(progress_data)
        st.sidebar.dataframe(progress_df, use_container_width=True, hide_index=True)


class SidebarComponent:
    """Handles sidebar with global parameters"""
    
    @staticmethod
    @with_error_boundary("Sidebar")
    def render_sidebar(current_params: Dict[str, float]) -> Dict[str, float]:
        """
        Render sidebar with global parameters
        
        Args:
            current_params: Current parameter values
        
        Returns:
            Updated parameter values
        """
        st.sidebar.markdown("## Global Parameters")
        st.sidebar.markdown("### Market Parameters")
        
        # Total FDV input
        total_valuation = st.sidebar.number_input(
            "Total FDV ($)",
            value=float(current_params.get('total_valuation', DEFAULTS.TOTAL_VALUATION)),
            min_value=VALIDATION.MIN_VALUATION,
            step=1000.0,
            key="sidebar_total_valuation",
            help="Fully Diluted Valuation of the token"
        )
        
        # Volatility input
        volatility_pct = st.sidebar.number_input(
            "Volatility (%)",
            value=float(current_params.get('volatility', DEFAULTS.VOLATILITY) * 100),
            min_value=VALIDATION.MIN_VOLATILITY,
            max_value=VALIDATION.MAX_VOLATILITY,
            step=0.1,
            key="sidebar_volatility",
            help="Expected volatility of the underlying asset"
        )
        
        # Risk-free rate input
        risk_free_rate_pct = st.sidebar.number_input(
            "Risk-free Rate (%)",
            value=float(current_params.get('risk_free_rate', DEFAULTS.RISK_FREE_RATE) * 100),
            min_value=VALIDATION.MIN_RISK_FREE_RATE,
            max_value=VALIDATION.MAX_RISK_FREE_RATE,
            step=0.1,
            key="sidebar_risk_free_rate",
            help="Risk-free interest rate (e.g., Treasury rate)"
        )
        
        return {
            'total_valuation': total_valuation,
            'total_tokens': current_params.get('total_tokens', DEFAULTS.TOTAL_TOKENS),
            'volatility': volatility_pct / 100.0,
            'risk_free_rate': risk_free_rate_pct / 100.0
        }


class EntityComponent:
    """Handles entity-related UI components"""
    
    def __init__(self):
        self.validator = EntityDataValidator()
    
    @with_error_boundary("Entity Input Form")
    def render_entity_form(self) -> Optional[Dict[str, Any]]:
        """
        Render entity input form
        
        Returns:
            Entity data if form submitted successfully, None otherwise
        """
        with st.form("entity_setup"):
            col1, col2 = st.columns(2)
            
            with col1:
                entity_name = st.text_input(
                    "Entity Name", 
                    value="Company A",
                    help="Name of the business entity"
                )
            
            with col2:
                loan_duration = st.number_input(
                    "Loan Duration (months)", 
                    min_value=VALIDATION.MIN_LOAN_DURATION,
                    max_value=VALIDATION.MAX_LOAN_DURATION,
                    value=DEFAULTS.LOAN_DURATION,
                    step=1,
                    key="entity_loan_duration",
                    help="Duration of the loan in months"
                )
            
            if st.form_submit_button("Add Entity", use_container_width=True):
                entity_data = {
                    'name': entity_name,
                    'loan_duration': loan_duration
                }
                
                # Validate data
                validation_errors = self.validator.validate_entity(entity_data)
                if display_validation_results(validation_errors):
                    return entity_data
        
        return None
    
    @with_error_boundary("Entity Table")
    def render_entity_table(self, entities_data: List[Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
        """
        Render entity table with remove functionality
        
        Args:
            entities_data: List of entity data
        
        Returns:
            Tuple of (data_changed, duplicate_name_if_any)
        """
        if not entities_data:
            return False, None
        
        st.markdown("### Current Entities")
        
        for i, entity in enumerate(entities_data):
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{entity['name']}**")
            with col2:
                st.write(f"{entity['loan_duration']} months")
            with col3:
                if st.button("❌", key=f"remove_entity_{i}", help="Remove entity"):
                    entities_data.pop(i)
                    return True, None
        
        return False, None
    
    def check_duplicate_entity(self, entities_data: List[Dict[str, Any]], entity_name: str) -> bool:
        """Check if entity name already exists"""
        return any(e['name'] == entity_name for e in entities_data)


class OptionComponent:
    """Handles option configuration UI components"""
    
    def __init__(self):
        self.validator = OptionDataValidator()
    
    @with_error_boundary("Option Configuration")
    def render_option_configuration(
        self, 
        entities_data: List[Dict[str, Any]],
        sidebar_params: Dict[str, float]
    ) -> Tuple[Optional[Dict[str, Any]], Dict[str, Any]]:
        """
        Render option configuration form
        
        Args:
            entities_data: Available entities
            sidebar_params: Current sidebar parameters
        
        Returns:
            Tuple of (option_data_if_submitted, form_state_for_preview)
        """
        if not entities_data:
            st.warning("Add entities first!")
            return None, {}
        
        # Basic entity and option setup
        col1, col2 = st.columns(2)
        
        with col1:
            entity_names = [e['name'] for e in entities_data]
            selected_entity = st.selectbox("Entity", entity_names, key="selected_entity")
            option_type = st.selectbox("Option Type", OPTION_TYPES, key="option_type")
        
        with col2:
            entity_info = next(e for e in entities_data if e['name'] == selected_entity)
            loan_duration = entity_info['loan_duration']
            
            start_month = st.number_input(
                "Start Month", 
                min_value=0, 
                max_value=loan_duration-1, 
                value=0, 
                key="start_month"
            )
        
        # Time calculation
        time_to_expiration = (loan_duration - start_month) / 12.0
        st.info(f"Time to expiration: {time_to_expiration:.2f} years ({loan_duration - start_month} months)")
        
        # Token supply share
        token_share_pct = st.number_input(
            "Token Supply Share (%)", 
            min_value=VALIDATION.MIN_TOKEN_SHARE,
            max_value=VALIDATION.MAX_TOKEN_SHARE,
            value=DEFAULTS.TOKEN_SHARE_PCT,
            step=0.01,
            key="token_share_pct"
        )
        
        # Option valuation method
        valuation_method = st.radio(
            "Option Valuation Method", 
            ["FDV Valuation", "Premium from Current FDV"], 
            horizontal=True, 
            key="valuation_method"
        )
        
        # Method-specific inputs
        if valuation_method == "FDV Valuation":
            token_valuation = st.number_input(
                "Token FDV ($)", 
                min_value=0.01, 
                value=DEFAULTS.TOKEN_VALUATION, 
                step=100.0, 
                key="token_valuation"
            )
            strike_price = token_valuation
            premium_pct = None
            current_fdv = None
        else:
            current_fdv_from_sidebar = sidebar_params['total_valuation']
            st.info(f"Using Current FDV from sidebar: ${current_fdv_from_sidebar:,.2f}")
            premium_pct = st.number_input(
                "Premium from Current FDV (%)", 
                min_value=VALIDATION.MIN_PREMIUM,
                max_value=VALIDATION.MAX_PREMIUM,
                value=DEFAULTS.PREMIUM_PCT,
                step=1.0,
                key="premium_pct"
            )
            strike_price = current_fdv_from_sidebar * (1 + premium_pct / 100.0)
            current_fdv = current_fdv_from_sidebar
            token_valuation = None
        
        # Display calculated values
        st.info(f"Calculated Strike Price: ${strike_price:,.2f}")
        
        # Option value preview
        if valuation_method == "FDV Valuation":
            option_value_preview = token_valuation * (token_share_pct / 100.0)
        else:
            option_value_preview = current_fdv_from_sidebar * (token_share_pct / 100.0)
        
        st.info(f"Option represents {token_share_pct:.2f}% of token supply (≈${option_value_preview:,.2f} value)")
        
        # Form state for return
        form_state = {
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
        }
        
        # Form submission
        with st.form("add_option_form"):
            if st.form_submit_button("Add Option", use_container_width=True):
                validation_errors = self.validator.validate_option(form_state)
                if display_validation_results(validation_errors):
                    return form_state, form_state
        
        return None, form_state
    
    @with_error_boundary("Option Table")
    def render_option_table(self, tranches_data: List[Dict[str, Any]]) -> bool:
        """
        Render option table with remove functionality
        
        Returns:
            True if data was modified
        """
        if not tranches_data:
            return False
        
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
        
        # Data rows
        for i, tranche in enumerate(tranches_data):
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
                    tranches_data.pop(i)
                    return True
        
        return False


class HeaderComponent:
    """Handles application header and styling"""
    
    @staticmethod
    @with_error_boundary("Header")
    def render_header():
        """Render application header with styling"""
        # Custom CSS
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
            
            .info-box {
                background-color: #f8f9fa;
                border-left: 4px solid #17a2b8;
                padding: 1rem;
                margin: 1rem 0;
                border-radius: 4px;
            }
            
            .success-box {
                background-color: #d4edda;
                border-left: 4px solid #28a745;
                padding: 1rem;
                margin: 1rem 0;
                border-radius: 4px;
            }
            
            .warning-box {
                background-color: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 1rem;
                margin: 1rem 0;
                border-radius: 4px;
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Main header
        st.markdown(f'<h1 class="main-header">{UI.PAGE_TITLE}</h1>', unsafe_allow_html=True)


class PhaseTransitionComponent:
    """Handles phase transition buttons and logic"""
    
    @staticmethod
    @with_error_boundary("Phase Transition")
    def render_phase_transition_button(
        phase: int, 
        target_phase: int, 
        button_text: str, 
        required_data_count: int = 0,
        data_type: str = "items"
    ) -> bool:
        """
        Render phase transition button with validation
        
        Args:
            phase: Current phase
            target_phase: Target phase to transition to
            button_text: Text for the button
            required_data_count: Minimum required data count
            data_type: Type of data (for error message)
        
        Returns:
            True if transition should occur
        """
        if phase == target_phase - 1:  # Only show if current phase
            if required_data_count > 0:
                st.markdown("---")
                if st.button(button_text, type="primary"):
                    return True
            else:
                st.warning(f"Add {data_type} first!")
        
        return False


class DataExportComponent:
    """Handles data export functionality"""
    
    @staticmethod
    @with_error_boundary("Data Export")
    def render_export_section(
        entities_data: List[Dict[str, Any]],
        tranches_data: List[Dict[str, Any]], 
        depths_data: List[Dict[str, Any]]
    ):
        """Render data export section in sidebar"""
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Data Export")
        
        if entities_data or tranches_data or depths_data:
            export_data = {
                'entities': entities_data,
                'options': tranches_data,
                'depths': depths_data,
                'exported_at': datetime.now().isoformat(),
                'version': '2.0'
            }
            
            if st.sidebar.button("📥 Export Configuration"):
                import json
                json_str = json.dumps(export_data, indent=2)
                st.sidebar.download_button(
                    label="Download JSON",
                    data=json_str,
                    file_name=f"options_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        else:
            st.sidebar.info("No data to export yet")


# Convenience function to get all UI components
def get_ui_components() -> Dict[str, Any]:
    """Get instances of all UI components"""
    return {
        'navigation': NavigationComponent(),
        'sidebar': SidebarComponent(),
        'entity': EntityComponent(),
        'option': OptionComponent(),
        'header': HeaderComponent(),
        'phase_transition': PhaseTransitionComponent(),
        'export': DataExportComponent()
    }
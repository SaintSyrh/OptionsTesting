"""
Refactored Options Pricing Calculator - Modular Architecture
This is the main application file that orchestrates all components.

The refactored architecture provides:
1. Modular function breakdown for better maintainability
2. Constants extraction into config files 
3. Separation of concerns - business logic vs UI
4. Reusable components to eliminate duplication
5. Better error handling patterns
"""

import streamlit as st
from typing import Dict, List, Any

# Import configuration and constants
from config.constants import UI, SESSIONS, DEFAULTS, PHASES

# Import services (business logic)
from services.calculation_service import CalculationOrchestrator
from services.depth_analysis_service import DepthAnalysisOrchestrator

# Import UI components
from components.ui_components import get_ui_components

# Import utilities
from utils.error_handling import error_handler_instance, with_error_boundary

# Import data models
from models.data_models import ValidationError


class SessionStateManager:
    """Manages Streamlit session state with proper initialization"""
    
    @staticmethod
    def initialize_session_state():
        """Initialize all session state variables with defaults"""
        defaults = {
            SESSIONS.CURRENT_PHASE: PHASES.ENTITY_SETUP,
            SESSIONS.ENTITIES_DATA: [],
            SESSIONS.TRANCHES_DATA: [],
            SESSIONS.DEPTHS_DATA: [],
            SESSIONS.CALCULATION_RESULTS: None,
            SESSIONS.PARAMS: {
                SESSIONS.TOTAL_VALUATION: DEFAULTS.TOTAL_VALUATION,
                SESSIONS.TOTAL_TOKENS: DEFAULTS.TOTAL_TOKENS,
                SESSIONS.VOLATILITY: DEFAULTS.VOLATILITY,
                SESSIONS.RISK_FREE_RATE: DEFAULTS.RISK_FREE_RATE
            }
        }
        
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    @staticmethod
    def get_session_data() -> Dict[str, Any]:
        """Get all relevant session data"""
        return {
            'current_phase': st.session_state.get(SESSIONS.CURRENT_PHASE, 1),
            'entities_data': st.session_state.get(SESSIONS.ENTITIES_DATA, []),
            'tranches_data': st.session_state.get(SESSIONS.TRANCHES_DATA, []),
            'depths_data': st.session_state.get(SESSIONS.DEPTHS_DATA, []),
            'params': st.session_state.get(SESSIONS.PARAMS, {})
        }
    
    @staticmethod
    def update_session_state(key: str, value: Any):
        """Update session state safely"""
        st.session_state[key] = value


class PhaseOneHandler:
    """Handles Phase 1: Entity Setup"""
    
    def __init__(self, ui_components: Dict[str, Any]):
        self.ui = ui_components
    
    @with_error_boundary("Phase 1 - Entity Setup")
    def render_phase_one(self, session_data: Dict[str, Any]) -> bool:
        """
        Render Phase 1: Entity Setup
        
        Returns:
            True if rerun is needed
        """
        st.markdown("## Phase 1: Entity Setup")
        
        # Render entity input form
        new_entity_data = self.ui['entity'].render_entity_form()
        
        if new_entity_data:
            # Check for duplicates
            if self.ui['entity'].check_duplicate_entity(
                session_data['entities_data'], 
                new_entity_data['name']
            ):
                st.warning(f"Entity '{new_entity_data['name']}' already exists!")
            else:
                session_data['entities_data'].append(new_entity_data)
                st.success(f"Added {new_entity_data['name']}")
                SessionStateManager.update_session_state(SESSIONS.ENTITIES_DATA, session_data['entities_data'])
                return True
        
        # Render entity table
        data_changed, _ = self.ui['entity'].render_entity_table(session_data['entities_data'])
        if data_changed:
            SessionStateManager.update_session_state(SESSIONS.ENTITIES_DATA, session_data['entities_data'])
            return True
        
        # Phase transition
        if self.ui['phase_transition'].render_phase_transition_button(
            phase=1, 
            target_phase=2,
            button_text="Continue to Phase 2",
            required_data_count=len(session_data['entities_data']),
            data_type="entities"
        ):
            SessionStateManager.update_session_state(SESSIONS.CURRENT_PHASE, 2)
            return True
        
        return False


class PhaseTwoHandler:
    """Handles Phase 2: Option Configuration"""
    
    def __init__(self, ui_components: Dict[str, Any]):
        self.ui = ui_components
    
    @with_error_boundary("Phase 2 - Option Configuration")
    def render_phase_two(self, session_data: Dict[str, Any]) -> bool:
        """
        Render Phase 2: Option Configuration
        
        Returns:
            True if rerun is needed
        """
        st.markdown("## Phase 2: Option Configuration")
        
        if not session_data['entities_data']:
            st.warning("Add entities first!")
            if st.button("Back to Phase 1"):
                SessionStateManager.update_session_state(SESSIONS.CURRENT_PHASE, 1)
                return True
            return False
        
        # Render option configuration
        new_option_data, _ = self.ui['option'].render_option_configuration(
            session_data['entities_data'],
            session_data['params']
        )
        
        if new_option_data:
            session_data['tranches_data'].append(new_option_data)
            st.success(f"Added {new_option_data['option_type']} option for {new_option_data['entity']}")
            SessionStateManager.update_session_state(SESSIONS.TRANCHES_DATA, session_data['tranches_data'])
            return True
        
        # Render option table
        data_changed = self.ui['option'].render_option_table(session_data['tranches_data'])
        if data_changed:
            SessionStateManager.update_session_state(SESSIONS.TRANCHES_DATA, session_data['tranches_data'])
            return True
        
        # Phase transition
        if self.ui['phase_transition'].render_phase_transition_button(
            phase=2,
            target_phase=3, 
            button_text="Continue to Phase 3",
            required_data_count=len(session_data['tranches_data']),
            data_type="options"
        ):
            SessionStateManager.update_session_state(SESSIONS.CURRENT_PHASE, 3)
            return True
        
        return False


class PhaseThreeHandler:
    """Handles Phase 3: Depth Analysis"""
    
    def __init__(self):
        self.depth_orchestrator = DepthAnalysisOrchestrator()
    
    @with_error_boundary("Phase 3 - Depth Analysis")
    def render_phase_three(self, session_data: Dict[str, Any]) -> bool:
        """
        Render Phase 3: Depth Analysis
        
        Returns:
            True if rerun is needed
        """
        # Use the depth analysis orchestrator which handles all the complex logic
        rerun_needed = self.depth_orchestrator.run_depth_analysis_phase(
            session_data['entities_data'],
            session_data['tranches_data'], 
            session_data['depths_data'],
            session_data['params']
        )
        
        if rerun_needed:
            # Update session state with modified depths data
            SessionStateManager.update_session_state(SESSIONS.DEPTHS_DATA, session_data['depths_data'])
        
        return rerun_needed


class OptionsCalculatorApp:
    """Main application class that orchestrates everything"""
    
    def __init__(self):
        self.ui_components = get_ui_components()
        self.session_manager = SessionStateManager()
        self.calculation_orchestrator = CalculationOrchestrator()
        
        # Phase handlers
        self.phase_one_handler = PhaseOneHandler(self.ui_components)
        self.phase_two_handler = PhaseTwoHandler(self.ui_components)
        self.phase_three_handler = PhaseThreeHandler()
    
    @with_error_boundary("Application Initialization")
    def initialize_app(self):
        """Initialize the application"""
        # Page configuration
        st.set_page_config(
            page_title=UI.PAGE_TITLE,
            layout=UI.LAYOUT,
            initial_sidebar_state=UI.SIDEBAR_STATE
        )
        
        # Initialize session state
        self.session_manager.initialize_session_state()
        
        # Render header
        self.ui_components['header'].render_header()
    
    @with_error_boundary("Main Application Loop")
    def run(self):
        """Main application loop"""
        # Initialize the application
        self.initialize_app()
        
        # Get current session data
        session_data = self.session_manager.get_session_data()
        
        # Render sidebar with global parameters
        updated_params = self.ui_components['sidebar'].render_sidebar(session_data['params'])
        if updated_params != session_data['params']:
            SessionStateManager.update_session_state(SESSIONS.PARAMS, updated_params)
            session_data['params'] = updated_params
        
        # Render progress indicator in sidebar
        self.ui_components['navigation'].render_progress_indicator(
            session_data['current_phase'],
            len(session_data['entities_data']),
            len(session_data['tranches_data']),
            len(session_data['depths_data'])
        )
        
        # Render data export in sidebar
        self.ui_components['export'].render_export_section(
            session_data['entities_data'],
            session_data['tranches_data'],
            session_data['depths_data']
        )
        
        # Render phase navigation
        new_phase = self.ui_components['navigation'].render_phase_navigation(
            session_data['current_phase']
        )
        if new_phase:
            SessionStateManager.update_session_state(SESSIONS.CURRENT_PHASE, new_phase)
            st.rerun()
        
        # Route to appropriate phase handler
        rerun_needed = False
        
        try:
            if session_data['current_phase'] == PHASES.ENTITY_SETUP:
                rerun_needed = self.phase_one_handler.render_phase_one(session_data)
            elif session_data['current_phase'] == PHASES.OPTION_CONFIG:
                rerun_needed = self.phase_two_handler.render_phase_two(session_data)
            elif session_data['current_phase'] == PHASES.DEPTH_ANALYSIS:
                rerun_needed = self.phase_three_handler.render_phase_three(session_data)
            
            # Rerun if needed
            if rerun_needed:
                st.rerun()
                
        except ValidationError as e:
            st.error(f"Validation Error: {str(e)}")
        except Exception as e:
            error_handler_instance.handle_error(e, context="Main Application", show_in_ui=True)
    
    @staticmethod
    @with_error_boundary("Application Health Check")
    def health_check() -> Dict[str, bool]:
        """Perform application health check"""
        checks = {
            'session_state_initialized': bool(st.session_state),
            'ui_components_available': True,  # Will be False if import fails
            'calculation_service_available': True,  # Will be False if import fails
        }
        
        try:
            # Test calculation service
            calc_service = CalculationOrchestrator()
            checks['calculation_service_functional'] = True
        except Exception:
            checks['calculation_service_functional'] = False
        
        return checks


def main():
    """Main entry point"""
    try:
        app = OptionsCalculatorApp()
        
        # Optional: Add health check in development mode
        if st.sidebar.checkbox("Show Health Check", value=False):
            health_status = app.health_check()
            st.sidebar.json(health_status)
        
        # Run the application
        app.run()
        
    except Exception as e:
        st.error("Critical application error occurred")
        st.exception(e)
        error_handler_instance.handle_error(
            e, 
            context="Application Startup",
            show_in_ui=False  # Already showing error above
        )


if __name__ == "__main__":
    main()
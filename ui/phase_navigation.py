"""
Phase navigation component
"""
import streamlit as st
from typing import Dict, Optional
import logging

from config.settings import PHASES
from app.session_state import session_manager

logger = logging.getLogger(__name__)


class PhaseNavigationManager:
    """Manages phase navigation and progression"""
    
    def __init__(self):
        self.phases = PHASES
        self.session_manager = session_manager
    
    def display_phase_navigation(self) -> None:
        """Display phase navigation with current phase indicator"""
        try:
            st.markdown("---")
            
            col1, col2, col3 = st.columns([1, 3, 1])
            
            # Previous phase button
            with col1:
                self._display_previous_button()
            
            # Phase indicator
            with col2:
                self._display_phase_indicator()
            
            # Next phase button
            with col3:
                self._display_next_button()
                
        except Exception as e:
            logger.error(f"Error displaying phase navigation: {e}")
            st.error("Error displaying navigation")
    
    def _display_previous_button(self) -> None:
        """Display previous phase button if applicable"""
        current_phase = self.session_manager.get_current_phase()
        
        if current_phase > 1:
            prev_phase = current_phase - 1
            phase_name = self.phases.get(prev_phase, f"Phase {prev_phase}")
            
            if st.button(f"← {phase_name}", use_container_width=True, key=f"prev_phase_{prev_phase}"):
                self.session_manager.set_current_phase(prev_phase)
                st.rerun()
    
    def _display_phase_indicator(self) -> None:
        """Display current phase indicator"""
        current_phase = self.session_manager.get_current_phase()
        
        # Create phase indicator with highlighting
        phase_texts = []
        for phase_num, phase_name in self.phases.items():
            if phase_num == current_phase:
                phase_texts.append(f"**{phase_name}**")
            else:
                phase_texts.append(phase_name)
        
        indicator_text = " → ".join(phase_texts)
        st.markdown(f'<div class="phase-indicator">{indicator_text}</div>', unsafe_allow_html=True)
    
    def _display_next_button(self) -> None:
        """Display next phase button if applicable and ready"""
        current_phase = self.session_manager.get_current_phase()
        
        if current_phase < 3:
            next_phase = current_phase + 1
            phase_name = self.phases.get(next_phase, f"Phase {next_phase}")
            
            # Check if ready to advance
            can_advance, message = self._can_advance_to_phase(next_phase)
            
            if can_advance:
                if st.button(f"{phase_name} →", use_container_width=True, key=f"next_phase_{next_phase}"):
                    self.session_manager.set_current_phase(next_phase)
                    st.rerun()
            else:
                st.button(
                    f"{phase_name} →", 
                    use_container_width=True, 
                    disabled=True, 
                    help=message,
                    key=f"next_phase_disabled_{next_phase}"
                )
    
    def _can_advance_to_phase(self, phase: int) -> tuple[bool, str]:
        """Check if can advance to specified phase"""
        try:
            validation = self.session_manager.validate_phase_readiness(phase)
            
            if validation['ready']:
                return True, "Ready to proceed"
            
            if validation['errors']:
                return False, f"Cannot proceed: {', '.join(validation['errors'])}"
            
            if validation['missing_requirements']:
                return False, f"Missing: {', '.join(validation['missing_requirements'])}"
            
            return False, "Requirements not met"
            
        except Exception as e:
            logger.error(f"Error checking phase advancement: {e}")
            return False, "Error checking requirements"
    
    def get_phase_completion_status(self) -> Dict[int, Dict[str, any]]:
        """Get completion status for all phases"""
        status = {}
        
        for phase_num in self.phases.keys():
            try:
                validation = self.session_manager.validate_phase_readiness(phase_num)
                
                status[phase_num] = {
                    'name': self.phases[phase_num],
                    'ready': validation['ready'],
                    'errors': validation['errors'],
                    'warnings': validation['warnings'],
                    'missing': validation['missing_requirements']
                }
                
            except Exception as e:
                logger.error(f"Error getting status for phase {phase_num}: {e}")
                status[phase_num] = {
                    'name': self.phases[phase_num],
                    'ready': False,
                    'errors': [f"Error: {e}"],
                    'warnings': [],
                    'missing': []
                }
        
        return status
    
    def display_phase_summary(self) -> None:
        """Display summary of phase completion status"""
        try:
            status = self.get_phase_completion_status()
            current_phase = self.session_manager.get_current_phase()
            
            st.markdown("### Phase Status Summary")
            
            for phase_num, phase_info in status.items():
                with st.expander(f"Phase {phase_num}: {phase_info['name']}", 
                                expanded=(phase_num == current_phase)):
                    
                    if phase_info['ready']:
                        st.success("✅ Complete and ready")
                    else:
                        st.warning("⚠️ Incomplete")
                    
                    if phase_info['errors']:
                        st.error("**Errors:**")
                        for error in phase_info['errors']:
                            st.write(f"• {error}")
                    
                    if phase_info['warnings']:
                        st.warning("**Warnings:**")
                        for warning in phase_info['warnings']:
                            st.write(f"• {warning}")
                    
                    if phase_info['missing']:
                        st.info("**Missing Requirements:**")
                        for missing in phase_info['missing']:
                            st.write(f"• {missing}")
                            
        except Exception as e:
            logger.error(f"Error displaying phase summary: {e}")
            st.error("Error displaying phase summary")
    
    def force_phase_change(self, phase: int) -> bool:
        """Force change to specific phase (for debugging/admin)"""
        try:
            if phase in self.phases:
                self.session_manager.set_current_phase(phase)
                logger.info(f"Forced phase change to {phase}")
                return True
            else:
                logger.error(f"Invalid phase for force change: {phase}")
                return False
                
        except Exception as e:
            logger.error(f"Error forcing phase change: {e}")
            return False
    
    def get_current_phase_info(self) -> Dict[str, any]:
        """Get information about current phase"""
        current_phase = self.session_manager.get_current_phase()
        
        return {
            'number': current_phase,
            'name': self.phases.get(current_phase, f"Phase {current_phase}"),
            'is_first': current_phase == 1,
            'is_last': current_phase == len(self.phases),
            'can_go_back': current_phase > 1,
            'can_go_forward': current_phase < len(self.phases),
        }


# Global instance
phase_nav_manager = PhaseNavigationManager()
"""
Entity setup UI component (Phase 1)
"""
import streamlit as st
import pandas as pd
from typing import Dict, Any, List
import logging

from config.settings import DEFAULT_ENTITY_VALUES, VALIDATION_CONSTRAINTS
from app.session_state import session_manager
from models.data_models import validate_entity_data

logger = logging.getLogger(__name__)


class EntitySetupManager:
    """Manages entity setup UI and operations"""
    
    def __init__(self):
        self.session_manager = session_manager
        self.default_values = DEFAULT_ENTITY_VALUES
        self.constraints = VALIDATION_CONSTRAINTS
    
    def display_phase_1_entity_setup(self) -> None:
        """Display Phase 1: Entity and Loan Duration Setup"""
        try:
            st.markdown("## Phase 1: Entity & Loan Setup")
            
            # Entity creation form
            self._display_entity_form()
            
            # Display existing entities
            self._display_entities_table()
            
            # Management buttons
            self._display_management_buttons()
            
        except Exception as e:
            logger.error(f"Error displaying entity setup: {e}")
            st.error("Error displaying entity setup")
    
    def _display_entity_form(self) -> None:
        """Display form for adding new entities"""
        with st.form("phase1_setup"):
            st.markdown("### Add New Entity")
            st.markdown("Set up entities and their loan durations")
            
            col1, col2 = st.columns(2)
            
            with col1:
                entity_name = st.text_input(
                    "Entity Name",
                    value=self.default_values['entity_name'],
                    help="Name of the company/entity for this loan",
                    key="entity_name_input"
                )
            
            with col2:
                loan_duration = st.number_input(
                    "Loan Duration (months)",
                    min_value=self.constraints['loan_duration']['min'],
                    max_value=self.constraints['loan_duration']['max'],
                    value=self.default_values['loan_duration'],
                    step=1,
                    help="Total duration of the loan in months",
                    key="loan_duration_input"
                )
            
            if st.form_submit_button("Add Entity", use_container_width=True):
                self._handle_add_entity(entity_name, loan_duration)
    
    def _handle_add_entity(self, entity_name: str, loan_duration: int) -> None:
        """Handle adding a new entity"""
        try:
            # Validate input
            entity_name = entity_name.strip()
            if not entity_name:
                st.error("Entity name cannot be empty")
                return
            
            # Check for duplicates
            existing_entities = self.session_manager.get_entities()
            existing_names = [e['name'] for e in existing_entities]
            
            if entity_name in existing_names:
                st.warning(f"Entity '{entity_name}' already exists!")
                return
            
            # Create entity data
            entity_data = {
                'name': entity_name,
                'loan_duration': loan_duration
            }
            
            # Validate with Pydantic model
            try:
                validate_entity_data(entity_data)
            except Exception as validation_error:
                st.error(f"Validation error: {validation_error}")
                return
            
            # Add entity
            if self.session_manager.add_entity(entity_data):
                st.success(f"Added {entity_name} with {loan_duration} month loan")
                st.rerun()
            else:
                st.error("Failed to add entity")
                
        except Exception as e:
            logger.error(f"Error adding entity: {e}")
            st.error(f"Error adding entity: {e}")
    
    def _display_entities_table(self) -> None:
        """Display table of existing entities"""
        entities = self.session_manager.get_entities()
        
        if not entities:
            st.info("No entities configured yet. Add an entity above to get started.")
            return
        
        st.markdown("### Current Entities")
        
        # Create DataFrame
        entities_df = pd.DataFrame(entities)
        
        # Display with custom column configuration
        st.dataframe(
            entities_df,
            use_container_width=True,
            column_config={
                "name": "Entity Name",
                "loan_duration": st.column_config.NumberColumn(
                    "Loan Duration (months)",
                    format="%d"
                )
            },
            hide_index=True
        )
        
        # Entity statistics
        total_entities = len(entities)
        avg_duration = sum(e['loan_duration'] for e in entities) / total_entities
        min_duration = min(e['loan_duration'] for e in entities)
        max_duration = max(e['loan_duration'] for e in entities)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Entities", total_entities)
        with col2:
            st.metric("Avg Duration", f"{avg_duration:.1f} mo")
        with col3:
            st.metric("Min Duration", f"{min_duration} mo")
        with col4:
            st.metric("Max Duration", f"{max_duration} mo")
    
    def _display_management_buttons(self) -> None:
        """Display entity management buttons"""
        entities = self.session_manager.get_entities()
        
        if not entities:
            return
        
        st.markdown("### Entity Management")
        
        col1, col2, col3 = st.columns(3)
        
        # Clear all entities
        with col1:
            if st.button("Clear All Entities", use_container_width=True, key="clear_entities"):
                self.session_manager.clear_all_entities()
                st.success("Cleared all entities and related data")
                st.rerun()
        
        # Delete specific entity
        with col2:
            self._display_delete_entity_selector()
        
        # Continue to next phase
        with col3:
            if st.button("Continue to Phase 2", type="primary", use_container_width=True, key="continue_phase_2"):
                self.session_manager.set_current_phase(2)
                st.rerun()
    
    def _display_delete_entity_selector(self) -> None:
        """Display entity deletion selector"""
        entities = self.session_manager.get_entities()
        
        if not entities:
            return
        
        with st.expander("Delete Specific Entity"):
            entity_names = [e['name'] for e in entities]
            
            selected_entity = st.selectbox(
                "Select entity to delete:",
                options=entity_names,
                key="delete_entity_selector"
            )
            
            if st.button("Delete Selected Entity", type="secondary", key="delete_entity"):
                if self.session_manager.remove_entity(selected_entity):
                    st.success(f"Deleted entity: {selected_entity}")
                    st.rerun()
                else:
                    st.error(f"Failed to delete entity: {selected_entity}")
    
    def get_entity_summary(self) -> Dict[str, Any]:
        """Get summary of current entities"""
        entities = self.session_manager.get_entities()
        
        if not entities:
            return {
                'count': 0,
                'total_duration': 0,
                'avg_duration': 0,
                'min_duration': 0,
                'max_duration': 0,
                'entities': []
            }
        
        durations = [e['loan_duration'] for e in entities]
        
        return {
            'count': len(entities),
            'total_duration': sum(durations),
            'avg_duration': sum(durations) / len(durations),
            'min_duration': min(durations),
            'max_duration': max(durations),
            'entities': [e['name'] for e in entities]
        }
    
    def validate_entity_readiness(self) -> Dict[str, Any]:
        """Validate if entities are ready for next phase"""
        entities = self.session_manager.get_entities()
        
        validation_result = {
            'ready': len(entities) > 0,
            'entity_count': len(entities),
            'errors': [],
            'warnings': []
        }
        
        if not entities:
            validation_result['errors'].append("No entities configured")
        
        # Check for duplicate names (shouldn't happen with current logic)
        names = [e['name'] for e in entities]
        if len(names) != len(set(names)):
            validation_result['errors'].append("Duplicate entity names found")
        
        # Check for reasonable loan durations
        for entity in entities:
            if entity['loan_duration'] < 3:
                validation_result['warnings'].append(f"Entity '{entity['name']}' has very short loan duration ({entity['loan_duration']} months)")
            elif entity['loan_duration'] > 60:
                validation_result['warnings'].append(f"Entity '{entity['name']}' has very long loan duration ({entity['loan_duration']} months)")
        
        return validation_result


# Global instance
entity_setup_manager = EntitySetupManager()
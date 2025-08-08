"""
Session state management for the Options Pricing Calculator
"""
import streamlit as st
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

from models.data_models import SessionState

logger = logging.getLogger(__name__)


class SessionStateManager:
    """Centralized session state management"""
    
    def __init__(self):
        self.initialize_session_state()
    
    def initialize_session_state(self) -> None:
        """Initialize all session state variables with default values"""
        try:
            # Initialize main phase tracking
            if 'current_phase' not in st.session_state:
                st.session_state.current_phase = 1
                logger.info("Initialized session state: current_phase = 1")
            
            # Initialize data containers
            if 'entities_data' not in st.session_state:
                st.session_state.entities_data = []
                logger.info("Initialized session state: entities_data = []")
            
            if 'tranches_data' not in st.session_state:
                st.session_state.tranches_data = []
                logger.info("Initialized session state: tranches_data = []")
            
            if 'quoting_depths_data' not in st.session_state:
                st.session_state.quoting_depths_data = []
                logger.info("Initialized session state: quoting_depths_data = []")
            
            if 'calculation_results' not in st.session_state:
                st.session_state.calculation_results = None
                logger.info("Initialized session state: calculation_results = None")
            
            # Initialize UI state
            if 'ui_state' not in st.session_state:
                st.session_state.ui_state = {
                    'last_calculation_time': None,
                    'show_advanced_results': False,
                    'selected_visualization_type': 'default',
                    'error_messages': [],
                    'warning_messages': [],
                }
                logger.info("Initialized session state: ui_state")
            
            # Initialize validation state
            if 'validation_state' not in st.session_state:
                st.session_state.validation_state = {
                    'last_validation_time': None,
                    'validation_errors': {},
                    'validation_warnings': {},
                }
                logger.info("Initialized session state: validation_state")
            
        except Exception as e:
            logger.error(f"Error initializing session state: {e}")
            raise
    
    def get_current_phase(self) -> int:
        """Get current application phase"""
        return st.session_state.get('current_phase', 1)
    
    def set_current_phase(self, phase: int) -> None:
        """Set current application phase with validation"""
        if phase not in [1, 2, 3]:
            raise ValueError(f"Invalid phase: {phase}. Must be 1, 2, or 3.")
        
        old_phase = st.session_state.get('current_phase', 1)
        st.session_state.current_phase = phase
        logger.info(f"Phase changed from {old_phase} to {phase}")
    
    def add_entity(self, entity_data: Dict[str, Any]) -> bool:
        """Add entity to session state with validation"""
        try:
            # Check for duplicates
            existing_names = [e['name'] for e in st.session_state.entities_data]
            if entity_data['name'] in existing_names:
                logger.warning(f"Entity '{entity_data['name']}' already exists")
                return False
            
            st.session_state.entities_data.append(entity_data.copy())
            logger.info(f"Added entity: {entity_data['name']}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding entity: {e}")
            return False
    
    def remove_entity(self, entity_name: str) -> bool:
        """Remove entity and all associated tranches and depths"""
        try:
            # Remove entity
            st.session_state.entities_data = [
                e for e in st.session_state.entities_data 
                if e['name'] != entity_name
            ]
            
            # Remove associated tranches
            st.session_state.tranches_data = [
                t for t in st.session_state.tranches_data
                if t['entity'] != entity_name
            ]
            
            # Remove associated quoting depths
            st.session_state.quoting_depths_data = [
                q for q in st.session_state.quoting_depths_data
                if q['entity'] != entity_name
            ]
            
            # Reset calculation results
            st.session_state.calculation_results = None
            
            logger.info(f"Removed entity and associated data: {entity_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing entity {entity_name}: {e}")
            return False
    
    def add_tranche(self, tranche_data: Dict[str, Any]) -> bool:
        """Add tranche to session state"""
        try:
            st.session_state.tranches_data.append(tranche_data.copy())
            # Reset calculation results when data changes
            st.session_state.calculation_results = None
            logger.info(f"Added tranche for entity: {tranche_data.get('entity', 'Unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding tranche: {e}")
            return False
    
    def remove_tranche(self, index: int) -> bool:
        """Remove tranche by index"""
        try:
            if 0 <= index < len(st.session_state.tranches_data):
                removed = st.session_state.tranches_data.pop(index)
                st.session_state.calculation_results = None
                logger.info(f"Removed tranche at index {index}")
                return True
            else:
                logger.warning(f"Invalid tranche index: {index}")
                return False
                
        except Exception as e:
            logger.error(f"Error removing tranche at index {index}: {e}")
            return False
    
    def add_quoting_depth(self, depth_data: Dict[str, Any]) -> bool:
        """Add quoting depth data to session state"""
        try:
            # Check for duplicates (entity + exchange combination)
            existing = [
                (q['entity'], q['exchange']) 
                for q in st.session_state.quoting_depths_data
            ]
            new_combo = (depth_data['entity'], depth_data['exchange'])
            
            if new_combo in existing:
                logger.warning(f"Quoting depth for {new_combo[0]} on {new_combo[1]} already exists")
                return False
            
            st.session_state.quoting_depths_data.append(depth_data.copy())
            logger.info(f"Added quoting depth for {new_combo[0]} on {new_combo[1]}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding quoting depth: {e}")
            return False
    
    def remove_quoting_depth(self, index: int) -> bool:
        """Remove quoting depth by index"""
        try:
            if 0 <= index < len(st.session_state.quoting_depths_data):
                removed = st.session_state.quoting_depths_data.pop(index)
                logger.info(f"Removed quoting depth at index {index}")
                return True
            else:
                logger.warning(f"Invalid quoting depth index: {index}")
                return False
                
        except Exception as e:
            logger.error(f"Error removing quoting depth at index {index}: {e}")
            return False
    
    def clear_all_entities(self) -> None:
        """Clear all entities and related data"""
        st.session_state.entities_data = []
        st.session_state.tranches_data = []
        st.session_state.quoting_depths_data = []
        st.session_state.calculation_results = None
        logger.info("Cleared all entities and related data")
    
    def clear_all_tranches(self) -> None:
        """Clear all tranches"""
        st.session_state.tranches_data = []
        st.session_state.calculation_results = None
        logger.info("Cleared all tranches")
    
    def clear_all_depths(self) -> None:
        """Clear all quoting depths"""
        st.session_state.quoting_depths_data = []
        logger.info("Cleared all quoting depths")
    
    def set_calculation_results(self, results: Dict[str, Any]) -> None:
        """Set calculation results"""
        try:
            st.session_state.calculation_results = results
            st.session_state.ui_state['last_calculation_time'] = datetime.now()
            logger.info("Updated calculation results")
        except Exception as e:
            logger.error(f"Error setting calculation results: {e}")
    
    def get_entities(self) -> List[Dict[str, Any]]:
        """Get all entities"""
        return st.session_state.get('entities_data', [])
    
    def get_tranches(self) -> List[Dict[str, Any]]:
        """Get all tranches"""
        return st.session_state.get('tranches_data', [])
    
    def get_quoting_depths(self) -> List[Dict[str, Any]]:
        """Get all quoting depths"""
        return st.session_state.get('quoting_depths_data', [])
    
    def get_calculation_results(self) -> Optional[Dict[str, Any]]:
        """Get calculation results"""
        return st.session_state.get('calculation_results')
    
    def get_entities_with_depths(self) -> set:
        """Get set of entities that have quoting depth data"""
        return set(entry['entity'] for entry in self.get_quoting_depths())
    
    def get_required_entities(self) -> set:
        """Get set of entities that need quoting depth data (from tranches)"""
        return set(tranche['entity'] for tranche in self.get_tranches())
    
    def validate_phase_readiness(self, phase: int) -> Dict[str, Any]:
        """Validate if ready to proceed to a specific phase"""
        validation_result = {
            'ready': False,
            'errors': [],
            'warnings': [],
            'missing_requirements': []
        }
        
        try:
            if phase == 2:
                # Phase 2 requires entities
                if not self.get_entities():
                    validation_result['errors'].append("No entities configured")
                    validation_result['missing_requirements'].append("At least one entity")
                else:
                    validation_result['ready'] = True
            
            elif phase == 3:
                # Phase 3 requires tranches
                if not self.get_tranches():
                    validation_result['errors'].append("No tranches configured")
                    validation_result['missing_requirements'].append("At least one tranche")
                else:
                    validation_result['ready'] = True
            
            # For calculations, need all entities to have depths
            entities_with_depths = self.get_entities_with_depths()
            required_entities = self.get_required_entities()
            missing_entities = required_entities - entities_with_depths
            
            if missing_entities and phase == 3:
                validation_result['warnings'].append(f"Missing depths for: {', '.join(missing_entities)}")
                
        except Exception as e:
            logger.error(f"Error validating phase readiness: {e}")
            validation_result['errors'].append(f"Validation error: {e}")
        
        return validation_result
    
    def export_data(self) -> Dict[str, Any]:
        """Export all session data for backup/restore"""
        return {
            'entities': self.get_entities(),
            'tranches': self.get_tranches(),
            'quoting_depths': self.get_quoting_depths(),
            'timestamp': datetime.now().isoformat(),
            'current_phase': self.get_current_phase(),
        }
    
    def import_data(self, data: Dict[str, Any]) -> bool:
        """Import session data from backup"""
        try:
            if 'entities' in data:
                st.session_state.entities_data = data['entities']
            if 'tranches' in data:
                st.session_state.tranches_data = data['tranches']
            if 'quoting_depths' in data:
                st.session_state.quoting_depths_data = data['quoting_depths']
            
            # Reset calculation results when importing new data
            st.session_state.calculation_results = None
            
            logger.info("Successfully imported session data")
            return True
            
        except Exception as e:
            logger.error(f"Error importing session data: {e}")
            return False
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session state"""
        entities = self.get_entities()
        tranches = self.get_tranches()
        depths = self.get_quoting_depths()
        
        return {
            'current_phase': self.get_current_phase(),
            'entities_count': len(entities),
            'tranches_count': len(tranches),
            'depths_count': len(depths),
            'unique_entities_in_tranches': len(set(t['entity'] for t in tranches)),
            'unique_entities_in_depths': len(set(d['entity'] for d in depths)),
            'has_calculations': self.get_calculation_results() is not None,
            'last_calculation': st.session_state.ui_state.get('last_calculation_time'),
        }


# Global instance
session_manager = SessionStateManager()
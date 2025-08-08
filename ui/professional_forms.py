"""
Professional Form Components with Advanced Validation
Bloomberg/TradingView-inspired form system with real-time validation feedback
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Any, Optional, Callable, Tuple, Union
from datetime import datetime, date
import re
import logging

from ui.professional_components import professional_components
from config.styles import ICONS
from config.settings import VALIDATION_CONSTRAINTS

logger = logging.getLogger(__name__)


class ProfessionalForms:
    """Professional form components with advanced validation"""
    
    def __init__(self):
        self.components = professional_components
        self.icons = ICONS
        self.constraints = VALIDATION_CONSTRAINTS
    
    def create_professional_form(
        self,
        form_id: str,
        title: str,
        icon: Optional[str] = None,
        description: Optional[str] = None,
        submit_label: str = "Submit",
        show_validation: bool = True
    ) -> Dict[str, Any]:
        """Create a professional form container with validation"""
        try:
            # Form container styling
            form_html = f"""
            <div class="professional-form slide-in-up">
                <h3 class="form-section-title">
                    {icon + ' ' if icon else ''}{title}
                </h3>
                {f'<p style="color: var(--text-secondary); margin-bottom: 1.5rem;">{description}</p>' if description else ''}
            </div>
            """
            
            st.markdown(form_html, unsafe_allow_html=True)
            
            # Create form context
            form_data = {}
            validation_results = {}
            
            with st.form(key=form_id):
                # Store form data and validation results
                form_context = {
                    'form_id': form_id,
                    'data': form_data,
                    'validation': validation_results,
                    'submit_label': submit_label,
                    'show_validation': show_validation
                }
                
                return form_context
                
        except Exception as e:
            logger.error(f"Error creating professional form: {e}")
            st.error(f"Error creating form: {title}")
            return {}
    
    def create_enhanced_number_input(
        self,
        label: str,
        key: str,
        value: Union[int, float] = 0,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        step: Union[int, float] = 1,
        format_string: str = "%.2f",
        help_text: Optional[str] = None,
        validation_rules: Optional[Dict[str, Any]] = None,
        prefix: Optional[str] = None,
        suffix: Optional[str] = None,
        show_validation: bool = True
    ) -> Tuple[Union[int, float], bool]:
        """Create enhanced number input with professional validation"""
        try:
            # Create input with styling
            input_html = f"""
            <div class="input-group">
                <label class="input-label" for="{key}">
                    {prefix + ' ' if prefix else ''}{label}{' ' + suffix if suffix else ''}
                </label>
            </div>
            """
            
            st.markdown(input_html, unsafe_allow_html=True)
            
            # Create the input
            input_value = st.number_input(
                label="",  # Empty label since we have custom styling
                min_value=min_value,
                max_value=max_value,
                value=value,
                step=step,
                format=format_string,
                help=help_text,
                key=key
            )
            
            # Validation
            is_valid = True
            validation_messages = []
            
            if validation_rules:
                # Required validation
                if validation_rules.get('required', False) and input_value is None:
                    is_valid = False
                    validation_messages.append(f"{label} is required")
                
                # Range validation
                if 'min' in validation_rules and input_value < validation_rules['min']:
                    is_valid = False
                    validation_messages.append(f"{label} must be at least {validation_rules['min']}")
                
                if 'max' in validation_rules and input_value > validation_rules['max']:
                    is_valid = False
                    validation_messages.append(f"{label} must be at most {validation_rules['max']}")
                
                # Custom validation function
                if 'validator' in validation_rules:
                    custom_result = validation_rules['validator'](input_value)
                    if not custom_result[0]:
                        is_valid = False
                        validation_messages.extend(custom_result[1])
            
            # Show validation feedback
            if show_validation and validation_messages:
                for message in validation_messages:
                    self.components.create_validation_feedback(message, "error")
            elif show_validation and is_valid and input_value is not None:
                self.components.create_validation_feedback("Valid input", "success")
            
            return input_value, is_valid
            
        except Exception as e:
            logger.error(f"Error creating enhanced number input: {e}")
            st.error(f"Error creating input for {label}")
            return value, False
    
    def create_enhanced_selectbox(
        self,
        label: str,
        key: str,
        options: List[Any],
        index: int = 0,
        help_text: Optional[str] = None,
        validation_rules: Optional[Dict[str, Any]] = None,
        show_validation: bool = True
    ) -> Tuple[Any, bool]:
        """Create enhanced selectbox with professional validation"""
        try:
            # Create input with styling
            input_html = f"""
            <div class="input-group">
                <label class="input-label" for="{key}">
                    {label}
                </label>
            </div>
            """
            
            st.markdown(input_html, unsafe_allow_html=True)
            
            # Create the selectbox
            selected_value = st.selectbox(
                label="",  # Empty label since we have custom styling
                options=options,
                index=index,
                help=help_text,
                key=key
            )
            
            # Validation
            is_valid = True
            validation_messages = []
            
            if validation_rules:
                # Required validation
                if validation_rules.get('required', False) and selected_value is None:
                    is_valid = False
                    validation_messages.append(f"{label} is required")
                
                # Options validation
                if 'allowed_values' in validation_rules:
                    if selected_value not in validation_rules['allowed_values']:
                        is_valid = False
                        validation_messages.append(f"{label} must be one of {validation_rules['allowed_values']}")
                
                # Custom validation function
                if 'validator' in validation_rules:
                    custom_result = validation_rules['validator'](selected_value)
                    if not custom_result[0]:
                        is_valid = False
                        validation_messages.extend(custom_result[1])
            
            # Show validation feedback
            if show_validation and validation_messages:
                for message in validation_messages:
                    self.components.create_validation_feedback(message, "error")
            elif show_validation and is_valid and selected_value is not None:
                self.components.create_validation_feedback("Valid selection", "success")
            
            return selected_value, is_valid
            
        except Exception as e:
            logger.error(f"Error creating enhanced selectbox: {e}")
            st.error(f"Error creating selectbox for {label}")
            return options[0] if options else None, False
    
    def create_enhanced_text_input(
        self,
        label: str,
        key: str,
        value: str = "",
        max_chars: Optional[int] = None,
        help_text: Optional[str] = None,
        validation_rules: Optional[Dict[str, Any]] = None,
        show_validation: bool = True,
        input_type: str = "default"
    ) -> Tuple[str, bool]:
        """Create enhanced text input with professional validation"""
        try:
            # Create input with styling
            input_html = f"""
            <div class="input-group">
                <label class="input-label" for="{key}">
                    {label}
                </label>
            </div>
            """
            
            st.markdown(input_html, unsafe_allow_html=True)
            
            # Create the input based on type
            if input_type == "password":
                input_value = st.text_input(
                    label="",
                    value=value,
                    max_chars=max_chars,
                    help=help_text,
                    key=key,
                    type="password"
                )
            elif input_type == "multiline":
                input_value = st.text_area(
                    label="",
                    value=value,
                    max_chars=max_chars,
                    help=help_text,
                    key=key
                )
            else:
                input_value = st.text_input(
                    label="",
                    value=value,
                    max_chars=max_chars,
                    help=help_text,
                    key=key
                )
            
            # Validation
            is_valid = True
            validation_messages = []
            
            if validation_rules:
                # Required validation
                if validation_rules.get('required', False) and not input_value.strip():
                    is_valid = False
                    validation_messages.append(f"{label} is required")
                
                # Length validation
                if 'min_length' in validation_rules and len(input_value) < validation_rules['min_length']:
                    is_valid = False
                    validation_messages.append(f"{label} must be at least {validation_rules['min_length']} characters")
                
                if 'max_length' in validation_rules and len(input_value) > validation_rules['max_length']:
                    is_valid = False
                    validation_messages.append(f"{label} must be at most {validation_rules['max_length']} characters")
                
                # Pattern validation
                if 'pattern' in validation_rules:
                    if not re.match(validation_rules['pattern'], input_value):
                        is_valid = False
                        pattern_message = validation_rules.get('pattern_message', f"{label} format is invalid")
                        validation_messages.append(pattern_message)
                
                # Email validation
                if validation_rules.get('email', False):
                    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    if input_value and not re.match(email_pattern, input_value):
                        is_valid = False
                        validation_messages.append(f"{label} must be a valid email address")
                
                # Custom validation function
                if 'validator' in validation_rules:
                    custom_result = validation_rules['validator'](input_value)
                    if not custom_result[0]:
                        is_valid = False
                        validation_messages.extend(custom_result[1])
            
            # Show validation feedback
            if show_validation and validation_messages:
                for message in validation_messages:
                    self.components.create_validation_feedback(message, "error")
            elif show_validation and is_valid and input_value.strip():
                self.components.create_validation_feedback("Valid input", "success")
            
            return input_value, is_valid
            
        except Exception as e:
            logger.error(f"Error creating enhanced text input: {e}")
            st.error(f"Error creating text input for {label}")
            return value, False
    
    def create_entity_form(self, entity_data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Create professional entity configuration form"""
        try:
            # Create form
            form_context = self.create_professional_form(
                "entity_form",
                "Entity Configuration",
                self.icons['entity'],
                "Configure loan entity parameters and settings"
            )
            
            if not form_context:
                return None
            
            # Entity name input
            entity_name, name_valid = self.create_enhanced_text_input(
                label="Entity Name",
                key="entity_name",
                value=entity_data.get('name', '') if entity_data else '',
                validation_rules={
                    'required': True,
                    'min_length': 2,
                    'max_length': 50,
                    'pattern': r'^[a-zA-Z0-9\s\-_]+$',
                    'pattern_message': 'Entity name can only contain letters, numbers, spaces, hyphens, and underscores'
                }
            )
            
            # Loan duration
            loan_duration, duration_valid = self.create_enhanced_number_input(
                label="Loan Duration",
                key="loan_duration", 
                value=entity_data.get('loan_duration', 12) if entity_data else 12,
                min_value=self.constraints['loan_duration']['min'],
                max_value=self.constraints['loan_duration']['max'],
                step=1,
                format_string="%.0f",
                suffix="months",
                help_text="Duration of the loan in months",
                validation_rules={
                    'required': True,
                    'min': self.constraints['loan_duration']['min'],
                    'max': self.constraints['loan_duration']['max']
                }
            )
            
            # Submit button
            if st.form_submit_button(form_context['submit_label'], use_container_width=True):
                if name_valid and duration_valid:
                    return {
                        'name': entity_name.strip(),
                        'loan_duration': int(loan_duration)
                    }
                else:
                    st.error("Please fix validation errors before submitting")
                    return None
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating entity form: {e}")
            st.error("Error creating entity form")
            return None
    
    def create_tranche_form(
        self,
        entities: List[Dict[str, Any]],
        tranche_data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Create professional tranche configuration form"""
        try:
            if not entities:
                st.warning("No entities available. Please create entities first.")
                return None
            
            # Create form
            form_context = self.create_professional_form(
                "tranche_form",
                "Tranche Configuration",
                self.icons['tranche'],
                "Configure option tranches for your entities"
            )
            
            if not form_context:
                return None
            
            # Entity selection
            entity_names = [entity['name'] for entity in entities]
            selected_entity, entity_valid = self.create_enhanced_selectbox(
                label="Select Entity",
                key="tranche_entity",
                options=entity_names,
                validation_rules={'required': True}
            )
            
            # Get selected entity details
            entity_info = next((e for e in entities if e['name'] == selected_entity), entities[0])
            loan_duration = entity_info.get('loan_duration', 12)
            
            # Option type
            option_type, type_valid = self.create_enhanced_selectbox(
                label="Option Type",
                key="option_type",
                options=["call", "put"],
                validation_rules={'required': True}
            )
            
            # Start month
            start_month, start_valid = self.create_enhanced_number_input(
                label="Start Month of Pricing",
                key="start_month",
                value=tranche_data.get('start_month', 0) if tranche_data else 0,
                min_value=0,
                max_value=loan_duration-1,
                step=1,
                format_string="%.0f",
                help_text=f"Month when pricing starts (0 = immediately, max: {loan_duration-1})",
                validation_rules={
                    'required': True,
                    'min': 0,
                    'max': loan_duration-1
                }
            )
            
            # Strike price
            strike_price, strike_valid = self.create_enhanced_number_input(
                label="Strike Price",
                key="strike_price",
                value=tranche_data.get('strike_price', 12.0) if tranche_data else 12.0,
                min_value=self.constraints['strike_price']['min'],
                max_value=self.constraints['strike_price']['max'],
                step=0.0001,
                format_string="%.4f",
                prefix="$",
                validation_rules={
                    'required': True,
                    'min': self.constraints['strike_price']['min'],
                    'max': self.constraints['strike_price']['max']
                }
            )
            
            # Token allocation method
            st.markdown("#### Token Allocation Method")
            allocation_method = st.radio(
                "Choose allocation method:",
                ["Percentage of Total Tokens", "Absolute Token Count"],
                horizontal=True,
                key="allocation_method"
            )
            
            # Token allocation inputs
            if allocation_method == "Percentage of Total Tokens":
                token_percentage, percentage_valid = self.create_enhanced_number_input(
                    label="Percentage of Tokens",
                    key="token_percentage",
                    value=tranche_data.get('token_percentage', 1.0) if tranche_data else 1.0,
                    min_value=self.constraints['token_percentage']['min'],
                    max_value=self.constraints['token_percentage']['max'],
                    step=0.1,
                    format_string="%.3f",
                    suffix="%",
                    validation_rules={
                        'required': True,
                        'min': self.constraints['token_percentage']['min'],
                        'max': self.constraints['token_percentage']['max']
                    }
                )
                token_count = None
                count_valid = True
            else:
                token_count, count_valid = self.create_enhanced_number_input(
                    label="Number of Tokens",
                    key="token_count",
                    value=tranche_data.get('token_count', 1000) if tranche_data else 1000,
                    min_value=self.constraints['token_count']['min'],
                    max_value=self.constraints['token_count']['max'],
                    step=100,
                    format_string="%.0f",
                    validation_rules={
                        'required': True,
                        'min': self.constraints['token_count']['min'],
                        'max': self.constraints['token_count']['max']
                    }
                )
                token_percentage = None
                percentage_valid = True
            
            # Time to expiration calculation
            time_to_expiration = (loan_duration - start_month) / 12.0
            st.info(f"**Time to Expiration:** {time_to_expiration:.2f} years (from month {start_month} to {loan_duration})")
            
            # Submit button
            if st.form_submit_button("Add Tranche", use_container_width=True):
                all_valid = all([entity_valid, type_valid, start_valid, strike_valid, 
                               percentage_valid, count_valid])
                
                if all_valid:
                    return {
                        'entity': selected_entity,
                        'option_type': option_type,
                        'loan_duration': loan_duration,
                        'start_month': int(start_month),
                        'time_to_expiration': time_to_expiration,
                        'strike_price': strike_price,
                        'allocation_method': allocation_method,
                        'token_percentage': token_percentage,
                        'token_count': int(token_count) if token_count else None
                    }
                else:
                    st.error("Please fix validation errors before submitting")
                    return None
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating tranche form: {e}")
            st.error("Error creating tranche form")
            return None
    
    def create_depth_form(
        self,
        entities: List[str],
        exchanges: List[str],
        depth_data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Create professional quoting depths form"""
        try:
            if not entities:
                st.warning("No entities available. Please configure tranches first.")
                return None
            
            # Create form
            form_context = self.create_professional_form(
                "depth_form",
                "Quoting Depths Configuration",
                self.icons['depth'],
                "Configure exchange quoting depths for each entity"
            )
            
            if not form_context:
                return None
            
            # Entity selection
            selected_entity, entity_valid = self.create_enhanced_selectbox(
                label="Select Entity",
                key="depth_entity",
                options=entities,
                validation_rules={'required': True}
            )
            
            # Exchange selection
            selected_exchange, exchange_valid = self.create_enhanced_selectbox(
                label="Exchange",
                key="depth_exchange",
                options=exchanges,
                validation_rules={'required': True}
            )
            
            # Bid/Ask spread
            bid_ask_spread, spread_valid = self.create_enhanced_number_input(
                label="Bid/Ask Spread",
                key="bid_ask_spread",
                value=depth_data.get('bid_ask_spread', 10.0) if depth_data else 10.0,
                min_value=self.constraints['bid_ask_spread']['min'],
                max_value=self.constraints['bid_ask_spread']['max'],
                step=0.1,
                format_string="%.1f",
                suffix="bps",
                help_text="Bid-ask spread in basis points",
                validation_rules={
                    'required': True,
                    'min': self.constraints['bid_ask_spread']['min'],
                    'max': self.constraints['bid_ask_spread']['max']
                }
            )
            
            # Depth input method
            st.markdown("#### Depth Input Method")
            depth_method = st.radio(
                "Choose depth input method:",
                ["Absolute Values ($)", "Percentage of Loan Value (%)"],
                horizontal=True,
                key="depth_method"
            )
            
            # Depth inputs
            st.markdown("#### Liquidity Depths")
            
            if depth_method == "Absolute Values ($)":
                depth_50bps, d50_valid = self.create_enhanced_number_input(
                    label="Depth @ 50bps",
                    key="depth_50bps",
                    value=depth_data.get('depth_50bps', 50000.0) if depth_data else 50000.0,
                    min_value=self.constraints['depth_values']['min'],
                    max_value=self.constraints['depth_values']['max'],
                    step=1000.0,
                    format_string="%.0f",
                    prefix="$",
                    validation_rules={
                        'required': True,
                        'min': self.constraints['depth_values']['min']
                    }
                )
                
                depth_100bps, d100_valid = self.create_enhanced_number_input(
                    label="Depth @ 100bps",
                    key="depth_100bps",
                    value=depth_data.get('depth_100bps', 100000.0) if depth_data else 100000.0,
                    min_value=self.constraints['depth_values']['min'],
                    max_value=self.constraints['depth_values']['max'],
                    step=1000.0,
                    format_string="%.0f",
                    prefix="$",
                    validation_rules={
                        'required': True,
                        'min': self.constraints['depth_values']['min']
                    }
                )
                
                depth_200bps, d200_valid = self.create_enhanced_number_input(
                    label="Depth @ 200bps",
                    key="depth_200bps",
                    value=depth_data.get('depth_200bps', 200000.0) if depth_data else 200000.0,
                    min_value=self.constraints['depth_values']['min'],
                    max_value=self.constraints['depth_values']['max'],
                    step=1000.0,
                    format_string="%.0f",
                    prefix="$",
                    validation_rules={
                        'required': True,
                        'min': self.constraints['depth_values']['min']
                    }
                )
                
                depth_50bps_pct = depth_100bps_pct = depth_200bps_pct = None
                
            else:  # Percentage method
                depth_50bps_pct, d50_valid = self.create_enhanced_number_input(
                    label="Depth @ 50bps",
                    key="depth_50bps_pct",
                    value=depth_data.get('depth_50bps_pct', 5.0) if depth_data else 5.0,
                    min_value=self.constraints['depth_percentages']['min'],
                    max_value=self.constraints['depth_percentages']['max'],
                    step=0.1,
                    format_string="%.1f",
                    suffix="%",
                    validation_rules={
                        'required': True,
                        'min': self.constraints['depth_percentages']['min'],
                        'max': self.constraints['depth_percentages']['max']
                    }
                )
                
                depth_100bps_pct, d100_valid = self.create_enhanced_number_input(
                    label="Depth @ 100bps",
                    key="depth_100bps_pct",
                    value=depth_data.get('depth_100bps_pct', 10.0) if depth_data else 10.0,
                    min_value=self.constraints['depth_percentages']['min'],
                    max_value=self.constraints['depth_percentages']['max'],
                    step=0.1,
                    format_string="%.1f",
                    suffix="%",
                    validation_rules={
                        'required': True,
                        'min': self.constraints['depth_percentages']['min'],
                        'max': self.constraints['depth_percentages']['max']
                    }
                )
                
                depth_200bps_pct, d200_valid = self.create_enhanced_number_input(
                    label="Depth @ 200bps",
                    key="depth_200bps_pct",
                    value=depth_data.get('depth_200bps_pct', 20.0) if depth_data else 20.0,
                    min_value=self.constraints['depth_percentages']['min'],
                    max_value=self.constraints['depth_percentages']['max'],
                    step=0.1,
                    format_string="%.1f",
                    suffix="%",
                    validation_rules={
                        'required': True,
                        'min': self.constraints['depth_percentages']['min'],
                        'max': self.constraints['depth_percentages']['max']
                    }
                )
                
                # Calculate absolute values (would need entity loan value)
                entity_loan_value = 1000000  # Placeholder
                depth_50bps = (depth_50bps_pct / 100.0) * entity_loan_value
                depth_100bps = (depth_100bps_pct / 100.0) * entity_loan_value
                depth_200bps = (depth_200bps_pct / 100.0) * entity_loan_value
            
            # Submit button
            if st.form_submit_button("Add Quoting Depth", use_container_width=True):
                all_valid = all([entity_valid, exchange_valid, spread_valid, 
                               d50_valid, d100_valid, d200_valid])
                
                if all_valid:
                    return {
                        'entity': selected_entity,
                        'exchange': selected_exchange,
                        'bid_ask_spread': bid_ask_spread,
                        'depth_method': depth_method,
                        'depth_50bps': depth_50bps,
                        'depth_100bps': depth_100bps,
                        'depth_200bps': depth_200bps,
                        'depth_50bps_pct': depth_50bps_pct,
                        'depth_100bps_pct': depth_100bps_pct,
                        'depth_200bps_pct': depth_200bps_pct
                    }
                else:
                    st.error("Please fix validation errors before submitting")
                    return None
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating depth form: {e}")
            st.error("Error creating depth form")
            return None


# Global instance
professional_forms = ProfessionalForms()
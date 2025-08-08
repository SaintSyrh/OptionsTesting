"""
Sidebar component for base parameters
"""
import streamlit as st
from typing import Dict
import logging

from config.settings import DEFAULT_PARAMETERS, VALIDATION_CONSTRAINTS

logger = logging.getLogger(__name__)


class SidebarManager:
    """Manages the sidebar with base parameters"""
    
    def __init__(self):
        self.default_params = DEFAULT_PARAMETERS
        self.constraints = VALIDATION_CONSTRAINTS
    
    def create_sidebar(self) -> Dict[str, float]:
        """Create sidebar with base parameters and return parameter dictionary"""
        try:
            st.sidebar.markdown("## Base Parameters")
            
            # Core Token Parameters
            params = self._create_token_parameters()
            
            # Market Parameters
            market_params = self._create_market_parameters()
            params.update(market_params)
            
            # Display calculated token price
            self._display_token_price(params['total_valuation'], params['total_tokens'])
            
            logger.debug("Sidebar parameters created successfully")
            return params
            
        except Exception as e:
            logger.error(f"Error creating sidebar: {e}")
            # Return default parameters if there's an error
            return self._get_default_parameters()
    
    def _create_token_parameters(self) -> Dict[str, float]:
        """Create token information parameters"""
        st.sidebar.markdown("### Token Information")
        
        total_valuation = st.sidebar.number_input(
            "Total Token Valuation ($)",
            min_value=self.constraints['total_valuation']['min'],
            max_value=self.constraints['total_valuation']['max'],
            value=self.default_params['total_valuation'],
            step=10000.0,
            format="%.2f",
            help="Total market valuation of all tokens",
            key="sidebar_total_valuation"
        )
        
        total_tokens = st.sidebar.number_input(
            "Total Tokens",
            min_value=self.constraints['total_tokens']['min'],
            max_value=self.constraints['total_tokens']['max'],
            value=self.default_params['total_tokens'],
            step=1000.0,
            format="%.0f",
            help="Total number of tokens in circulation",
            key="sidebar_total_tokens"
        )
        
        return {
            'total_valuation': total_valuation,
            'total_tokens': total_tokens,
        }
    
    def _create_market_parameters(self) -> Dict[str, float]:
        """Create market parameters"""
        st.sidebar.markdown("### Market Parameters")
        
        volatility = st.sidebar.slider(
            "Volatility (%)",
            min_value=self.constraints['volatility']['min'],
            max_value=self.constraints['volatility']['max'],
            value=self.default_params['volatility'],
            step=1.0,
            format="%.1f",
            help="Annual volatility percentage",
            key="sidebar_volatility"
        ) / 100.0  # Convert to decimal
        
        risk_free_rate = st.sidebar.slider(
            "Risk-free Rate (%)",
            min_value=self.constraints['risk_free_rate']['min'],
            max_value=self.constraints['risk_free_rate']['max'],
            value=self.default_params['risk_free_rate'],
            step=0.1,
            format="%.1f",
            help="Annual risk-free rate percentage",
            key="sidebar_risk_free_rate"
        ) / 100.0  # Convert to decimal
        
        return {
            'volatility': volatility,
            'risk_free_rate': risk_free_rate,
        }
    
    def _display_token_price(self, total_valuation: float, total_tokens: float) -> None:
        """Display calculated token price"""
        try:
            token_price = total_valuation / total_tokens if total_tokens > 0 else 0
            st.sidebar.info(f"**Current Token Price:** ${token_price:.4f}")
        except Exception as e:
            logger.error(f"Error calculating token price: {e}")
            st.sidebar.error("Error calculating token price")
    
    def _get_default_parameters(self) -> Dict[str, float]:
        """Get default parameters with calculated token price"""
        params = self.default_params.copy()
        params['token_price'] = params['total_valuation'] / params['total_tokens']
        # Convert percentage values to decimals
        params['volatility'] = params['volatility'] / 100.0
        params['risk_free_rate'] = params['risk_free_rate'] / 100.0
        return params
    
    def validate_parameters(self, params: Dict[str, float]) -> Dict[str, str]:
        """Validate parameters and return any validation errors"""
        errors = {}
        
        try:
            # Check total valuation
            if not (self.constraints['total_valuation']['min'] <= params['total_valuation'] <= self.constraints['total_valuation']['max']):
                errors['total_valuation'] = f"Must be between ${self.constraints['total_valuation']['min']:,.0f} and ${self.constraints['total_valuation']['max']:,.0f}"
            
            # Check total tokens
            if not (self.constraints['total_tokens']['min'] <= params['total_tokens'] <= self.constraints['total_tokens']['max']):
                errors['total_tokens'] = f"Must be between {self.constraints['total_tokens']['min']:,.0f} and {self.constraints['total_tokens']['max']:,.0f}"
            
            # Check volatility (already in decimal)
            vol_pct = params['volatility'] * 100
            if not (self.constraints['volatility']['min'] <= vol_pct <= self.constraints['volatility']['max']):
                errors['volatility'] = f"Must be between {self.constraints['volatility']['min']:.0f}% and {self.constraints['volatility']['max']:.0f}%"
            
            # Check risk-free rate (already in decimal)
            rf_pct = params['risk_free_rate'] * 100
            if not (self.constraints['risk_free_rate']['min'] <= rf_pct <= self.constraints['risk_free_rate']['max']):
                errors['risk_free_rate'] = f"Must be between {self.constraints['risk_free_rate']['min']:.0f}% and {self.constraints['risk_free_rate']['max']:.0f}%"
            
        except Exception as e:
            logger.error(f"Error validating parameters: {e}")
            errors['general'] = "Error validating parameters"
        
        return errors
    
    def get_parameter_summary(self, params: Dict[str, float]) -> str:
        """Get formatted parameter summary"""
        try:
            token_price = params['total_valuation'] / params['total_tokens']
            return f"""
            **Parameter Summary:**
            - Total Valuation: ${params['total_valuation']:,.2f}
            - Total Tokens: {params['total_tokens']:,.0f}
            - Token Price: ${token_price:.4f}
            - Volatility: {params['volatility']*100:.1f}%
            - Risk-free Rate: {params['risk_free_rate']*100:.1f}%
            """
        except Exception as e:
            logger.error(f"Error creating parameter summary: {e}")
            return "Error creating parameter summary"


# Global instance
sidebar_manager = SidebarManager()
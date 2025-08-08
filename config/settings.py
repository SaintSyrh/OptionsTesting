"""
Configuration settings for the Options Pricing Calculator
"""

# Professional application settings
APP_TITLE = "🚀 Professional Options Pricing Suite"
APP_SUBTITLE = "Institutional-Grade Derivatives Analytics & Portfolio Management"
PAGE_LAYOUT = "wide"
INITIAL_SIDEBAR_STATE = "expanded"
THEME = "dark"  # Default theme: 'dark' or 'light'

# Default parameter values
DEFAULT_PARAMETERS = {
    'total_valuation': 1000000.0,
    'total_tokens': 100000.0,
    'volatility': 30.0,  # Percentage
    'risk_free_rate': 5.0,  # Percentage
}

# Entity setup defaults
DEFAULT_ENTITY_VALUES = {
    'entity_name': "Company A",
    'loan_duration': 12,
}

# Tranche setup defaults
DEFAULT_TRANCHE_VALUES = {
    'start_month': 0,
    'strike_price': 12.0000,
    'token_percentage': 1.0,
    'token_count': 1000,
}

# Quoting depths defaults
DEFAULT_DEPTH_VALUES = {
    'bid_ask_spread': 10.0,
    'depth_50bps': 50000.0,
    'depth_100bps': 100000.0,
    'depth_200bps': 200000.0,
    'depth_50bps_pct': 5.0,
    'depth_100bps_pct': 10.0,
    'depth_200bps_pct': 20.0,
}

# Exchange definitions
EXCHANGES = [
    "Binance", "OKX", "Coinbase", "Bybit", "KuCoin", 
    "MEXC", "Gate", "Bitvavo", "Bitget", "Other"
]

# Option types
OPTION_TYPES = ["call", "put"]

# Allocation methods
ALLOCATION_METHODS = ["Percentage of Total Tokens", "Absolute Token Count"]

# Depth methods
DEPTH_METHODS = ["Absolute Values ($)", "Percentage of Loan Value (%)"]

# Validation constraints
VALIDATION_CONSTRAINTS = {
    'total_valuation': {'min': 0.0, 'max': 1e12},
    'total_tokens': {'min': 1.0, 'max': 1e12},
    'volatility': {'min': 1.0, 'max': 200.0},
    'risk_free_rate': {'min': 0.0, 'max': 20.0},
    'loan_duration': {'min': 1, 'max': 120},
    'strike_price': {'min': 0.0001, 'max': 1e6},
    'token_percentage': {'min': 0.001, 'max': 100.0},
    'token_count': {'min': 1, 'max': 1e9},
    'bid_ask_spread': {'min': 0.0, 'max': 1000.0},
    'depth_values': {'min': 0.0, 'max': 1e9},
    'depth_percentages': {'min': 0.0, 'max': 100.0},
}

# Phase navigation
PHASES = {
    1: "Entity Setup",
    2: "Tranche Setup", 
    3: "Quoting Depths"
}

# Professional financial color scheme
COLORS = {
    'primary': '#1E3A8A',
    'primary_light': '#3B82F6',
    'secondary': '#0F172A',
    'accent': '#3B82F6',
    'success': '#10B981',
    'success_light': '#34D399',
    'danger': '#EF4444',
    'danger_light': '#F87171',
    'warning': '#F59E0B',
    'warning_light': '#FBBF24',
    'info': '#3B82F6',
    'info_light': '#60A5FA',
    'neutral_50': '#F8FAFC',
    'neutral_100': '#F1F5F9',
    'neutral_200': '#E2E8F0',
    'neutral_300': '#CBD5E1',
    'neutral_400': '#94A3B8',
    'neutral_500': '#64748B',
    'neutral_600': '#475569',
    'neutral_700': '#334155',
    'neutral_800': '#1E293B',
    'neutral_900': '#0F172A',
    'background_dark': '#0D1421',
    'surface_dark': '#1E293B',
    'text_primary_dark': '#F8FAFC',
    'text_secondary_dark': '#CBD5E1',
    'border_dark': '#334155',
    'background_light': '#F8FAFC',
    'surface_light': '#FFFFFF',
    'text_primary_light': '#0F172A',
    'text_secondary_light': '#475569',
    'border_light': '#E2E8F0'
}

# Professional financial chart colors
CHART_COLORS = [
    '#3B82F6',  # Primary blue
    '#10B981',  # Success green
    '#F59E0B',  # Warning yellow
    '#EF4444',  # Danger red
    '#8B5CF6',  # Purple
    '#06B6D4',  # Cyan
    '#F97316',  # Orange
    '#84CC16',  # Lime
    '#EC4899',  # Pink
    '#6366F1'   # Indigo
]

# Financial data visualization colors
FINANCIAL_COLORS = {
    'bullish': '#10B981',     # Green for positive/up movements
    'bearish': '#EF4444',     # Red for negative/down movements
    'neutral': '#64748B',     # Gray for neutral/unchanged
    'volume': '#3B82F6',      # Blue for volume indicators
    'volatility': '#F59E0B',  # Yellow for volatility
    'risk': '#EF4444',        # Red for risk metrics
    'profit': '#10B981',      # Green for profit
    'loss': '#EF4444',        # Red for loss
    'portfolio': '#8B5CF6',   # Purple for portfolio
    'benchmark': '#64748B'    # Gray for benchmark
}

# Enhanced logging configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S',
    'log_file': 'logs/options_calculator.log',
    'max_file_size': '10MB',
    'backup_count': 5,
    'enable_console': True,
    'enable_file': True
}

# File export settings
EXPORT_SETTINGS = {
    'json_indent': 2,
    'timestamp_format': '%Y%m%d_%H%M%S',
    'file_prefix': 'option_config_'
}

# Professional CSS class names
CSS_CLASSES = {
    'main_header': 'main-header',
    'subtitle_header': 'subtitle-header',
    'financial_card': 'financial-card',
    'metric_container': 'metric-container',
    'entity_section': 'entity-section',
    'success_box': 'success-box',
    'error_section': 'error-section',
    'warning_section': 'warning-section',
    'info_section': 'info-section',
    'phase_indicator': 'phase-indicator',
    'calculation_section': 'calculation-section',
    'professional_table': 'professional-table',
    'progress_container': 'progress-container',
    'loading_spinner': 'professional-spinner',
    'tooltip': 'custom-tooltip'
}

# Professional branding
BRANDING = {
    'company_name': 'Architech Analytics',
    'product_name': 'Options Pricing Suite',
    'version': '2.0.0',
    'tagline': 'Institutional-Grade Financial Analytics',
    'logo_emoji': '🚀',
    'primary_color': '#3B82F6',
    'brand_gradient': 'linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%)'
}

# Dashboard layout configuration
DASHBOARD_CONFIG = {
    'sidebar_width': 320,
    'content_padding': '2rem',
    'card_spacing': '1.5rem',
    'animation_duration': '0.3s',
    'border_radius': '12px',
    'shadow_level': 'lg',
    'show_progress_indicators': True,
    'enable_animations': True,
    'show_tooltips': True,
    'enable_dark_mode': True
}

# Professional navigation
NAVIGATION = {
    'phases': {
        1: {
            'name': 'Entity Setup',
            'icon': '🏢',
            'color': '#10B981',
            'description': 'Configure loan entities and parameters'
        },
        2: {
            'name': 'Tranche Configuration',
            'icon': '📊',
            'color': '#3B82F6',
            'description': 'Set up option tranches and pricing'
        },
        3: {
            'name': 'Depth Analysis',
            'icon': '💰',
            'color': '#F59E0B',
            'description': 'Market depth and liquidity analysis'
        }
    },
    'show_progress_bar': True,
    'enable_phase_validation': True
}
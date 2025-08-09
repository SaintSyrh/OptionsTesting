"""
Configuration module containing all constants and magic numbers used throughout the application.
This centralizes all configuration values for easy maintenance and modification.
"""

from typing import Dict, List
from dataclasses import dataclass, field

# Market Maker Constants
@dataclass
class MarketMakerConfig:
    """Market maker related constants"""
    DAILY_VOLUME: float = 1000000.0  # Default assumed daily volume in USD
    ADVERSE_SELECTION_RATE: float = 0.3  # 30% of trades are informed/toxic
    SPREAD_REDUCTION_FACTOR: float = 0.5  # MM reduces spread by 50%
    DEPTH_INCREASE_FACTOR: float = 0.5  # MM adds 50% more depth
    MM_VOLUME: float = 500000.0  # MM contribution to daily volume
    DEFAULT_VOLATILITY: float = 0.25  # Default volatility for depth calculations

# Default Values
@dataclass
class DefaultValues:
    """Default values for various inputs"""
    TOTAL_VALUATION: float = 1000000.0
    TOTAL_TOKENS: float = 100000.0
    VOLATILITY: float = 0.30
    RISK_FREE_RATE: float = 0.05
    LOAN_DURATION: int = 12  # months
    TOKEN_SHARE_PCT: float = 1.0
    TOKEN_VALUATION: float = 10000.0
    PREMIUM_PCT: float = 20.0
    BID_ASK_SPREAD: float = 10.0  # basis points
    DEPTH_50BPS: float = 100000.0
    DEPTH_100BPS: float = 200000.0
    DEPTH_200BPS: float = 300000.0

# UI Configuration
@dataclass
class UIConfig:
    """UI related constants"""
    PAGE_TITLE: str = "Options Pricing Calculator"
    LAYOUT: str = "wide"
    SIDEBAR_STATE: str = "expanded"
    
    # Chart dimensions
    CHART_WIDTH: int = 12
    CHART_HEIGHT: int = 6
    
    # Colors for charts
    CHART_COLORS: List[str] = field(default_factory=lambda: ['#2ca02c', '#ff7f0e', '#1f77b4', '#d62728', '#9467bd'])
    MODEL_VALUE_COLOR: str = '#2ca02c'
    SPREAD_COST_COLOR: str = '#d62728'

# Validation Limits
@dataclass
class ValidationLimits:
    """Validation limits for various inputs"""
    MIN_VALUATION: float = 1.0
    MAX_VALUATION: float = 1e12  # 1 trillion
    MIN_VOLATILITY: float = 0.1
    MAX_VOLATILITY: float = 500.0
    MIN_RISK_FREE_RATE: float = 0.0
    MAX_RISK_FREE_RATE: float = 20.0
    MIN_LOAN_DURATION: int = 1
    MAX_LOAN_DURATION: int = 120
    MIN_TOKEN_SHARE: float = 0.01
    MAX_TOKEN_SHARE: float = 100.0
    MIN_PREMIUM: float = -50.0
    MAX_PREMIUM: float = 200.0

# Exchange Configuration - Using tuples instead of lists for immutability
SUPPORTED_EXCHANGES = ("Binance", "OKX", "Coinbase", "Other")
OPTION_TYPES = ("call", "put")

# Risk Scoring Configuration
@dataclass
class RiskScoring:
    """Risk scoring thresholds"""
    LOW_RISK_THRESHOLD: float = 10.0  # Depth coverage >= 10x
    MEDIUM_RISK_THRESHOLD: float = 5.0  # Depth coverage 5-10x
    HIGH_RISK_THRESHOLD: float = 2.0  # Depth coverage 2-5x
    # Below 2x is very high risk (score 4)

# Calculation Parameters
@dataclass
class CalculationParams:
    """Parameters for various calculations"""
    BASIS_POINTS_DIVISOR: int = 10000  # Convert basis points to decimal
    TRADE_SIZE_SAMPLE_SIZE: int = 10  # Number of trade sizes to sample
    MONTHS_TO_YEARS: float = 12.0  # Convert months to years
    PERCENTAGE_DIVISOR: float = 100.0  # Convert percentage to decimal

# File Paths and Naming
@dataclass
class FileConfig:
    """File and path configuration"""
    CONFIG_DIR: str = "config"
    SERVICES_DIR: str = "services"
    COMPONENTS_DIR: str = "components"
    UTILS_DIR: str = "utils"
    MODELS_DIR: str = "models"

# Session State Keys
@dataclass
class SessionKeys:
    """Session state keys to avoid magic strings"""
    CURRENT_PHASE: str = "current_phase"
    ENTITIES_DATA: str = "entities_data"
    TRANCHES_DATA: str = "tranches_data"
    DEPTHS_DATA: str = "depths_data"
    CALCULATION_RESULTS: str = "calculation_results"
    PARAMS: str = "params"
    
    # Parameter keys
    TOTAL_VALUATION: str = "total_valuation"
    TOTAL_TOKENS: str = "total_tokens"
    VOLATILITY: str = "volatility"
    RISK_FREE_RATE: str = "risk_free_rate"

# Error Messages
@dataclass
class ErrorMessages:
    """Centralized error messages"""
    INVALID_PARAMETERS: str = "Invalid parameters for option calculation"
    MISSING_ENTITIES: str = "Add entities first!"
    MISSING_OPTIONS: str = "Configure options first!"
    CALCULATION_ERROR: str = "Error during calculation"
    DIVISION_BY_ZERO: str = "Division by zero encountered"
    NEGATIVE_VALUE: str = "Negative values not allowed"

# Success Messages
@dataclass
class SuccessMessages:
    """Centralized success messages"""
    ENTITY_ADDED: str = "Entity added successfully"
    OPTION_ADDED: str = "Option added successfully"
    DEPTH_ADDED: str = "Depth data added successfully"
    CALCULATION_COMPLETE: str = "Calculation completed successfully"

# Phase Configuration
@dataclass
class PhaseConfig:
    """Phase navigation configuration"""
    TOTAL_PHASES: int = 3
    PHASE_NAMES: List[str] = field(default_factory=lambda: ["Entity Setup", "Option Configuration", "Market Depth Analysis"])
    
    # Phase indices
    ENTITY_SETUP: int = 1
    OPTION_CONFIG: int = 2
    DEPTH_ANALYSIS: int = 3

# Create singleton instances
MARKET_MAKER = MarketMakerConfig()
DEFAULTS = DefaultValues()
UI = UIConfig()
VALIDATION = ValidationLimits()
RISK = RiskScoring()
CALC = CalculationParams()
FILES = FileConfig()
SESSIONS = SessionKeys()
ERRORS = ErrorMessages()
SUCCESS = SuccessMessages()
PHASES = PhaseConfig()
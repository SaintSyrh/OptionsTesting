"""
Configuration constants for financial models

This module centralizes all magic numbers and model parameters used throughout
the options pricing and depth valuation system. All values are based on
academic literature and empirical market data.
"""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class AlmgrenChrissConfig:
    """Almgren-Chriss market impact model parameters"""
    ALPHA_DEFAULT: float = 0.1          # Market impact coefficient
    ALPHA_MIN: float = 0.01             # Minimum reasonable alpha
    ALPHA_MAX: float = 1.0              # Maximum reasonable alpha
    VOLATILITY_SCALING: float = 1.0     # Volatility scaling factor


@dataclass
class KyleLambdaConfig:
    """Kyle's Lambda model parameters"""
    LAMBDA_BASE: float = 0.001          # Base lambda value
    DEPTH_DIVISOR: float = 2.0          # Lambda = 1/(2*Depth)
    MIN_DEPTH: float = 1000.0           # Minimum depth for calculations
    PRICE_SCALING: float = 10.0         # Default asset price for scaling


@dataclass
class BouchaudConfig:
    """Bouchaud Power Law model parameters"""
    DELTA_DEFAULT: float = 0.6          # Power law exponent
    DELTA_MIN: float = 0.1              # Minimum delta
    DELTA_MAX: float = 1.0              # Maximum delta
    Y_COEFFICIENT: float = 1.0          # Bouchaud Y coefficient
    VOLUME_SCALING: float = 1.0         # Volume normalization factor


@dataclass
class AmihudConfig:
    """Amihud Illiquidity model parameters"""
    MIN_VOLUME: float = 1.0             # Minimum volume to avoid division by zero
    RETURN_ABS_THRESHOLD: float = 1e-10 # Minimum return for calculations
    DEFAULT_RETURN: float = 0.001       # Default average return (0.1%)


@dataclass
class HawkesCascadeConfig:
    """Hawkes Process/Cascade model parameters"""
    BETA_DECAY: float = 2.0             # Hawkes process decay rate
    MU_BASE_INTENSITY: float = 0.1      # Base intensity parameter
    VOLATILITY_MULTIPLIER: float = 2.0  # Volume spike factor multiplier
    
    # Scaling factors (adjusted from original overly aggressive values)
    LIQUIDATION_SCALE: float = 0.01     # Liquidation protection scaling
    LIQUIDATION_FRACTION: float = 0.001 # Fraction of daily volume affected
    CASCADE_SCALE: float = 0.01         # Cascade value scaling
    SOCIAL_SCALE: float = 0.05          # Social momentum factor
    SOCIAL_FRACTION: float = 0.001      # Social dampening scaling


@dataclass
class ResilienceConfig:
    """Order Book Resilience/Recovery model parameters"""
    RHO_RECOVERY_BASE: float = 0.3      # Base recovery rate
    TIME_HORIZON_HOURS: float = 24.0    # Default analysis time horizon
    RECOVERY_DENOMINATOR: float = 100000.0  # Recovery rate calculation base
    
    # Scaling factors (improved from original)
    RECOVERY_VOLUME_FRACTION: float = 0.1     # Volume fraction for recovery
    RECOVERY_SCALE: float = 0.001             # Recovery value scaling
    PERMANENT_VOLUME_FRACTION: float = 0.2    # Permanent impact volume fraction
    PERMANENT_IMPACT_FRACTION: float = 0.3    # Fraction that becomes permanent
    PERMANENT_SCALE: float = 0.0001           # Permanent value scaling


@dataclass
class PINConfig:
    """Adverse Selection/PIN model parameters"""
    ALPHA_INFORMED: float = 0.2         # Informed trader arrival rate
    MU_INFO_EVENT: float = 0.1          # Information event rate
    EPSILON_BUY: float = 0.3            # Uninformed buy rate
    EPSILON_SELL: float = 0.3           # Uninformed sell rate
    
    # Spread adjustments
    TOXIC_SPREAD_MULTIPLIER: float = 2.0      # Toxic flow spread premium
    BENIGN_SPREAD_DISCOUNT: float = 0.5       # Benign flow spread discount
    BENIGN_LOSS_RATE: float = 0.3            # Opportunity cost on benign flow
    
    # Final scaling
    VOLUME_SCALE: float = 0.00001            # Scale by daily volume


@dataclass
class CrossVenueConfig:
    """Cross-Venue Arbitrage model parameters"""
    ARB_EFFICIENCY_BETA: float = 0.5    # Arbitrage efficiency factor
    MAX_IMPACT_REDUCTION: float = 0.5   # Maximum 50% impact reduction
    MM_IMPACT_REDUCTION: float = 0.7    # Higher reduction with MM
    
    # Value components
    ARB_VALUE_SCALE: float = 0.0001     # Arbitrage value scaling
    DISCOVERY_VOLUME_FRACTION: float = 0.1   # Price discovery volume fraction
    DISCOVERY_SCALE: float = 0.001      # Discovery value scaling


@dataclass
class CryptoDepthConfig:
    """Crypto-optimized depth calculator parameters"""
    
    # Exchange quality tiers
    EXCHANGE_TIERS: Dict[str, float] = field(default_factory=lambda: {
        # Tier 1: Major centralized exchanges
        'Binance': 0.90,
        'Coinbase': 0.88,
        'OKX': 0.85,
        'Bybit': 0.82,
        
        # Tier 2: Mid-tier exchanges
        'KuCoin': 0.75,
        'MEXC': 0.72,
        'Gate': 0.70,
        'Bitget': 0.68,
        
        # Tier 3: Smaller/DEX
        'Bitvavo': 0.60,
        'Other': 0.50,
    })
    
    # Target spreads for adjustment calculation
    TARGET_SPREADS: Dict[str, float] = field(default_factory=lambda: {
        '50bps': 60.0,
        '100bps': 110.0,
        '200bps': 210.0
    })
    
    # Spread tier base multipliers
    SPREAD_50BPS_EFFICIENCY: float = 0.95
    SPREAD_100BPS_EFFICIENCY: float = 0.78
    SPREAD_200BPS_EFFICIENCY: float = 0.55
    
    # Volatility parameters
    VOL_IMPACT_FACTOR: float = 1.5          # Crypto vol impact (gentler than trad)
    VOL_ADJUSTMENT_FLOOR: float = 0.25      # Minimum vol adjustment (vs 30% trad)
    
    # Spread bonus parameters
    SPREAD_BONUS_FACTOR: float = 1000.0     # How much tighter spreads matter
    SPREAD_BONUS_MIN: float = 0.7           # Min spread adjustment
    SPREAD_BONUS_MAX: float = 1.3           # Max spread adjustment
    
    # Liquidity parameters
    LIQUIDITY_BONUS_THRESHOLD: float = 100000.0  # $100k threshold
    LIQUIDITY_BONUS_MAX: float = 1.25            # Max 25% bonus
    LIQUIDITY_LOG_MULTIPLIER: float = 0.25       # Log bonus multiplier
    
    # MEV and cascade parameters
    MEV_TIGHT_SPREAD_THRESHOLD: float = 25.0     # <25bps vulnerable to MEV
    MEV_PENALTY_FACTOR: float = 0.95             # 5% MEV penalty
    CASCADE_PROTECTION_BONUS: float = 1.1        # 10% cascade bonus


@dataclass
class ModelWeightsConfig:
    """Model composition weights for different scenarios"""
    
    # Crypto-optimized weights (comprehensive 8-model framework)
    CRYPTO_WEIGHTS: Dict[str, float] = field(default_factory=lambda: {
        # Original models (adjusted down for new models)
        'almgren_chriss': 0.25,        # Reduced from 35%
        'kyle_lambda': 0.20,           # Reduced from 25%
        'bouchaud_power': 0.15,        # Reduced from 30%
        'amihud': 0.05,               # Kept as sanity check
        
        # New critical crypto models
        'resilience': 0.15,            # Temporal recovery dynamics
        'adverse_selection': 0.10,     # Flow toxicity filtering
        'cross_venue': 0.05,          # Arbitrage effects
        'hawkes_cascade': 0.05         # Liquidation/momentum cascades
    })
    
    # Traditional weights (legacy 4-model framework)
    TRADITIONAL_WEIGHTS: Dict[str, float] = field(default_factory=lambda: {
        'almgren_chriss': 0.4,
        'kyle_lambda': 0.3,
        'bouchaud_power': 0.2,
        'amihud': 0.1,
        'resilience': 0.0,
        'adverse_selection': 0.0,
        'cross_venue': 0.0,
        'hawkes_cascade': 0.0
    })


@dataclass
class ValidationConfig:
    """Input validation bounds and constraints"""
    
    # Option pricing bounds
    MIN_SPOT_PRICE: float = 0.01
    MAX_SPOT_PRICE: float = 1000000.0
    MIN_STRIKE_PRICE: float = 0.01
    MAX_STRIKE_PRICE: float = 1000000.0
    MIN_TIME_TO_EXPIRY: float = 0.001  # ~9 hours
    MAX_TIME_TO_EXPIRY: float = 10.0   # 10 years
    MIN_RISK_FREE_RATE: float = -0.1   # -10% (negative rates possible)
    MAX_RISK_FREE_RATE: float = 1.0    # 100%
    
    # Volatility bounds (crypto vs traditional)
    MIN_VOLATILITY_CRYPTO: float = 0.001    # 0.1%
    MAX_VOLATILITY_CRYPTO: float = 10.0     # 1000%
    MIN_VOLATILITY_TRADITIONAL: float = 0.05 # 5%
    MAX_VOLATILITY_TRADITIONAL: float = 2.0  # 200%
    
    # Depth analysis bounds
    MIN_DEPTH_VALUE: float = 1.0
    MAX_DEPTH_VALUE: float = 1000000000.0  # $1B
    MIN_BID_ASK_SPREAD: float = 0.1        # 0.1 bps
    MAX_BID_ASK_SPREAD: float = 10000.0    # 100%
    
    # Volume bounds
    MIN_DAILY_VOLUME: float = 1000.0       # $1k minimum
    MAX_DAILY_VOLUME: float = 10000000000.0 # $10B maximum


# Singleton instances for easy import
ALMGREN_CHRISS = AlmgrenChrissConfig()
KYLE_LAMBDA = KyleLambdaConfig()
BOUCHAUD = BouchaudConfig()
AMIHUD = AmihudConfig()
HAWKES_CASCADE = HawkesCascadeConfig()
RESILIENCE = ResilienceConfig()
PIN = PINConfig()
CROSS_VENUE = CrossVenueConfig()
CRYPTO_DEPTH = CryptoDepthConfig()
MODEL_WEIGHTS = ModelWeightsConfig()
VALIDATION = ValidationConfig()


def get_model_config(model_name: str) -> object:
    """Get configuration for a specific model"""
    config_map = {
        'almgren_chriss': ALMGREN_CHRISS,
        'kyle_lambda': KYLE_LAMBDA,
        'bouchaud': BOUCHAUD,
        'amihud': AMIHUD,
        'hawkes_cascade': HAWKES_CASCADE,
        'resilience': RESILIENCE,
        'pin': PIN,
        'cross_venue': CROSS_VENUE,
        'crypto_depth': CRYPTO_DEPTH,
        'weights': MODEL_WEIGHTS,
        'validation': VALIDATION,
    }
    return config_map.get(model_name)


def validate_weights(weights: Dict[str, float], tolerance: float = 1e-6) -> bool:
    """Validate that model weights sum to 1.0"""
    total = sum(weights.values())
    return abs(total - 1.0) < tolerance
"""
Data models for type safety, validation, and structured data handling.
These models ensure data integrity throughout the application.
"""
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass, field


class ValidationError(Exception):
    """Custom validation error"""
    pass


@dataclass
class MarketParameters:
    """Global market parameters used across calculations"""
    total_valuation: float
    total_tokens: float
    volatility: float
    risk_free_rate: float
    
    def __post_init__(self):
        """Validate market parameters"""
        if self.total_valuation <= 0:
            raise ValidationError("Total valuation must be positive")
        if self.total_tokens <= 0:
            raise ValidationError("Total tokens must be positive")
        if self.volatility <= 0:
            raise ValidationError("Volatility must be positive")
        if self.risk_free_rate < 0:
            raise ValidationError("Risk-free rate cannot be negative")
    
    @property
    def token_price(self) -> float:
        """Calculate price per token"""
        return self.total_valuation / self.total_tokens if self.total_tokens > 0 else 0.0
    
    def to_dict(self) -> Dict[str, float]:
        """Convert parameters to dictionary"""
        return {
            'total_valuation': self.total_valuation,
            'total_tokens': self.total_tokens,
            'volatility': self.volatility,
            'risk_free_rate': self.risk_free_rate,
            'token_price': self.token_price
        }


class Entity:
    """Entity model for company/loan information"""
    
    def __init__(self, name: str, loan_duration: int):
        self.name = self._validate_string(name, "name")
        self.loan_duration = self._validate_loan_duration(loan_duration)
    
    def _validate_string(self, value: str, name: str) -> str:
        """Validate string value"""
        if not isinstance(value, str):
            raise ValidationError(f"{name} must be a string")
        
        value = value.strip()
        if not value:
            raise ValidationError(f"{name} cannot be empty")
        
        return value
    
    def _validate_loan_duration(self, value: int) -> int:
        """Validate loan duration"""
        if not isinstance(value, (int, float)):
            raise ValidationError("Loan duration must be numeric")
        
        value = int(value)
        constraints = VALIDATION_CONSTRAINTS['loan_duration']
        
        if value < constraints['min'] or value > constraints['max']:
            raise ValidationError(f"Loan duration must be between {constraints['min']} and {constraints['max']}")
        
        return value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'loan_duration': self.loan_duration
        }


class SessionState:
    """Model for session state data"""
    
    def __init__(self):
        self.current_phase = 1
        self.entities_data = []
        self.tranches_data = []
        self.quoting_depths_data = []
        self.calculation_results = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'current_phase': self.current_phase,
            'entities_data': self.entities_data,
            'tranches_data': self.tranches_data,
            'quoting_depths_data': self.quoting_depths_data,
            'calculation_results': self.calculation_results
        }


class ExportData:
    """Model for data export"""
    
    def __init__(self, entities: List[Dict], tranches: List[Dict], 
                 quoting_depths: List[Dict], timestamp: Optional[datetime] = None):
        self.entities = entities
        self.tranches = tranches
        self.quoting_depths = quoting_depths
        self.timestamp = timestamp or datetime.now()
        self.metadata = {
            'version': '1.0',
            'application': 'Options Pricing Calculator'
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'entities': self.entities,
            'tranches': self.tranches,
            'quoting_depths': self.quoting_depths,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }


# Validation utility functions
def validate_entity_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate entity data and return validated dict"""
    try:
        entity = Entity(data['name'], data['loan_duration'])
        return entity.to_dict()
    except KeyError as e:
        raise ValidationError(f"Missing required field: {e}")


def validate_tranche_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate tranche data and return validated dict"""
    # Basic validation for tranche data
    required_fields = ['entity', 'option_type', 'strike_price', 'time_to_expiration']
    
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"Missing required field: {field}")
    
    # Validate option type
    if data['option_type'] not in OPTION_TYPES:
        raise ValidationError(f"Invalid option type: {data['option_type']}")
    
    # Validate numeric fields
    if not isinstance(data['strike_price'], (int, float)) or data['strike_price'] <= 0:
        raise ValidationError("Strike price must be positive numeric value")
    
    if not isinstance(data['time_to_expiration'], (int, float)) or data['time_to_expiration'] <= 0:
        raise ValidationError("Time to expiration must be positive numeric value")
    
    return data


def validate_quoting_depth_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate quoting depth data and return validated dict"""
    required_fields = ['entity', 'exchange', 'bid_ask_spread', 'depth_50bps', 'depth_100bps', 'depth_200bps']
    
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"Missing required field: {field}")
    
    # Validate numeric fields
    numeric_fields = ['bid_ask_spread', 'depth_50bps', 'depth_100bps', 'depth_200bps']
    for field in numeric_fields:
        if not isinstance(data[field], (int, float)) or data[field] < 0:
            raise ValidationError(f"{field} must be non-negative numeric value")
    
    return data


def validate_base_parameters(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate base parameters and return validated dict"""
    try:
        params = MarketParameters(
            data['total_valuation'],
            data['total_tokens'],
            data['volatility'],
            data['risk_free_rate']
        )
        return params.to_dict()
    except KeyError as e:
        raise ValidationError(f"Missing required field: {e}")


# Additional data models for comprehensive type safety

@dataclass
class OptionContract:
    """Represents an option contract configuration"""
    entity: str
    option_type: str  # 'call' or 'put'
    loan_duration: int
    start_month: int
    time_to_expiration: float
    token_share_pct: float
    strike_price: float
    valuation_method: str  # 'FDV Valuation' or 'Premium from Current FDV'
    token_valuation: Optional[float] = None
    current_fdv: Optional[float] = None
    premium_pct: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate option contract data"""
        if self.option_type not in ['call', 'put']:
            raise ValidationError("Option type must be 'call' or 'put'")
        if self.token_share_pct <= 0 or self.token_share_pct > 100:
            raise ValidationError("Token share percentage must be between 0 and 100")
        if self.strike_price <= 0:
            raise ValidationError("Strike price must be positive")
        if self.time_to_expiration <= 0:
            raise ValidationError("Time to expiration must be positive")
    
    @property
    def option_value_estimate(self) -> float:
        """Estimate option value based on valuation method"""
        if self.valuation_method == "FDV Valuation" and self.token_valuation:
            return self.token_valuation * (self.token_share_pct / 100.0)
        elif self.current_fdv:
            return self.current_fdv * (self.token_share_pct / 100.0)
        return 0.0

@dataclass
class MarketDepth:
    """Represents market depth data for an entity"""
    entity: str
    exchange: str
    spread: float  # in basis points
    depth_50: float  # depth at 50bps in USD
    depth_100: float  # depth at 100bps in USD
    depth_200: float  # depth at 200bps in USD
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate market depth data"""
        if self.spread < 0:
            raise ValidationError("Spread cannot be negative")
        if any(depth < 0 for depth in [self.depth_50, self.depth_100, self.depth_200]):
            raise ValidationError("Depth values cannot be negative")
    
    @property
    def total_raw_depth(self) -> float:
        """Calculate total raw depth across all levels"""
        return self.depth_50 + self.depth_100 + self.depth_200
    
    @property
    def spread_decimal(self) -> float:
        """Convert spread from basis points to decimal"""
        return self.spread / 10000.0

@dataclass
class EffectiveDepthResult:
    """Result from effective depth calculation"""
    entity: str
    exchange: str
    total_raw_depth: float
    total_effective_depth: float
    overall_efficiency: float
    calculation_timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def efficiency_percentage(self) -> float:
        """Get efficiency as percentage"""
        return self.overall_efficiency * 100.0

@dataclass
class MarketMakerValuation:
    """Result from market maker valuation calculation"""
    entity: str
    exchange: str
    total_value: float
    spread_cost: float
    net_value_after_spread: float
    model_components: Dict[str, float] = field(default_factory=dict)
    calculation_timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def profitability_ratio(self) -> float:
        """Calculate profitability ratio (net value / total value)"""
        return self.net_value_after_spread / self.total_value if self.total_value > 0 else 0.0

@dataclass
class EntitySummary:
    """Comprehensive summary for an entity"""
    entity: str
    exchanges: List[str]
    total_mm_value: float
    total_spread_cost: float
    total_net_value: float
    option_value: float
    effective_depth: float
    mm_efficiency: float  # Net MM value as % of option value
    depth_coverage: float  # How many times depth covers option value
    risk_score: int  # 1-4 scale
    
    @property
    def risk_level(self) -> str:
        """Get risk level description"""
        risk_levels = {1: "Low Risk", 2: "Medium Risk", 3: "High Risk", 4: "Very High Risk"}
        return risk_levels.get(self.risk_score, "Unknown Risk")

@dataclass
class CalculationResult:
    """Generic calculation result with error handling"""
    success: bool
    value: Optional[float] = None
    error: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def success_result(cls, value: float, details: Optional[Dict[str, Any]] = None) -> 'CalculationResult':
        """Create a successful calculation result"""
        return cls(success=True, value=value, details=details or {})
    
    @classmethod
    def error_result(cls, error: str, details: Optional[Dict[str, Any]] = None) -> 'CalculationResult':
        """Create an error calculation result"""
        return cls(success=False, error=error, details=details or {})

# Type aliases for better code readability
EntityList = List[Entity]
OptionContractList = List[OptionContract]
MarketDepthList = List[MarketDepth]
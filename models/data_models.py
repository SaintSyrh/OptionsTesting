"""
Data models for the Options Pricing Calculator with basic validation
"""
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from config.settings import VALIDATION_CONSTRAINTS, OPTION_TYPES, EXCHANGES


class ValidationError(Exception):
    """Custom validation error"""
    pass


class BaseParameters:
    """Base parameters model for market data"""
    
    def __init__(self, total_valuation: float, total_tokens: float, 
                 volatility: float, risk_free_rate: float, 
                 token_price: Optional[float] = None):
        self.total_valuation = self._validate_numeric(total_valuation, "total_valuation", 
                                                     VALIDATION_CONSTRAINTS['total_valuation'])
        self.total_tokens = self._validate_numeric(total_tokens, "total_tokens",
                                                  VALIDATION_CONSTRAINTS['total_tokens'])
        self.volatility = self._validate_numeric(volatility, "volatility",
                                                VALIDATION_CONSTRAINTS['volatility'])
        self.risk_free_rate = self._validate_numeric(risk_free_rate, "risk_free_rate",
                                                    VALIDATION_CONSTRAINTS['risk_free_rate'])
        
        # Calculate token price
        if token_price is None and total_tokens > 0:
            self.token_price = total_valuation / total_tokens
        else:
            self.token_price = token_price
    
    def _validate_numeric(self, value: Union[int, float], name: str, constraints: Dict) -> float:
        """Validate numeric value against constraints"""
        if not isinstance(value, (int, float)):
            raise ValidationError(f"{name} must be numeric")
        
        if value < constraints['min'] or value > constraints['max']:
            raise ValidationError(f"{name} must be between {constraints['min']} and {constraints['max']}")
        
        return float(value)
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary"""
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
        params = BaseParameters(
            data['total_valuation'],
            data['total_tokens'],
            data['volatility'],
            data['risk_free_rate'],
            data.get('token_price')
        )
        return params.to_dict()
    except KeyError as e:
        raise ValidationError(f"Missing required field: {e}")
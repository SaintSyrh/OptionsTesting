"""
Business logic services for financial calculations.
Separates calculation logic from UI concerns.
"""

from typing import Dict, List, Tuple, Optional, Any
import pandas as pd
from datetime import datetime

from models.data_models import (
    MarketParameters, OptionContract, MarketDepth, EffectiveDepthResult,
    MarketMakerValuation, EntitySummary, CalculationResult, ValidationError
)
from config.constants import MARKET_MAKER, DEFAULTS, RISK, CALC
from utils.error_handling import (
    calculation_handler, validate_option_parameters, 
    ParameterValidator, SafeOperations
)
from option_pricing import black_scholes_call, black_scholes_put, calculate_greeks
from depth_valuation import DepthValuationModels, generate_trade_size_distribution
from crypto_depth_calculator import CryptoEffectiveDepthCalculator


class OptionPricingService:
    """Service for option pricing calculations"""
    
    @calculation_handler
    def calculate_option_value(
        self, 
        option: OptionContract,
        market_params: MarketParameters
    ) -> CalculationResult:
        """
        Calculate option value using Black-Scholes model
        
        Args:
            option: Option contract configuration
            market_params: Market parameters
        
        Returns:
            CalculationResult with option value or error
        """
        try:
            # Determine spot price based on valuation method
            if option.valuation_method == "FDV Valuation":
                if option.token_valuation is None:
                    return CalculationResult.error_result("Token valuation is required for FDV method")
                
                S = option.token_valuation
                total_option_value = S * (option.token_share_pct / CALC.PERCENTAGE_DIVISOR)
                
                return CalculationResult.success_result(
                    total_option_value,
                    details={
                        'method': 'FDV_Valuation',
                        'spot_price': S,
                        'token_share_pct': option.token_share_pct,
                        'calculation_type': 'direct_valuation'
                    }
                )
            else:
                # Premium from current FDV method
                if option.current_fdv is None:
                    return CalculationResult.error_result("Current FDV is required for premium method")
                
                S = option.current_fdv
                K = option.strike_price
                T = option.time_to_expiration
                r = market_params.risk_free_rate
                sigma = market_params.volatility
                
                # Validate parameters
                validated_params = validate_option_parameters(S, K, T, r, sigma)
                
                # Calculate option price using Black-Scholes
                if option.option_type == 'call':
                    option_price = black_scholes_call(S, K, T, r, sigma)
                else:
                    option_price = black_scholes_put(S, K, T, r, sigma)
                
                # Apply token share percentage
                total_option_value = option_price * (option.token_share_pct / CALC.PERCENTAGE_DIVISOR)
                
                return CalculationResult.success_result(
                    total_option_value,
                    details={
                        'method': 'Black_Scholes',
                        'option_price_per_unit': option_price,
                        'token_share_pct': option.token_share_pct,
                        'parameters': validated_params
                    }
                )
                
        except Exception as e:
            return CalculationResult.error_result(f"Option valuation failed: {str(e)}")
    
    @calculation_handler
    def calculate_greeks(
        self,
        option: OptionContract,
        market_params: MarketParameters
    ) -> Dict[str, float]:
        """Calculate option Greeks"""
        if option.valuation_method != "Premium from Current FDV" or option.current_fdv is None:
            return {}
        
        S = option.current_fdv
        K = option.strike_price
        T = option.time_to_expiration
        r = market_params.risk_free_rate
        sigma = market_params.volatility
        
        return calculate_greeks(S, K, T, r, sigma, option.option_type)


class EffectiveDepthService:
    """Service for effective depth calculations"""
    
    def __init__(self):
        self.calculator = CryptoEffectiveDepthCalculator()
    
    @calculation_handler
    def calculate_entity_effective_depth(
        self, 
        market_depth: MarketDepth
    ) -> EffectiveDepthResult:
        """
        Calculate effective depth for a single entity-exchange combination
        
        Args:
            market_depth: Market depth data
        
        Returns:
            EffectiveDepthResult with calculated values
        """
        result = self.calculator.calculate_entity_effective_depth(
            depth_50bps=market_depth.depth_50,
            depth_100bps=market_depth.depth_100,
            depth_200bps=market_depth.depth_200,
            bid_ask_spread=market_depth.spread,
            volatility=MARKET_MAKER.DEFAULT_VOLATILITY,
            exchange=market_depth.exchange
        )
        
        return EffectiveDepthResult(
            entity=market_depth.entity,
            exchange=market_depth.exchange,
            total_raw_depth=result['total_raw_depth'],
            total_effective_depth=result['total_effective_depth'],
            overall_efficiency=result['overall_efficiency']
        )
    
    @calculation_handler
    def calculate_cumulative_depths_by_entity(
        self,
        depths: List[MarketDepth]
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculate cumulative effective depths grouped by entity
        
        Args:
            depths: List of market depth data
        
        Returns:
            Dictionary mapping entity name to cumulative depth metrics
        """
        entity_totals = {}
        
        for depth in depths:
            effective_depth_result = self.calculate_entity_effective_depth(depth)
            
            if depth.entity not in entity_totals:
                entity_totals[depth.entity] = {
                    'raw_depth': 0,
                    'effective_depth': 0,
                    'exchanges': []
                }
            
            entity_totals[depth.entity]['raw_depth'] += effective_depth_result.total_raw_depth
            entity_totals[depth.entity]['effective_depth'] += effective_depth_result.total_effective_depth
            entity_totals[depth.entity]['exchanges'].append(depth.exchange)
        
        # Calculate overall efficiency for each entity
        for entity, totals in entity_totals.items():
            totals['overall_efficiency'] = SafeOperations.safe_divide(
                totals['effective_depth'],
                totals['raw_depth'],
                default=0.0
            )
        
        return entity_totals


class MarketMakerService:
    """Service for market maker valuation calculations"""
    
    def __init__(self):
        self.models = DepthValuationModels()
    
    @calculation_handler
    def calculate_market_maker_valuation(
        self,
        market_depth: MarketDepth,
        market_params: MarketParameters
    ) -> MarketMakerValuation:
        """
        Calculate market maker valuation for a single depth entry
        
        Args:
            market_depth: Market depth data
            market_params: Market parameters
        
        Returns:
            MarketMakerValuation result
        """
        # Prepare calculation parameters
        depth_0 = market_depth.total_raw_depth
        spread_0 = market_depth.spread_decimal
        spread_1 = spread_0 * MARKET_MAKER.SPREAD_REDUCTION_FACTOR
        
        # Get trade size distribution
        trade_sizes, probabilities = generate_trade_size_distribution()
        
        # Calculate spread cost (adverse selection)
        spread_cost = (spread_0 / 2) * MARKET_MAKER.DAILY_VOLUME * MARKET_MAKER.ADVERSE_SELECTION_RATE
        
        # Calculate composite valuation
        result = self.models.composite_valuation(
            spread_0=spread_0,
            spread_1=spread_1,
            volatility=market_params.volatility,
            trade_sizes=trade_sizes[:CALC.TRADE_SIZE_SAMPLE_SIZE],
            probabilities=probabilities[:CALC.TRADE_SIZE_SAMPLE_SIZE],
            volume_0=MARKET_MAKER.DAILY_VOLUME,
            volume_mm=MARKET_MAKER.MM_VOLUME,
            depth_0=depth_0,
            depth_mm=depth_0 * MARKET_MAKER.DEPTH_INCREASE_FACTOR,
            daily_volume_0=MARKET_MAKER.DAILY_VOLUME,
            daily_volume_mm=MARKET_MAKER.MM_VOLUME,
            asset_price=market_params.token_price,
            use_crypto_weights=True
        )
        
        return MarketMakerValuation(
            entity=market_depth.entity,
            exchange=market_depth.exchange,
            total_value=result['total_value'],
            spread_cost=spread_cost,
            net_value_after_spread=result['total_value'] - spread_cost,
            model_components=result
        )
    
    def calculate_entity_summaries(
        self,
        mm_valuations: List[MarketMakerValuation],
        option_values: Dict[str, float],
        effective_depths: Dict[str, float]
    ) -> List[EntitySummary]:
        """
        Calculate comprehensive entity summaries
        
        Args:
            mm_valuations: List of market maker valuations
            option_values: Dictionary mapping entity to total option value
            effective_depths: Dictionary mapping entity to total effective depth
        
        Returns:
            List of EntitySummary objects
        """
        # Group valuations by entity
        entity_mm_data = {}
        for valuation in mm_valuations:
            entity = valuation.entity
            if entity not in entity_mm_data:
                entity_mm_data[entity] = {
                    'exchanges': [],
                    'total_value': 0,
                    'total_spread_cost': 0,
                    'total_net_value': 0
                }
            
            entity_mm_data[entity]['exchanges'].append(valuation.exchange)
            entity_mm_data[entity]['total_value'] += valuation.total_value
            entity_mm_data[entity]['total_spread_cost'] += valuation.spread_cost
            entity_mm_data[entity]['total_net_value'] += valuation.net_value_after_spread
        
        # Create entity summaries
        summaries = []
        for entity, mm_data in entity_mm_data.items():
            option_value = option_values.get(entity, 1)  # Avoid division by zero
            effective_depth = effective_depths.get(entity, 0)
            
            # Calculate metrics
            mm_efficiency = SafeOperations.safe_divide(
                mm_data['total_net_value'],
                option_value,
                default=0.0
            ) * CALC.PERCENTAGE_DIVISOR
            
            depth_coverage = SafeOperations.safe_divide(
                effective_depth,
                option_value,
                default=0.0
            )
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(depth_coverage)
            
            summaries.append(EntitySummary(
                entity=entity,
                exchanges=list(set(mm_data['exchanges'])),
                total_mm_value=mm_data['total_value'],
                total_spread_cost=mm_data['total_spread_cost'],
                total_net_value=mm_data['total_net_value'],
                option_value=option_value,
                effective_depth=effective_depth,
                mm_efficiency=mm_efficiency,
                depth_coverage=depth_coverage,
                risk_score=risk_score
            ))
        
        return summaries
    
    def _calculate_risk_score(self, depth_coverage: float) -> int:
        """Calculate risk score based on depth coverage"""
        if depth_coverage >= RISK.LOW_RISK_THRESHOLD:
            return 1
        elif depth_coverage >= RISK.MEDIUM_RISK_THRESHOLD:
            return 2
        elif depth_coverage >= RISK.HIGH_RISK_THRESHOLD:
            return 3
        else:
            return 4


class CalculationOrchestrator:
    """Orchestrates all calculations for the application"""
    
    def __init__(self):
        self.option_service = OptionPricingService()
        self.depth_service = EffectiveDepthService()
        self.mm_service = MarketMakerService()
    
    def calculate_comprehensive_analysis(
        self,
        entities: List[Dict[str, Any]],
        options: List[Dict[str, Any]],
        depths: List[Dict[str, Any]],
        market_params: MarketParameters
    ) -> Dict[str, Any]:
        """
        Perform comprehensive analysis combining all calculations
        
        Returns:
            Dictionary with all calculation results
        """
        results = {
            'option_values': {},
            'effective_depths': {},
            'mm_valuations': [],
            'entity_summaries': [],
            'total_mm_value': 0,
            'calculation_timestamp': datetime.now()
        }
        
        try:
            # Convert dictionaries to data model objects
            option_contracts = [OptionContract(**opt) for opt in options]
            market_depths = [MarketDepth(**depth) for depth in depths]
            
            # Calculate option values
            for option in option_contracts:
                result = self.option_service.calculate_option_value(option, market_params)
                if result.success:
                    entity = option.entity
                    if entity not in results['option_values']:
                        results['option_values'][entity] = 0
                    results['option_values'][entity] += result.value
            
            # Calculate effective depths
            entity_depths = self.depth_service.calculate_cumulative_depths_by_entity(market_depths)
            for entity, depth_data in entity_depths.items():
                results['effective_depths'][entity] = depth_data['effective_depth']
            
            # Calculate market maker valuations
            for depth in market_depths:
                mm_result = self.mm_service.calculate_market_maker_valuation(depth, market_params)
                results['mm_valuations'].append(mm_result)
                results['total_mm_value'] += mm_result.net_value_after_spread
            
            # Calculate entity summaries
            results['entity_summaries'] = self.mm_service.calculate_entity_summaries(
                results['mm_valuations'],
                results['option_values'],
                results['effective_depths']
            )
            
        except Exception as e:
            results['error'] = str(e)
        
        return results
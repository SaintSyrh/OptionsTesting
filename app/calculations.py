"""
Business logic for options pricing and depth calculations
"""
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

from option_pricing import black_scholes_call, black_scholes_put, calculate_greeks
from depth_valuation import DepthValuationModels, generate_trade_size_distribution
from crypto_depth_calculator import CryptoEffectiveDepthCalculator
from app.session_state import session_manager

logger = logging.getLogger(__name__)


class CalculationOrchestrator:
    """Orchestrates all calculation operations"""
    
    def __init__(self):
        self.session_manager = session_manager
        self.depth_models = DepthValuationModels()
        self.crypto_calc = CryptoEffectiveDepthCalculator()
    
    def perform_options_calculations(self, params: Dict[str, float]) -> Dict[str, Any]:
        """Perform Black-Scholes options calculations"""
        try:
            logger.info("Starting options calculations")
            
            tranches = self.session_manager.get_tranches()
            if not tranches:
                raise ValueError("No tranches available for calculation")
            
            results = {
                'tranches': [],
                'entities': {},
                'total_portfolio_value': 0,
                'calculation_timestamp': datetime.now()
            }
            
            for tranche in tranches:
                tranche_result = self._calculate_single_tranche(tranche, params)
                results['tranches'].append(tranche_result)
                results['total_portfolio_value'] += tranche_result['total_value']
                
                # Group by entity
                entity = tranche['entity']
                if entity not in results['entities']:
                    results['entities'][entity] = []
                results['entities'][entity].append(tranche_result)
            
            logger.info(f"Options calculations completed. Total portfolio value: ${results['total_portfolio_value']:,.2f}")
            return results
            
        except Exception as e:
            logger.error(f"Error in options calculations: {e}")
            raise
    
    def _calculate_single_tranche(self, tranche: Dict[str, Any], params: Dict[str, float]) -> Dict[str, Any]:
        """Calculate single tranche option value"""
        try:
            S = params['token_price']
            K = tranche['strike_price']
            T = tranche['time_to_expiration']
            r = params['risk_free_rate']
            sigma = params['volatility']
            
            # Calculate number of tokens and percentage based on allocation method
            if tranche['allocation_method'] == "Percentage of Total Tokens":
                num_tokens = (tranche['token_percentage'] / 100.0) * params['total_tokens']
                token_percentage = tranche['token_percentage']
            else:  # Absolute Token Count
                num_tokens = tranche['token_count']
                token_percentage = (num_tokens / params['total_tokens']) * 100.0
            
            # Calculate option price per token
            if tranche['option_type'] == 'call':
                option_price = black_scholes_call(S, K, T, r, sigma)
            else:
                option_price = black_scholes_put(S, K, T, r, sigma)
            
            # Total value of this tranche
            total_value = option_price * num_tokens
            
            # Calculate Greeks
            greeks = calculate_greeks(S, K, T, r, sigma)
            
            tranche_result = {
                **tranche,
                'num_tokens': num_tokens,
                'token_percentage': token_percentage,
                'option_price_per_token': option_price,
                'total_value': total_value,
                'greeks': greeks
            }
            
            return tranche_result
            
        except Exception as e:
            logger.error(f"Error calculating tranche: {e}")
            raise
    
    def calculate_advanced_depth_valuation(self, params: Dict[str, float]) -> Optional[Dict[str, Any]]:
        """Calculate advanced market maker depth valuation using multiple models"""
        try:
            quoting_depths = self.session_manager.get_quoting_depths()
            if not quoting_depths:
                logger.warning("No quoting depths data available")
                return None
            
            logger.info("Starting advanced depth valuation")
            
            # Generate trade size distribution
            trade_sizes, probabilities = generate_trade_size_distribution(
                min_size=1000, max_size=100000, num_buckets=20, distribution_type='log_normal'
            )
            
            advanced_results = {
                'entity_valuations': {},
                'model_comparisons': {},
                'parameters_used': {
                    'volatility': params['volatility'],
                    'token_price': params['token_price'],
                    'trade_sizes': trade_sizes,
                    'probabilities': probabilities
                }
            }
            
            for entry in quoting_depths:
                entity = entry['entity']
                
                if entity not in advanced_results['entity_valuations']:
                    advanced_results['entity_valuations'][entity] = {
                        'exchanges': {},
                        'total_mm_value': 0,
                        'model_breakdown': {}
                    }
                
                # Calculate market maker value for this entry
                mm_value = self._calculate_mm_value_for_entry(entry, params, trade_sizes, probabilities)
                
                # Store results
                exchange = entry['exchange']
                advanced_results['entity_valuations'][entity]['exchanges'][exchange] = {
                    'raw_depth_data': entry,
                    'market_maker_value': mm_value,
                }
                
                advanced_results['entity_valuations'][entity]['total_mm_value'] += mm_value['total_value']
                
                # Aggregate model breakdowns
                for model_name, model_result in mm_value['individual_models'].items():
                    if model_name not in advanced_results['entity_valuations'][entity]['model_breakdown']:
                        advanced_results['entity_valuations'][entity]['model_breakdown'][model_name] = 0
                    advanced_results['entity_valuations'][entity]['model_breakdown'][model_name] += model_result['total_value']
            
            logger.info("Advanced depth valuation completed")
            return advanced_results
            
        except Exception as e:
            logger.error(f"Error in advanced depth valuation: {e}")
            raise
    
    def _calculate_mm_value_for_entry(self, entry: Dict[str, Any], params: Dict[str, float], 
                                     trade_sizes: List[float], probabilities: List[float]) -> Dict[str, Any]:
        """Calculate market maker value for single depth entry"""
        try:
            # Extract depth and spread data
            spread_0 = entry['bid_ask_spread'] * 1.5 / 10000  # Convert bps to decimal
            spread_1 = entry['bid_ask_spread'] / 10000  # Current spread in decimal
            
            # Volume estimates
            base_daily_volume = 1000000  # $1M base daily volume
            volume_0 = base_daily_volume
            volume_mm = entry['depth_50bps'] + entry['depth_100bps'] + entry['depth_200bps']
            
            # Depth estimates
            depth_0 = volume_0 * 0.1  # Assume 10% of daily volume as base depth
            depth_mm = volume_mm
            
            # Calculate composite valuation with crypto-optimized weights
            mm_value = self.depth_models.composite_valuation(
                spread_0=spread_0,
                spread_1=spread_1,
                volatility=params['volatility'],
                trade_sizes=trade_sizes,
                probabilities=probabilities,
                volume_0=volume_0,
                volume_mm=volume_mm,
                depth_0=depth_0,
                depth_mm=depth_mm,
                daily_volume_0=base_daily_volume,
                daily_volume_mm=volume_mm,
                asset_price=params['token_price'],
                avg_return=0.001,
                use_crypto_weights=True
            )
            
            return mm_value
            
        except Exception as e:
            logger.error(f"Error calculating MM value for entry: {e}")
            raise
    
    def calculate_depth_value_analysis(self, params: Dict[str, float]) -> Optional[Dict[str, Any]]:
        """Calculate crypto-optimized depth value analysis"""
        try:
            quoting_depths = self.session_manager.get_quoting_depths()
            if not quoting_depths:
                logger.warning("No quoting depths data available")
                return None
            
            logger.info("Starting depth value analysis")
            
            analysis_results = {
                'entity_analyses': {},
                'overall_metrics': {},
                'advanced_valuation': self.calculate_advanced_depth_valuation(params),
                'calculation_method': 'Crypto-Empirical Optimization'
            }
            
            volatility = params['volatility']
            
            for entry in quoting_depths:
                entity = entry['entity']
                exchange = entry['exchange']
                
                if entity not in analysis_results['entity_analyses']:
                    analysis_results['entity_analyses'][entity] = {
                        'exchanges': {},
                        'total_quoted_value': 0,
                        'effective_quoted_value': 0,
                        'avg_spread': 0,
                        'depth_distribution': {'50bps': 0, '100bps': 0, '200bps': 0}
                    }
                
                # Calculate crypto-optimized effective depths
                crypto_result = self.crypto_calc.calculate_entity_effective_depth(
                    depth_50bps=entry['depth_50bps'],
                    depth_100bps=entry['depth_100bps'], 
                    depth_200bps=entry['depth_200bps'],
                    bid_ask_spread=entry['bid_ask_spread'],
                    volatility=volatility,
                    exchange=exchange
                )
                
                total_quoted = crypto_result['total_raw_depth']
                total_effective = crypto_result['total_effective_depth']
                
                # Store exchange analysis
                exchange_analysis = self._create_exchange_analysis(entry, crypto_result, total_quoted, total_effective)
                analysis_results['entity_analyses'][entity]['exchanges'][exchange] = exchange_analysis
                
                # Update entity totals
                analysis_results['entity_analyses'][entity]['total_quoted_value'] += total_quoted
                analysis_results['entity_analyses'][entity]['effective_quoted_value'] += total_effective
                
                # Update depth distribution
                analysis_results['entity_analyses'][entity]['depth_distribution']['50bps'] += entry['depth_50bps']
                analysis_results['entity_analyses'][entity]['depth_distribution']['100bps'] += entry['depth_100bps']
                analysis_results['entity_analyses'][entity]['depth_distribution']['200bps'] += entry['depth_200bps']
            
            # Calculate overall metrics
            analysis_results['overall_metrics'] = self._calculate_overall_metrics(analysis_results, volatility)
            
            logger.info("Depth value analysis completed")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error in depth value analysis: {e}")
            raise
    
    def _create_exchange_analysis(self, entry: Dict[str, Any], crypto_result: Dict[str, Any], 
                                 total_quoted: float, total_effective: float) -> Dict[str, Any]:
        """Create exchange analysis data structure"""
        tier_results = crypto_result['tier_results']
        effective_50bps = tier_results.get('50bps', {}).get('effective_depth', 0)
        effective_100bps = tier_results.get('100bps', {}).get('effective_depth', 0) 
        effective_200bps = tier_results.get('200bps', {}).get('effective_depth', 0)
        
        return {
            'bid_ask_spread': entry['bid_ask_spread'],
            'raw_depths': {
                '50bps': entry['depth_50bps'],
                '100bps': entry['depth_100bps'],
                '200bps': entry['depth_200bps']
            },
            'effective_depths': {
                '50bps': effective_50bps,
                '100bps': effective_100bps,
                '200bps': effective_200bps
            },
            'total_quoted_value': total_quoted,
            'total_effective_value': total_effective,
            'efficiency_ratio': total_effective / total_quoted if total_quoted > 0 else 0,
            'depth_method': entry.get('depth_method', 'Absolute Values ($)'),
            'percentages': {
                '50bps': entry.get('depth_50bps_pct'),
                '100bps': entry.get('depth_100bps_pct'),
                '200bps': entry.get('depth_200bps_pct')
            },
            'crypto_optimization': {
                'exchange_quality': self.crypto_calc.get_exchange_tier_multiplier(entry['exchange']),
                'overall_efficiency': crypto_result['overall_efficiency'],
                'methodology': crypto_result['methodology'],
                'tier_breakdowns': {tier: result['breakdown'] for tier, result in tier_results.items()}
            }
        }
    
    def _calculate_overall_metrics(self, analysis_results: Dict[str, Any], volatility: float) -> Dict[str, Any]:
        """Calculate overall analysis metrics"""
        total_quoted = sum(entity['total_quoted_value'] for entity in analysis_results['entity_analyses'].values())
        total_effective = sum(entity['effective_quoted_value'] for entity in analysis_results['entity_analyses'].values())
        
        # Calculate average volatility adjustment
        avg_vol_adjustment = self.crypto_calc.calculate_volatility_adjustment(volatility)
        
        return {
            'total_quoted_value': total_quoted,
            'total_effective_value': total_effective,
            'overall_efficiency': total_effective / total_quoted if total_quoted > 0 else 0,
            'volatility_adjustment': avg_vol_adjustment,
            'depth_tier_impact': {
                '50bps_multiplier': self.crypto_calc.spread_tier_multipliers['50bps'],
                '100bps_multiplier': self.crypto_calc.spread_tier_multipliers['100bps'], 
                '200bps_multiplier': self.crypto_calc.spread_tier_multipliers['200bps']
            }
        }
    
    def calculate_depth_options_ratio(self, params: Dict[str, float]) -> Optional[Dict[str, Any]]:
        """Calculate depth-to-options value ratio per entity"""
        try:
            calculation_results = self.session_manager.get_calculation_results()
            if not calculation_results:
                logger.warning("No calculation results available for ratio analysis")
                return None
            
            # Get option values per entity
            entity_option_values = {}
            for entity, tranches in calculation_results['entities'].items():
                entity_option_values[entity] = sum(t['total_value'] for t in tranches)
            
            # Get depth values per entity from analysis
            analysis = self.calculate_depth_value_analysis(params)
            if not analysis:
                return None
            
            ratio_data = {}
            
            for entity in entity_option_values.keys():
                option_value = entity_option_values[entity]
                
                # Traditional depth analysis
                traditional_data = {}
                if entity in analysis['entity_analyses']:
                    entity_data = analysis['entity_analyses'][entity]
                    traditional_data = {
                        'total_depth_value': entity_data['total_quoted_value'],
                        'effective_depth_value': entity_data['effective_quoted_value']
                    }
                
                # Advanced market maker valuation
                mm_value = 0
                if analysis.get('advanced_valuation') and entity in analysis['advanced_valuation']['entity_valuations']:
                    mm_value = analysis['advanced_valuation']['entity_valuations'][entity]['total_mm_value']
                
                # Combined metrics
                total_depth_value = traditional_data.get('total_depth_value', 0)
                effective_depth_value = traditional_data.get('effective_depth_value', 0)
                
                ratio_data[entity] = self._calculate_entity_ratios(
                    option_value, total_depth_value, effective_depth_value, mm_value
                )
            
            logger.info("Depth-options ratio calculation completed")
            return ratio_data
            
        except Exception as e:
            logger.error(f"Error calculating depth-options ratio: {e}")
            raise
    
    def _calculate_entity_ratios(self, option_value: float, total_depth: float, 
                                effective_depth: float, mm_value: float) -> Dict[str, Any]:
        """Calculate ratios for single entity"""
        return {
            'option_value': option_value,
            'total_depth_value': total_depth,
            'effective_depth_value': effective_depth,
            'market_maker_value': mm_value,
            'depth_to_option_ratio': total_depth / option_value if option_value > 0 else 0,
            'effective_depth_to_option_ratio': effective_depth / option_value if option_value > 0 else 0,
            'mm_to_option_ratio': mm_value / option_value if option_value > 0 else 0,
            'depth_coverage_percentage': (total_depth / option_value) * 100 if option_value > 0 else 0,
            'effective_coverage_percentage': (effective_depth / option_value) * 100 if option_value > 0 else 0,
            'mm_coverage_percentage': (mm_value / option_value) * 100 if option_value > 0 else 0
        }
    
    def validate_calculation_readiness(self) -> Dict[str, Any]:
        """Validate if ready to perform calculations"""
        validation_result = {
            'ready': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Check tranches
            tranches = self.session_manager.get_tranches()
            if not tranches:
                validation_result['errors'].append("No tranches configured")
                validation_result['ready'] = False
            
            # Check entities have depths
            entities_with_depths = self.session_manager.get_entities_with_depths()
            required_entities = self.session_manager.get_required_entities()
            missing_entities = required_entities - entities_with_depths
            
            if missing_entities:
                validation_result['errors'].append(f"Missing depths for: {', '.join(missing_entities)}")
                validation_result['ready'] = False
            
        except Exception as e:
            logger.error(f"Error validating calculation readiness: {e}")
            validation_result['errors'].append(f"Validation error: {e}")
            validation_result['ready'] = False
        
        return validation_result


# Global instance
calculation_orchestrator = CalculationOrchestrator()
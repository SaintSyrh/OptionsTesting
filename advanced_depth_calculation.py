import numpy as np
import math
from typing import Dict, List, Tuple, Optional

class AdvancedDepthCalculator:
    """
    Advanced effective depth calculation based on market microstructure models
    Incorporates fill probability, market impact, quality, and resilience factors
    """
    
    def __init__(self):
        self.default_params = {
            # Fill probability parameters
            'lambda_arrival': 0.1,      # Order arrival rate
            'queue_decay': 0.05,        # Queue position decay rate  
            'vol_impact_fill': 2.0,     # Volatility impact on fill probability
            
            # Market impact parameters  
            'impact_coeff': 0.1,        # Square-root impact coefficient
            'permanent_ratio': 0.3,     # Fraction of impact that's permanent
            
            # Quality/adverse selection
            'pin_base': 0.05,           # Base adverse selection rate
            'spread_quality_factor': 10, # How spread affects flow quality
            
            # Resilience/recovery
            'recovery_rate': 0.5,       # How fast depth recovers (per hour)
            'depth_stickiness': 0.8,    # How much depth stays after consumption
        }
    
    def calculate_fill_probability(self, 
                                 spread_bps: float,
                                 volatility: float, 
                                 volume_ahead: float = 0.0,
                                 time_horizon: float = 1.0) -> float:
        """
        Calculate probability that depth at this level will be available when needed
        
        P(fill) = e^(-λ*t) * e^(-σ*impact_factor) * queue_position_factor
        
        Args:
            spread_bps: Distance from mid in basis points
            volatility: Asset volatility (annual)
            volume_ahead: Volume ahead in queue
            time_horizon: Time horizon in hours
        """
        params = self.default_params
        
        # Queue position effect (more volume ahead = lower fill probability)
        queue_factor = math.exp(-params['queue_decay'] * volume_ahead / 100000)
        
        # Volatility effect (higher vol = orders get picked off faster)
        vol_factor = math.exp(-params['vol_impact_fill'] * volatility * time_horizon)
        
        # Spread effect (tighter spreads more likely to be hit)
        spread_factor = 1 / (1 + (spread_bps / 50) ** 0.5)  # Decay with spread
        
        # Base arrival/execution probability
        arrival_prob = 1 - math.exp(-params['lambda_arrival'] * time_horizon)
        
        fill_prob = arrival_prob * spread_factor * vol_factor * queue_factor
        return min(1.0, max(0.01, fill_prob))  # Bounded between 1% and 100%
    
    def calculate_market_impact(self, 
                              volume: float, 
                              volatility: float,
                              daily_volume: float = 1000000) -> float:
        """
        Calculate market impact of consuming this volume
        
        Impact = α * σ * √(V/V_daily) + permanent_component
        """
        params = self.default_params
        
        if daily_volume <= 0 or volume <= 0:
            return 0.0
        
        # Square-root impact (Almgren-Chriss style)
        temporary_impact = params['impact_coeff'] * volatility * math.sqrt(volume / daily_volume)
        
        # Permanent impact component
        permanent_impact = temporary_impact * params['permanent_ratio']
        
        # Total impact factor (reduces effective value)
        total_impact = temporary_impact + permanent_impact
        return min(0.95, total_impact)  # Cap at 95% impact
    
    def calculate_quality_factor(self, 
                                spread_bps: float, 
                                volatility: float) -> float:
        """
        Calculate quality of depth (inverse of adverse selection cost)
        
        Quality = 1 - PIN(spread, volatility)
        Lower spread + higher vol = more toxic flow = lower quality
        """
        params = self.default_params
        
        # PIN increases with volatility and decreases with spread
        pin_rate = params['pin_base'] * (volatility / 0.3) / (1 + spread_bps / params['spread_quality_factor'])
        pin_rate = min(0.8, max(0.01, pin_rate))  # Bounded
        
        quality = 1 - pin_rate
        return quality
    
    def calculate_resilience_factor(self, 
                                  depth: float, 
                                  volatility: float,
                                  time_horizon: float = 1.0) -> float:
        """
        Calculate how much depth will be available over time
        
        Resilience = depth_stickiness + recovery_rate * time_horizon
        """
        params = self.default_params
        
        # Base stickiness (how much remains immediately after hit)
        base_resilience = params['depth_stickiness']
        
        # Recovery component (depth refills over time)
        recovery_component = (1 - base_resilience) * (1 - math.exp(-params['recovery_rate'] * time_horizon))
        
        # Volatility reduces resilience (harder to maintain quotes in volatile markets)
        vol_penalty = math.exp(-volatility * 2)  # Higher vol = lower resilience
        
        total_resilience = (base_resilience + recovery_component) * vol_penalty
        return min(1.0, max(0.1, total_resilience))
    
    def calculate_effective_depth_advanced(self,
                                         depth_50bps: float,
                                         depth_100bps: float, 
                                         depth_200bps: float,
                                         bid_ask_spread: float,  # in bps
                                         volatility: float,
                                         daily_volume: float = 1000000,
                                         time_horizon: float = 1.0) -> Dict:
        """
        Calculate advanced effective depth using market microstructure models
        
        For each depth tier:
        effective_depth_i = depth_i * P(fill_i) * (1 - impact_i) * quality_i * resilience_i
        """
        
        tiers = {
            '50bps': {'depth': depth_50bps, 'spread': bid_ask_spread + 50},
            '100bps': {'depth': depth_100bps, 'spread': bid_ask_spread + 100}, 
            '200bps': {'depth': depth_200bps, 'spread': bid_ask_spread + 200}
        }
        
        results = {
            'total_raw_depth': depth_50bps + depth_100bps + depth_200bps,
            'total_effective_depth': 0.0,
            'tier_details': {},
            'efficiency_ratio': 0.0,
            'methodology': 'Advanced Market Microstructure'
        }
        
        cumulative_volume = 0.0
        
        for tier_name, tier_data in tiers.items():
            depth = tier_data['depth']
            spread = tier_data['spread']
            
            if depth <= 0:
                continue
            
            # Calculate all factors
            fill_prob = self.calculate_fill_probability(spread, volatility, cumulative_volume, time_horizon)
            market_impact = self.calculate_market_impact(depth, volatility, daily_volume)
            quality_factor = self.calculate_quality_factor(spread, volatility)  
            resilience_factor = self.calculate_resilience_factor(depth, volatility, time_horizon)
            
            # Effective depth for this tier
            effective_depth = depth * fill_prob * (1 - market_impact) * quality_factor * resilience_factor
            
            results['tier_details'][tier_name] = {
                'raw_depth': depth,
                'effective_depth': effective_depth,
                'fill_probability': fill_prob,
                'market_impact': market_impact,
                'quality_factor': quality_factor,
                'resilience_factor': resilience_factor,
                'efficiency': effective_depth / depth if depth > 0 else 0
            }
            
            results['total_effective_depth'] += effective_depth
            cumulative_volume += depth
        
        # Overall efficiency
        if results['total_raw_depth'] > 0:
            results['efficiency_ratio'] = results['total_effective_depth'] / results['total_raw_depth']
        
        return results
    
    def compare_methodologies(self,
                            depth_50bps: float,
                            depth_100bps: float,
                            depth_200bps: float, 
                            bid_ask_spread: float,
                            volatility: float) -> Dict:
        """
        Compare current simple method vs advanced method
        """
        # Current simple method
        simple_multipliers = {'50bps': 1.0, '100bps': 0.75, '200bps': 0.50}
        simple_vol_adj = max(0.3, 1.0 - (volatility * 2))
        
        simple_effective = (
            depth_50bps * simple_multipliers['50bps'] * simple_vol_adj +
            depth_100bps * simple_multipliers['100bps'] * simple_vol_adj + 
            depth_200bps * simple_multipliers['200bps'] * simple_vol_adj
        )
        simple_total = depth_50bps + depth_100bps + depth_200bps
        simple_efficiency = simple_effective / simple_total if simple_total > 0 else 0
        
        # Advanced method
        advanced_result = self.calculate_effective_depth_advanced(
            depth_50bps, depth_100bps, depth_200bps, bid_ask_spread, volatility
        )
        
        return {
            'simple_method': {
                'effective_depth': simple_effective,
                'efficiency_ratio': simple_efficiency,
                'methodology': 'Tier Multipliers + Vol Adjustment'
            },
            'advanced_method': {
                'effective_depth': advanced_result['total_effective_depth'],
                'efficiency_ratio': advanced_result['efficiency_ratio'],
                'methodology': 'Market Microstructure Integration'
            },
            'improvement': {
                'value_difference': advanced_result['total_effective_depth'] - simple_effective,
                'efficiency_improvement': advanced_result['efficiency_ratio'] - simple_efficiency,
                'relative_change': ((advanced_result['total_effective_depth'] - simple_effective) / simple_effective * 100) if simple_effective > 0 else 0
            },
            'tier_breakdown': advanced_result['tier_details']
        }

def test_advanced_depth_calculation():
    """Test the advanced depth calculation"""
    calculator = AdvancedDepthCalculator()
    
    # Test scenarios
    scenarios = [
        {
            'name': 'Low Vol Scenario',
            'depth_50bps': 100000, 'depth_100bps': 200000, 'depth_200bps': 300000,
            'bid_ask_spread': 10, 'volatility': 0.15
        },
        {
            'name': 'High Vol Scenario', 
            'depth_50bps': 100000, 'depth_100bps': 200000, 'depth_200bps': 300000,
            'bid_ask_spread': 25, 'volatility': 0.45
        },
        {
            'name': 'Thin Market',
            'depth_50bps': 25000, 'depth_100bps': 50000, 'depth_200bps': 75000,
            'bid_ask_spread': 50, 'volatility': 0.60
        }
    ]
    
    print("=== ADVANCED DEPTH CALCULATION TEST ===\n")
    
    for scenario in scenarios:
        print(f"-- {scenario['name']} --")
        print(f"   Raw Depths: 50bps=${scenario['depth_50bps']:,}, 100bps=${scenario['depth_100bps']:,}, 200bps=${scenario['depth_200bps']:,}")
        print(f"   Spread: {scenario['bid_ask_spread']}bps, Vol: {scenario['volatility']:.1%}")
        
        # Extract only the relevant parameters
        params = {k: v for k, v in scenario.items() if k != 'name'}
        comparison = calculator.compare_methodologies(**params)
        
        simple = comparison['simple_method']
        advanced = comparison['advanced_method'] 
        improvement = comparison['improvement']
        
        print(f"\n   Simple Method:   ${simple['effective_depth']:,.0f} ({simple['efficiency_ratio']:.1%} efficient)")
        print(f"   Advanced Method: ${advanced['effective_depth']:,.0f} ({advanced['efficiency_ratio']:.1%} efficient)")
        print(f"   Improvement:     {improvement['relative_change']:+.1f}% ({improvement['value_difference']:+,.0f})")
        
        # Show tier breakdown
        print(f"\n   Tier Breakdown (Advanced):")
        for tier, details in comparison['tier_breakdown'].items():
            print(f"     {tier}: ${details['effective_depth']:,.0f} ({details['efficiency']:.1%}) "
                  f"[Fill:{details['fill_probability']:.2f}, Impact:{details['market_impact']:.2f}, "
                  f"Quality:{details['quality_factor']:.2f}, Resilience:{details['resilience_factor']:.2f}]")
        
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    test_advanced_depth_calculation()
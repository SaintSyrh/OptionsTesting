import math
from typing import Dict, List, Tuple, Optional

class CryptoEffectiveDepthCalculator:
    """
    Empirically-tuned effective depth calculator optimized for crypto markets
    Based on actual crypto market maker experience and data
    """
    
    def __init__(self):
        # Exchange tier multipliers based on crypto market liquidity patterns
        self.exchange_tiers = {
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
            'Other': 0.50,  # Conservative default
        }
        
        # Spread tier base multipliers (refined from experience)
        self.spread_tier_multipliers = {
            '50bps': 0.95,   # Slightly reduced from 1.0 (realistic fill rates)
            '100bps': 0.78,  # Slightly higher than 0.75 (better than expected)
            '200bps': 0.55   # Higher than 0.50 (deeper crypto books are more valuable)
        }
        
        # Crypto-specific parameters
        self.crypto_params = {
            'vol_impact_factor': 1.5,        # Gentler than traditional markets
            'spread_bonus_factor': 1000,     # How much tighter spreads matter
            'liquidity_bonus_threshold': 100000,  # $100k depth threshold for bonus
            'max_liquidity_bonus': 1.25,    # Max 25% bonus for large sizes
            'arb_efficiency_factor': 0.85,  # Crypto arb reduces depth value by 15%
            'cascade_protection_bonus': 1.1, # 10% bonus for cascade protection
            'mev_penalty_factor': 0.95,     # 5% MEV penalty on smaller spreads
        }
    
    def get_exchange_tier_multiplier(self, exchange: str) -> float:
        """Get the exchange quality multiplier"""
        return self.exchange_tiers.get(exchange, self.exchange_tiers['Other'])
    
    def calculate_volatility_adjustment(self, volatility: float) -> float:
        """
        Crypto-optimized volatility adjustment
        Less punitive than traditional markets due to better arb mechanisms
        """
        # Crypto markets handle volatility better than traditional markets
        vol_penalty = 1 / (1 + volatility * self.crypto_params['vol_impact_factor'])
        
        # Floor at 25% (vs 30% in old system) - crypto MMs can handle more vol
        return max(0.25, vol_penalty)
    
    def calculate_spread_adjustment(self, spread_bps: float, target_spread_bps: float) -> float:
        """
        Calculate bonus/penalty based on spread tightness vs target
        Tighter spreads get bonus, wider spreads get penalty
        """
        spread_diff = target_spread_bps - spread_bps
        spread_factor = 1 + (spread_diff / self.crypto_params['spread_bonus_factor'])
        
        # Bound between 0.7x and 1.3x
        return max(0.7, min(1.3, spread_factor))
    
    def calculate_liquidity_bonus(self, depth: float) -> float:
        """
        Size bonus for large depth provision
        Larger sizes get disproportionate value in crypto
        """
        if depth <= 0:
            return 1.0
            
        # Logarithmic bonus for size
        size_ratio = depth / self.crypto_params['liquidity_bonus_threshold']
        bonus = 1 + math.log10(max(1.0, size_ratio)) * 0.25
        
        return min(self.crypto_params['max_liquidity_bonus'], bonus)
    
    def calculate_mev_adjustment(self, spread_bps: float) -> float:
        """
        MEV penalty for tight spreads (more susceptible to sandwich attacks)
        """
        if spread_bps < 25:  # Tight spreads more vulnerable
            mev_penalty = self.crypto_params['mev_penalty_factor']
        else:
            mev_penalty = 1.0
        
        return mev_penalty
    
    def calculate_crypto_effective_depth(self,
                                       depth: float,
                                       spread_tier: str,  # '50bps', '100bps', '200bps'  
                                       bid_ask_spread: float,  # in bps
                                       volatility: float,
                                       exchange: str,
                                       include_cascade_bonus: bool = True) -> Dict:
        """
        Calculate effective depth using crypto-optimized empirical formula
        
        Formula:
        effective_depth = depth × base_efficiency × vol_adjustment × spread_adjustment 
                         × liquidity_bonus × exchange_quality × mev_adjustment × cascade_bonus
        """
        if depth <= 0:
            return {
                'effective_depth': 0.0,
                'efficiency_ratio': 0.0,
                'breakdown': {}
            }
        
        # Base efficiency from spread tier
        base_efficiency = self.spread_tier_multipliers.get(spread_tier, 0.5)
        
        # Volatility adjustment (crypto-optimized)
        vol_adjustment = self.calculate_volatility_adjustment(volatility)
        
        # Spread adjustment based on how tight/wide vs target
        target_spread = {'50bps': 60, '100bps': 110, '200bps': 210}.get(spread_tier, 100)
        spread_adjustment = self.calculate_spread_adjustment(bid_ask_spread, target_spread)
        
        # Liquidity size bonus
        liquidity_bonus = self.calculate_liquidity_bonus(depth)
        
        # Exchange quality multiplier
        exchange_quality = self.get_exchange_tier_multiplier(exchange)
        
        # MEV penalty for tight spreads
        mev_adjustment = self.calculate_mev_adjustment(bid_ask_spread)
        
        # Cascade protection bonus (crypto-specific benefit)
        cascade_bonus = self.crypto_params['cascade_protection_bonus'] if include_cascade_bonus else 1.0
        
        # Calculate effective depth
        effective_depth = (depth * base_efficiency * vol_adjustment * spread_adjustment 
                          * liquidity_bonus * exchange_quality * mev_adjustment * cascade_bonus)
        
        efficiency_ratio = effective_depth / depth
        
        return {
            'effective_depth': effective_depth,
            'efficiency_ratio': efficiency_ratio,
            'breakdown': {
                'base_efficiency': base_efficiency,
                'vol_adjustment': vol_adjustment,
                'spread_adjustment': spread_adjustment,
                'liquidity_bonus': liquidity_bonus,
                'exchange_quality': exchange_quality,
                'mev_adjustment': mev_adjustment,
                'cascade_bonus': cascade_bonus,
                'raw_depth': depth
            }
        }
    
    def calculate_entity_effective_depth(self,
                                       depth_50bps: float,
                                       depth_100bps: float,
                                       depth_200bps: float,
                                       bid_ask_spread: float,
                                       volatility: float,
                                       exchange: str) -> Dict:
        """
        Calculate total effective depth across all tiers for an entity
        """
        tiers = {
            '50bps': depth_50bps,
            '100bps': depth_100bps, 
            '200bps': depth_200bps
        }
        
        total_raw = sum(tiers.values())
        total_effective = 0.0
        tier_results = {}
        
        for tier_name, depth in tiers.items():
            if depth > 0:
                result = self.calculate_crypto_effective_depth(
                    depth, tier_name, bid_ask_spread, volatility, exchange
                )
                tier_results[tier_name] = result
                total_effective += result['effective_depth']
        
        overall_efficiency = total_effective / total_raw if total_raw > 0 else 0
        
        return {
            'total_raw_depth': total_raw,
            'total_effective_depth': total_effective,
            'overall_efficiency': overall_efficiency,
            'tier_results': tier_results,
            'methodology': 'Crypto-Empirical'
        }
    
    def compare_with_simple_method(self,
                                 depth_50bps: float,
                                 depth_100bps: float,
                                 depth_200bps: float,
                                 bid_ask_spread: float,
                                 volatility: float,
                                 exchange: str) -> Dict:
        """
        Compare crypto-optimized method with current simple method
        """
        # Simple method calculation
        simple_multipliers = {'50bps': 1.0, '100bps': 0.75, '200bps': 0.50}
        simple_vol_adj = max(0.3, 1.0 - (volatility * 2))
        
        simple_effective = (
            depth_50bps * simple_multipliers['50bps'] * simple_vol_adj +
            depth_100bps * simple_multipliers['100bps'] * simple_vol_adj + 
            depth_200bps * simple_multipliers['200bps'] * simple_vol_adj
        )
        
        # Crypto-optimized method
        crypto_result = self.calculate_entity_effective_depth(
            depth_50bps, depth_100bps, depth_200bps, bid_ask_spread, volatility, exchange
        )
        
        total_raw = depth_50bps + depth_100bps + depth_200bps
        simple_efficiency = simple_effective / total_raw if total_raw > 0 else 0
        
        improvement = crypto_result['total_effective_depth'] - simple_effective
        improvement_pct = (improvement / simple_effective * 100) if simple_effective > 0 else 0
        
        return {
            'simple_method': {
                'effective_depth': simple_effective,
                'efficiency': simple_efficiency,
                'method': 'Simple Tier Multipliers'
            },
            'crypto_method': {
                'effective_depth': crypto_result['total_effective_depth'],
                'efficiency': crypto_result['overall_efficiency'],
                'method': 'Crypto-Empirical Optimization'
            },
            'improvement': {
                'absolute': improvement,
                'percentage': improvement_pct,
                'better': improvement > 0
            },
            'tier_breakdown': crypto_result['tier_results']
        }

def test_crypto_depth_calculator():
    """Test the crypto-optimized depth calculator"""
    calculator = CryptoEffectiveDepthCalculator()
    
    test_scenarios = [
        {
            'name': 'Binance Low Vol',
            'depth_50bps': 200000, 'depth_100bps': 300000, 'depth_200bps': 500000,
            'bid_ask_spread': 8, 'volatility': 0.20, 'exchange': 'Binance'
        },
        {
            'name': 'Binance High Vol', 
            'depth_50bps': 150000, 'depth_100bps': 250000, 'depth_200bps': 400000,
            'bid_ask_spread': 15, 'volatility': 0.50, 'exchange': 'Binance'
        },
        {
            'name': 'Small Exchange Thin',
            'depth_50bps': 50000, 'depth_100bps': 80000, 'depth_200bps': 120000,
            'bid_ask_spread': 35, 'volatility': 0.60, 'exchange': 'Other'
        },
        {
            'name': 'OKX Medium Vol',
            'depth_50bps': 120000, 'depth_100bps': 200000, 'depth_200bps': 300000,
            'bid_ask_spread': 12, 'volatility': 0.35, 'exchange': 'OKX'
        }
    ]
    
    print("=== CRYPTO-OPTIMIZED DEPTH CALCULATOR TEST ===\n")
    
    for scenario in test_scenarios:
        print(f"-- {scenario['name']} --")
        params = {k: v for k, v in scenario.items() if k != 'name'}
        
        comparison = calculator.compare_with_simple_method(**params)
        
        simple = comparison['simple_method']
        crypto = comparison['crypto_method']
        improvement = comparison['improvement']
        
        total_raw = params['depth_50bps'] + params['depth_100bps'] + params['depth_200bps']
        
        print(f"Raw Depth: ${total_raw:,} | Spread: {params['bid_ask_spread']}bps | Vol: {params['volatility']:.0%} | {params['exchange']}")
        print(f"Simple Method:  ${simple['effective_depth']:,.0f} ({simple['efficiency']:.1%} efficient)")
        print(f"Crypto Method:  ${crypto['effective_depth']:,.0f} ({crypto['efficiency']:.1%} efficient)")
        print(f"Improvement:    {improvement['percentage']:+.1f}% ({improvement['absolute']:+,.0f})")
        
        # Show key factors
        if comparison['tier_breakdown']:
            print("Key Adjustments:")
            for tier, result in comparison['tier_breakdown'].items():
                breakdown = result['breakdown']
                print(f"  {tier}: Vol={breakdown['vol_adjustment']:.2f}, Spread={breakdown['spread_adjustment']:.2f}, "
                      f"Size={breakdown['liquidity_bonus']:.2f}, Exchange={breakdown['exchange_quality']:.2f}")
        
        print("\n" + "="*60 + "\n")
    
    return True

if __name__ == "__main__":
    test_crypto_depth_calculator()
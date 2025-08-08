import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import math

class DepthValuationModels:
    """
    Market maker depth valuation models based on various academic frameworks
    """
    
    def __init__(self):
        # Model parameters (can be calibrated based on market data)
        self.default_params = {
            'alpha': 0.1,           # Market impact coefficient (Almgren-Chriss)
            'lambda_0': 0.001,      # Base Kyle's lambda
            'delta': 0.6,           # Bouchaud power law exponent
            'Y': 1.0,               # Bouchaud coefficient
            'rho': 0.5,             # Order book resilience rate
            'beta_hawkes': 2.0,     # Hawkes process decay
            'mu_hawkes': 0.1,       # Hawkes base intensity
            'rho_recovery': 0.3,    # Recovery rate parameter (resilience model)
            'pin_alpha': 0.2,       # Informed trader arrival rate (PIN model)
            'pin_mu': 0.1,          # Information event rate (PIN model)
            'epsilon_buy': 0.3,     # Uninformed buy rate (PIN model)
            'epsilon_sell': 0.3,    # Uninformed sell rate (PIN model)
            'arb_beta': 0.5,        # Cross-venue arbitrage efficiency
        }
    
    def almgren_chriss_value(self, 
                           spread_0: float, 
                           spread_1: float,
                           volatility: float,
                           trade_sizes: List[float],
                           probabilities: List[float],
                           volume_0: float,
                           volume_mm: float,
                           alpha: Optional[float] = None) -> Dict:
        """
        Almgren-Chriss adapted model for market maker value
        
        Value_MM = Σᵢ Qᵢ * P(Qᵢ) * [(Spread₀ - Spread₁) + α * σ * (√(Qᵢ/V₀) - √(Qᵢ/(V₀ + V_MM)))]
        """
        if alpha is None:
            alpha = self.default_params['alpha']
            
        total_value = 0.0
        breakdown = []
        
        for i, (Q, P_Q) in enumerate(zip(trade_sizes, probabilities)):
            if Q <= 0 or P_Q <= 0:
                continue
                
            # Spread improvement component
            spread_component = spread_0 - spread_1
            
            # Market impact reduction component
            impact_0 = alpha * volatility * math.sqrt(Q / volume_0) if volume_0 > 0 else 0
            impact_1 = alpha * volatility * math.sqrt(Q / (volume_0 + volume_mm)) if (volume_0 + volume_mm) > 0 else 0
            impact_component = impact_0 - impact_1
            
            # Total value for this trade size
            trade_value = Q * P_Q * (spread_component + impact_component)
            total_value += trade_value
            
            breakdown.append({
                'trade_size': Q,
                'probability': P_Q,
                'spread_savings': Q * P_Q * spread_component,
                'impact_reduction': Q * P_Q * impact_component,
                'total_contribution': trade_value
            })
        
        return {
            'total_value': total_value,
            'model': 'Almgren-Chriss',
            'breakdown': breakdown,
            'parameters': {
                'alpha': alpha,
                'spread_0': spread_0,
                'spread_1': spread_1,
                'volatility': volatility,
                'volume_0': volume_0,
                'volume_mm': volume_mm
            }
        }
    
    def kyle_lambda_value(self,
                         trade_sizes: List[float],
                         probabilities: List[float],
                         depth_0: float,
                         depth_mm: float) -> Dict:
        """
        Kyle's Lambda model: ΔP = λ * Q, where λ = 1/(2*Depth)
        Value_MM = Σᵢ Qᵢ * P(Qᵢ) * (λ₀ - λ₁) * Qᵢ
        """
        lambda_0 = 1 / (2 * depth_0) if depth_0 > 0 else float('inf')
        lambda_1 = 1 / (2 * (depth_0 + depth_mm)) if (depth_0 + depth_mm) > 0 else float('inf')
        
        total_value = 0.0
        breakdown = []
        
        for Q, P_Q in zip(trade_sizes, probabilities):
            if Q <= 0 or P_Q <= 0:
                continue
                
            # Linear impact difference
            impact_reduction = (lambda_0 - lambda_1) * Q * Q
            trade_value = P_Q * impact_reduction
            total_value += trade_value
            
            breakdown.append({
                'trade_size': Q,
                'probability': P_Q,
                'lambda_0': lambda_0,
                'lambda_1': lambda_1,
                'impact_reduction': impact_reduction,
                'total_contribution': trade_value
            })
        
        return {
            'total_value': total_value,
            'model': 'Kyle Lambda',
            'breakdown': breakdown,
            'parameters': {
                'depth_0': depth_0,
                'depth_mm': depth_mm,
                'lambda_0': lambda_0,
                'lambda_1': lambda_1
            }
        }
    
    def bouchaud_power_law_value(self,
                                volatility: float,
                                trade_sizes: List[float],
                                probabilities: List[float],
                                volume_daily_0: float,
                                volume_daily_mm: float,
                                delta: Optional[float] = None,
                                Y: Optional[float] = None) -> Dict:
        """
        Bouchaud Power Law model: ΔP = Y * σ * (Q/V_daily)^δ
        Value_MM = Σᵢ Qᵢ * P(Qᵢ) * Y * σ * [Qᵢ^δ * (1/V₀^δ - 1/(V₀+V_MM)^δ)]
        """
        if delta is None:
            delta = self.default_params['delta']
        if Y is None:
            Y = self.default_params['Y']
            
        total_value = 0.0
        breakdown = []
        
        for Q, P_Q in zip(trade_sizes, probabilities):
            if Q <= 0 or P_Q <= 0 or volume_daily_0 <= 0:
                continue
                
            # Power law impact components
            impact_0 = Y * volatility * (Q / volume_daily_0) ** delta
            impact_1 = Y * volatility * (Q / (volume_daily_0 + volume_daily_mm)) ** delta if (volume_daily_0 + volume_daily_mm) > 0 else impact_0
            
            impact_reduction = impact_0 - impact_1
            trade_value = Q * P_Q * impact_reduction
            total_value += trade_value
            
            breakdown.append({
                'trade_size': Q,
                'probability': P_Q,
                'impact_0': impact_0,
                'impact_1': impact_1,
                'impact_reduction': impact_reduction,
                'total_contribution': trade_value
            })
        
        return {
            'total_value': total_value,
            'model': 'Bouchaud Power Law',
            'breakdown': breakdown,
            'parameters': {
                'Y': Y,
                'delta': delta,
                'volatility': volatility,
                'volume_daily_0': volume_daily_0,
                'volume_daily_mm': volume_daily_mm
            }
        }
    
    def amihud_illiquidity_value(self,
                               daily_volume_0: float,
                               daily_volume_mm: float,
                               asset_price: float,
                               avg_return: float) -> Dict:
        """
        Amihud Illiquidity Ratio model
        ILLIQ = |Return| / Volume
        Value_MM = Daily_Volume * (ILLIQ₀ - ILLIQ₁) * Asset_Price
        """
        illiq_0 = abs(avg_return) / daily_volume_0 if daily_volume_0 > 0 else float('inf')
        illiq_1 = abs(avg_return) / (daily_volume_0 + daily_volume_mm) if (daily_volume_0 + daily_volume_mm) > 0 else illiq_0
        
        illiq_reduction = illiq_0 - illiq_1
        total_value = (daily_volume_0 + daily_volume_mm) * illiq_reduction * asset_price
        
        return {
            'total_value': total_value,
            'model': 'Amihud Illiquidity',
            'breakdown': [{
                'illiq_0': illiq_0,
                'illiq_1': illiq_1,
                'illiq_reduction': illiq_reduction,
                'daily_volume_total': daily_volume_0 + daily_volume_mm,
                'asset_price': asset_price
            }],
            'parameters': {
                'daily_volume_0': daily_volume_0,
                'daily_volume_mm': daily_volume_mm,
                'asset_price': asset_price,
                'avg_return': avg_return
            }
        }
    
    def hawkes_cascade_value(self,
                           spread_0: float,
                           spread_1: float,
                           volatility: float,
                           volume_mm: float,
                           daily_volume_0: float,
                           asset_price: float,
                           beta: Optional[float] = None,
                           mu: Optional[float] = None,
                           time_horizon: float = 1.0) -> Dict:
        """
        Enhanced Hawkes Process/Cascade Model with Liquidation Dynamics
        λ(t) = μ + Σᵢ α*e^(-β*(t-tᵢ))
        P(cascade) = 1 - e^(-intensity*volume_spike)
        
        Unique to crypto: Captures liquidation cascades, momentum trading, 
        and social-media driven spikes that don't exist in traditional markets
        """
        if beta is None:
            beta = self.default_params['beta_hawkes']
        if mu is None:
            mu = self.default_params['mu_hawkes']
        
        # Market maker reduces clustering intensity by providing depth
        # Higher MM volume reduces the tendency for cascading aggressive orders
        clustering_reduction_factor = volume_mm / (daily_volume_0 + volume_mm) if (daily_volume_0 + volume_mm) > 0 else 0
        
        # Base intensity (aggressive order arrival rate)
        base_intensity = mu * volatility  # Higher volatility = more aggressive orders
        
        # Liquidation cascade probability
        # P(cascade) = 1 - e^(-intensity * volume_spike)
        volume_spike_factor = volatility * 2.0  # High volatility creates volume spikes
        cascade_probability_0 = 1 - math.exp(-base_intensity * volume_spike_factor)
        cascade_probability_1 = 1 - math.exp(-base_intensity * volume_spike_factor * (1 - clustering_reduction_factor))
        
        # Clustering component - MM reduces this by providing depth
        clustering_intensity_0 = base_intensity * (1 + volatility)  # More clustering in volatile markets
        clustering_intensity_1 = clustering_intensity_0 * (1 - clustering_reduction_factor)
        
        # Value from preventing liquidation cascades
        liquidation_protection = (cascade_probability_0 - cascade_probability_1) * asset_price * daily_volume_0 * 0.01 * 0.001
        
        # Traditional momentum/clustering value
        spread_savings = spread_0 - spread_1
        intensity_reduction = clustering_intensity_0 - clustering_intensity_1
        cascade_value = intensity_reduction * spread_savings * daily_volume_0 * time_horizon * 0.01
        
        # Social media momentum dampening (crypto-specific)
        social_momentum_factor = volatility * clustering_reduction_factor
        social_dampening = social_momentum_factor * daily_volume_0 * 0.05 * 0.001
        
        total_value = cascade_value + liquidation_protection + social_dampening
        
        return {
            'total_value': total_value,
            'model': 'Hawkes Cascade/Liquidation',
            'breakdown': [{
                'base_intensity': base_intensity,
                'clustering_intensity_0': clustering_intensity_0,
                'clustering_intensity_1': clustering_intensity_1,
                'intensity_reduction': intensity_reduction,
                'cascade_value': cascade_value,
                'liquidation_protection': liquidation_protection,
                'social_dampening': social_dampening,
                'clustering_reduction_factor': clustering_reduction_factor,
                'cascade_probability_0': cascade_probability_0,
                'cascade_probability_1': cascade_probability_1,
                'volume_spike_factor': volume_spike_factor
            }],
            'parameters': {
                'beta': beta,
                'mu': mu,
                'spread_0': spread_0,
                'spread_1': spread_1,
                'volatility': volatility,
                'volume_mm': volume_mm,
                'daily_volume_0': daily_volume_0,
                'time_horizon': time_horizon
            }
        }
    
    def order_book_resilience_value(self,
                                   spread_0: float,
                                   spread_1: float,
                                   depth_0: float,
                                   depth_mm: float,
                                   daily_volume: float,
                                   asset_price: float,
                                   rho: Optional[float] = None,
                                   time_horizon: float = 24.0) -> Dict:
        """
        Order Book Resilience/Recovery Model
        Impact(t) = ΔP_immediate * e^(-ρ*t) + ΔP_permanent
        Value_MM = ∫ Volume(t) * (ρ_with_MM - ρ_without) * ΔP(t) dt
        
        Critical for crypto: Captures temporal recovery dynamics - some crypto markets
        recover instantly (arbitrage bots), others never recover (thin altcoins)
        """
        if rho is None:
            rho = self.default_params['rho_recovery']
        
        # Recovery rates with and without MM
        rho_without = rho * (depth_0 / (depth_0 + 100000)) if depth_0 > 0 else 0.01  # Slower recovery without depth
        rho_with = rho * ((depth_0 + depth_mm) / (depth_0 + depth_mm + 100000))  # Faster with MM depth
        
        # Immediate impact
        immediate_impact_0 = spread_0
        immediate_impact_1 = spread_1
        
        # Permanent impact (reduced with better liquidity)
        permanent_impact_reduction = (immediate_impact_0 - immediate_impact_1) * 0.3  # 30% becomes permanent
        
        # Value from faster recovery (integral approximation)
        # ∫₀ᵀ Volume * (ρ_with - ρ_without) * ΔP * e^(-ρt) dt
        recovery_improvement = (rho_with - rho_without) * immediate_impact_0
        
        # Integral: ∫₀ᵀ e^(-ρt) dt = (1 - e^(-ρT))/ρ for exponential decay
        avg_recovery_rate = (rho_with + rho_without) / 2
        integral_factor = (1 - math.exp(-avg_recovery_rate * time_horizon)) / avg_recovery_rate if avg_recovery_rate > 0 else time_horizon
        
        # Total value: faster recovery + permanent impact reduction
        recovery_value = daily_volume * 0.1 * recovery_improvement * integral_factor * 0.001  # Scale appropriately
        permanent_value = daily_volume * 0.2 * permanent_impact_reduction * asset_price * 0.0001  # Scale for permanent component
        
        total_value = recovery_value + permanent_value
        
        return {
            'total_value': total_value,
            'model': 'Order Book Resilience',
            'breakdown': [{
                'rho_without': rho_without,
                'rho_with': rho_with,
                'recovery_improvement': recovery_improvement,
                'recovery_value': recovery_value,
                'permanent_value': permanent_value,
                'integral_factor': integral_factor,
                'immediate_impact_0': immediate_impact_0,
                'immediate_impact_1': immediate_impact_1
            }],
            'parameters': {
                'rho': rho,
                'spread_0': spread_0,
                'spread_1': spread_1,
                'depth_0': depth_0,
                'depth_mm': depth_mm,
                'daily_volume': daily_volume,
                'time_horizon': time_horizon
            }
        }
    
    def adverse_selection_pin_value(self,
                                   spread_0: float,
                                   spread_1: float,
                                   daily_volume: float,
                                   trade_sizes: List[float],
                                   probabilities: List[float],
                                   alpha: Optional[float] = None,
                                   mu: Optional[float] = None,
                                   epsilon_buy: Optional[float] = None,
                                   epsilon_sell: Optional[float] = None) -> Dict:
        """
        Adverse Selection/PIN (Probability of Informed Trading) Model
        PIN = (α*μ)/(α*μ + ε_buy + ε_sell)
        Spread_optimal = f(PIN) + inventory_cost
        Value_MM = Volume * (Loss_avoided_toxic - Profit_lost_benign)
        
        Crypto necessity: With MEV, insider trading, and wallet tracking,
        knowing flow toxicity is essential for optimal pricing
        """
        if alpha is None:
            alpha = self.default_params['pin_alpha']
        if mu is None:
            mu = self.default_params['pin_mu']
        if epsilon_buy is None:
            epsilon_buy = self.default_params['epsilon_buy']
        if epsilon_sell is None:
            epsilon_sell = self.default_params['epsilon_sell']
        
        # Calculate PIN (Probability of Informed Trading)
        informed_rate = alpha * mu
        uninformed_rate = epsilon_buy + epsilon_sell
        pin = informed_rate / (informed_rate + uninformed_rate) if (informed_rate + uninformed_rate) > 0 else 0
        
        # Optimal spread adjustment for toxicity
        # Higher PIN requires wider spreads to compensate for adverse selection
        toxic_spread_premium = pin * spread_0 * 2.0  # Toxic trades need wider spreads
        benign_spread_discount = (1 - pin) * spread_0 * 0.5  # Benign trades can have tighter spreads
        
        # Market maker value from better flow discrimination
        total_value = 0.0
        breakdown = []
        
        for Q, P_Q in zip(trade_sizes, probabilities):
            if Q <= 0 or P_Q <= 0:
                continue
            
            # Value from avoiding toxic flow losses
            toxic_loss_avoided = Q * P_Q * pin * toxic_spread_premium
            
            # Value lost from wider spreads on benign flow (opportunity cost)
            benign_profit_lost = Q * P_Q * (1 - pin) * benign_spread_discount * 0.3  # 30% loss rate
            
            net_value = toxic_loss_avoided - benign_profit_lost
            total_value += net_value
            
            breakdown.append({
                'trade_size': Q,
                'probability': P_Q,
                'pin': pin,
                'toxic_loss_avoided': toxic_loss_avoided,
                'benign_profit_lost': benign_profit_lost,
                'net_value': net_value
            })
        
        # Scale by daily volume
        total_value *= daily_volume * 0.00001  # Scale appropriately
        
        return {
            'total_value': total_value,
            'model': 'Adverse Selection/PIN',
            'breakdown': breakdown,
            'parameters': {
                'pin': pin,
                'alpha': alpha,
                'mu': mu,
                'epsilon_buy': epsilon_buy,
                'epsilon_sell': epsilon_sell,
                'informed_rate': informed_rate,
                'uninformed_rate': uninformed_rate,
                'toxic_spread_premium': toxic_spread_premium,
                'benign_spread_discount': benign_spread_discount
            }
        }
    
    def cross_venue_arbitrage_value(self,
                                   depth_local: float,
                                   depth_other_venues: List[float],
                                   spread_0: float,
                                   spread_1: float,
                                   daily_volume: float,
                                   asset_price: float,
                                   beta: Optional[float] = None) -> Dict:
        """
        Cross-Venue Arbitrage Model
        Impact_effective = Impact_local * (1 - Σ β_i * Depth_venue_i/Depth_total)
        Arb_pressure = max(0, Price_diff - Fee - Gas)
        
        Crypto-specific: Crypto MMs must consider Binance/Coinbase/Uniswap simultaneously
        """
        if beta is None:
            beta = self.default_params['arb_beta']
        
        # Total depth across venues
        total_depth = depth_local + sum(depth_other_venues)
        
        # Arbitrage efficiency factor
        if total_depth > 0:
            other_venue_factor = sum(depth_other_venues) / total_depth
            arb_efficiency = beta * other_venue_factor
        else:
            arb_efficiency = 0
        
        # Effective impact reduction due to arbitrage
        impact_0 = spread_0
        impact_1 = spread_1
        
        # Cross-venue arbitrage reduces local impact
        effective_impact_0 = impact_0 * (1 - arb_efficiency * 0.5)  # 50% max reduction
        effective_impact_1 = impact_1 * (1 - arb_efficiency * 0.7)  # More reduction with MM
        
        # Value from arbitrage pressure mitigation
        arbitrage_value = (effective_impact_0 - effective_impact_1) * daily_volume * asset_price * 0.0001
        
        # Additional value from price discovery improvement
        discovery_value = arb_efficiency * daily_volume * 0.1 * (spread_0 - spread_1) * 0.001
        
        total_value = arbitrage_value + discovery_value
        
        return {
            'total_value': total_value,
            'model': 'Cross-Venue Arbitrage',
            'breakdown': [{
                'depth_local': depth_local,
                'depth_other_venues': depth_other_venues,
                'total_depth': total_depth,
                'other_venue_factor': other_venue_factor,
                'arb_efficiency': arb_efficiency,
                'effective_impact_0': effective_impact_0,
                'effective_impact_1': effective_impact_1,
                'arbitrage_value': arbitrage_value,
                'discovery_value': discovery_value
            }],
            'parameters': {
                'beta': beta,
                'spread_0': spread_0,
                'spread_1': spread_1,
                'daily_volume': daily_volume,
                'asset_price': asset_price
            }
        }
    
    def composite_valuation(self,
                          spread_0: float,
                          spread_1: float,
                          volatility: float,
                          trade_sizes: List[float],
                          probabilities: List[float],
                          volume_0: float,
                          volume_mm: float,
                          depth_0: float,
                          depth_mm: float,
                          daily_volume_0: float,
                          daily_volume_mm: float,
                          asset_price: float,
                          avg_return: float = 0.001,
                          weights: Optional[Dict[str, float]] = None,
                          use_crypto_weights: bool = True) -> Dict:
        """
        Composite valuation using weighted combination of multiple models
        Now optimized for crypto markets with enhanced Bouchaud and Hawkes components
        """
        if weights is None:
            if use_crypto_weights:
                # Comprehensive crypto-optimized weights with new critical models
                weights = {
                    # Original models (adjusted down)
                    'almgren_chriss': 0.25,        # Reduced from 35%
                    'kyle_lambda': 0.20,           # Reduced from 25%
                    'bouchaud_power': 0.15,        # Reduced from 30%
                    'amihud': 0.05,               # Kept as sanity check
                    
                    # New critical crypto models
                    'resilience': 0.15,            # Temporal recovery dynamics
                    'adverse_selection': 0.10,     # Flow toxicity filtering
                    'cross_venue': 0.05,          # Arbitrage effects
                    'hawkes_cascade': 0.05         # Liquidation/momentum cascades
                }
            else:
                # Traditional weights (for comparison)
                weights = {
                    'almgren_chriss': 0.4,
                    'kyle_lambda': 0.3,
                    'bouchaud_power': 0.2,
                    'amihud': 0.1,
                    'resilience': 0.0,
                    'adverse_selection': 0.0,
                    'cross_venue': 0.0,
                    'hawkes_cascade': 0.0
                }
        
        # Calculate individual model values
        models_results = {}
        
        # Almgren-Chriss
        models_results['almgren_chriss'] = self.almgren_chriss_value(
            spread_0, spread_1, volatility, trade_sizes, probabilities, 
            volume_0, volume_mm
        )
        
        # Kyle's Lambda
        models_results['kyle_lambda'] = self.kyle_lambda_value(
            trade_sizes, probabilities, depth_0, depth_mm
        )
        
        # Bouchaud Power Law
        models_results['bouchaud_power'] = self.bouchaud_power_law_value(
            volatility, trade_sizes, probabilities, daily_volume_0, daily_volume_mm
        )
        
        # Amihud Illiquidity
        models_results['amihud'] = self.amihud_illiquidity_value(
            daily_volume_0, daily_volume_mm, asset_price, avg_return
        )
        
        # Order Book Resilience (only if weight > 0)
        if weights.get('resilience', 0) > 0:
            models_results['resilience'] = self.order_book_resilience_value(
                spread_0, spread_1, depth_0, depth_mm, daily_volume_0, asset_price
            )
        else:
            models_results['resilience'] = {'total_value': 0.0, 'model': 'Resilience (disabled)'}
        
        # Adverse Selection/PIN (only if weight > 0)
        if weights.get('adverse_selection', 0) > 0:
            models_results['adverse_selection'] = self.adverse_selection_pin_value(
                spread_0, spread_1, daily_volume_0, trade_sizes, probabilities
            )
        else:
            models_results['adverse_selection'] = {'total_value': 0.0, 'model': 'Adverse Selection (disabled)'}
        
        # Cross-Venue Arbitrage (only if weight > 0)
        if weights.get('cross_venue', 0) > 0:
            # Assume some other venues for demo (could be made configurable)
            other_venues_depth = [depth_0 * 0.8, depth_0 * 0.6, depth_0 * 0.4]  # Simulated other venues
            models_results['cross_venue'] = self.cross_venue_arbitrage_value(
                depth_0 + depth_mm, other_venues_depth, spread_0, spread_1, daily_volume_0, asset_price
            )
        else:
            models_results['cross_venue'] = {'total_value': 0.0, 'model': 'Cross-Venue (disabled)'}
        
        # Hawkes Cascade (only if weight > 0)
        if weights.get('hawkes_cascade', 0) > 0:
            models_results['hawkes_cascade'] = self.hawkes_cascade_value(
                spread_0, spread_1, volatility, volume_mm, daily_volume_0, asset_price
            )
        else:
            models_results['hawkes_cascade'] = {'total_value': 0.0, 'model': 'Hawkes Cascade (disabled)'}
        
        # Legacy Hawkes Momentum (for backwards compatibility)
        if weights.get('hawkes_momentum', 0) > 0:
            models_results['hawkes_momentum'] = models_results.get('hawkes_cascade', {'total_value': 0.0, 'model': 'Legacy Hawkes'})
        else:
            models_results['hawkes_momentum'] = {'total_value': 0.0, 'model': 'Legacy Hawkes (disabled)'}
        
        # Calculate weighted composite value
        total_weighted_value = 0.0
        for model_name, result in models_results.items():
            weight = weights.get(model_name, 0.0)
            total_weighted_value += weight * result['total_value']
        
        return {
            'total_value': total_weighted_value,
            'model': 'Composite (Crypto-Optimized)' if use_crypto_weights else 'Composite (Traditional)',
            'individual_models': models_results,
            'weights': weights,
            'crypto_optimized': use_crypto_weights,
            'parameters': {
                'spread_0': spread_0,
                'spread_1': spread_1,
                'volatility': volatility,
                'volume_0': volume_0,
                'volume_mm': volume_mm,
                'depth_0': depth_0,
                'depth_mm': depth_mm,
                'asset_price': asset_price,
                'daily_volume_0': daily_volume_0,
                'daily_volume_mm': daily_volume_mm
            }
        }

def generate_trade_size_distribution(min_size: float = 100, 
                                   max_size: float = 10000, 
                                   num_buckets: int = 20,
                                   distribution_type: str = 'log_normal') -> Tuple[List[float], List[float]]:
    """
    Generate trade size distribution for valuation models
    """
    if distribution_type == 'log_normal':
        # Log-normal distribution (common in trading)
        sizes = np.logspace(np.log10(min_size), np.log10(max_size), num_buckets)
        # Probability density based on log-normal
        mu = np.log(np.sqrt(min_size * max_size))
        sigma = 0.5
        probabilities = []
        for size in sizes:
            p = (1 / (size * sigma * np.sqrt(2 * np.pi))) * np.exp(-((np.log(size) - mu) ** 2) / (2 * sigma ** 2))
            probabilities.append(p)
        # Normalize probabilities
        total_prob = sum(probabilities)
        probabilities = [p / total_prob for p in probabilities]
        
    elif distribution_type == 'power_law':
        # Power law distribution
        alpha = 2.0  # Power law exponent
        sizes = np.linspace(min_size, max_size, num_buckets)
        probabilities = [size ** (-alpha) for size in sizes]
        # Normalize probabilities
        total_prob = sum(probabilities)
        probabilities = [p / total_prob for p in probabilities]
        
    else:  # uniform
        sizes = np.linspace(min_size, max_size, num_buckets)
        probabilities = [1.0 / num_buckets] * num_buckets
    
    return sizes.tolist(), probabilities
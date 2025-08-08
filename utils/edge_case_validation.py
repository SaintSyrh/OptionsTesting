"""
Edge Case and Extreme Market Scenario Validation

This module handles validation for extreme market conditions, edge cases,
and scenarios that require special financial logic validation.
"""

import math
import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import logging

from utils.financial_validation import (
    ValidationResult, ValidationSeverity, ValidationSummary,
    MarketType, AssetClass
)

logger = logging.getLogger(__name__)


class ExtremeCaseType(Enum):
    """Types of extreme market cases"""
    FLASH_CRASH = "flash_crash"
    MARKET_STRESS = "market_stress"
    CRYPTO_COLLAPSE = "crypto_collapse"
    LIQUIDITY_CRISIS = "liquidity_crisis"
    VOLATILITY_EXPLOSION = "volatility_explosion"
    NEAR_EXPIRY_GAMMA = "near_expiry_gamma"
    DEEP_ITM_OTM = "deep_itm_otm"
    ZERO_INTEREST_RATE = "zero_interest_rate"
    NEGATIVE_RATES = "negative_rates"
    HYPERINFLATION = "hyperinflation"


@dataclass
class ExtremeScenarioParameters:
    """Parameters defining an extreme market scenario"""
    scenario_type: ExtremeCaseType
    volatility_multiplier: float = 1.0
    time_compression_factor: float = 1.0
    liquidity_reduction_factor: float = 1.0
    spread_expansion_factor: float = 1.0
    description: str = ""


class ExtremeMarketValidator:
    """
    Validator specialized for extreme market conditions and edge cases
    """
    
    def __init__(self):
        self.extreme_scenarios = self._setup_extreme_scenarios()
        
    def _setup_extreme_scenarios(self) -> Dict[ExtremeCaseType, ExtremeScenarioParameters]:
        """Setup predefined extreme scenarios"""
        return {
            ExtremeCaseType.FLASH_CRASH: ExtremeScenarioParameters(
                ExtremeCaseType.FLASH_CRASH,
                volatility_multiplier=10.0,
                time_compression_factor=100.0,  # Minutes instead of days
                liquidity_reduction_factor=0.1,
                spread_expansion_factor=20.0,
                description="Flash crash: Extreme volatility, compressed time, vanishing liquidity"
            ),
            ExtremeCaseType.MARKET_STRESS: ExtremeScenarioParameters(
                ExtremeCaseType.MARKET_STRESS,
                volatility_multiplier=3.0,
                time_compression_factor=5.0,
                liquidity_reduction_factor=0.3,
                spread_expansion_factor=5.0,
                description="Market stress: Elevated volatility, reduced liquidity, wider spreads"
            ),
            ExtremeCaseType.CRYPTO_COLLAPSE: ExtremeScenarioParameters(
                ExtremeCaseType.CRYPTO_COLLAPSE,
                volatility_multiplier=15.0,
                time_compression_factor=50.0,
                liquidity_reduction_factor=0.05,
                spread_expansion_factor=50.0,
                description="Crypto collapse: Extreme downward volatility, liquidity disappears"
            ),
            ExtremeCaseType.VOLATILITY_EXPLOSION: ExtremeScenarioParameters(
                ExtremeCaseType.VOLATILITY_EXPLOSION,
                volatility_multiplier=20.0,
                time_compression_factor=1.0,
                liquidity_reduction_factor=0.2,
                spread_expansion_factor=10.0,
                description="Volatility explosion: Extreme implied volatility, gamma risk"
            )
        }

    def validate_extreme_volatility_scenarios(
        self,
        volatility: float,
        time_to_expiration: float,
        spot_price: float,
        strike_price: float,
        scenario_type: Optional[ExtremeCaseType] = None
    ) -> ValidationSummary:
        """Validate parameters under extreme volatility conditions"""
        
        summary = ValidationSummary(True, [], [], [], 0)
        
        # Detect scenario type if not provided
        if scenario_type is None:
            scenario_type = self._detect_scenario_type(volatility, time_to_expiration)
        
        # 1. Volatility explosion check
        if volatility > 3.0:  # >300% annual volatility
            if time_to_expiration < 0.1:  # <1.2 months
                summary.add_result(ValidationResult(
                    False, ValidationSeverity.ERROR,
                    f"Extreme volatility scenario: {volatility:.1%} volatility with "
                    f"{time_to_expiration*365:.1f} days to expiry may violate Black-Scholes assumptions. "
                    f"Consider using jump-diffusion or stochastic volatility models."
                ))
            else:
                summary.add_result(ValidationResult(
                    True, ValidationSeverity.WARNING,
                    f"Very high volatility {volatility:.1%} detected - model reliability decreased"
                ))
        
        # 2. Vol-time interaction check
        vol_time_product = volatility * math.sqrt(time_to_expiration)
        if vol_time_product > 2.0:  # Very high vol*sqrt(T)
            summary.add_result(ValidationResult(
                True, ValidationSeverity.WARNING,
                f"Vol*sqrt(T) = {vol_time_product:.2f} is very high - "
                f"option delta may be unstable, gamma risk extreme"
            ))
        elif vol_time_product < 0.05:  # Very low vol*sqrt(T) 
            summary.add_result(ValidationResult(
                True, ValidationSeverity.WARNING,
                f"Vol*sqrt(T) = {vol_time_product:.3f} is very low - "
                f"option may have minimal time value, high numerical sensitivity"
            ))
        
        # 3. Gamma explosion near expiry
        if time_to_expiration < 0.01 and abs(math.log(spot_price/strike_price)) < 0.1:
            # Near expiry and near ATM
            summary.add_result(ValidationResult(
                False, ValidationSeverity.ERROR,
                f"Gamma explosion risk: {time_to_expiration*365:.1f} days to expiry "
                f"with spot/strike ratio {spot_price/strike_price:.3f}. "
                f"Delta and gamma will be extremely unstable."
            ))
        
        # 4. Scenario-specific validation
        if scenario_type in self.extreme_scenarios:
            scenario = self.extreme_scenarios[scenario_type]
            summary.add_result(ValidationResult(
                True, ValidationSeverity.INFO,
                f"Detected {scenario_type.value}: {scenario.description}"
            ))
        
        return summary

    def validate_deep_itm_otm_options(
        self,
        spot_price: float,
        strike_price: float,
        time_to_expiration: float,
        risk_free_rate: float,
        option_type: str
    ) -> ValidationSummary:
        """Validate deep in-the-money or out-of-the-money options"""
        
        summary = ValidationSummary(True, [], [], [], 0)
        
        moneyness = strike_price / spot_price
        
        # Calculate intrinsic and time value boundaries
        if option_type.lower() == 'call':
            intrinsic_value = max(spot_price - strike_price, 0)
            is_itm = spot_price > strike_price
        else:  # put
            pv_strike = strike_price * math.exp(-risk_free_rate * time_to_expiration)
            intrinsic_value = max(pv_strike - spot_price, 0)
            is_itm = spot_price < strike_price
        
        # Deep ITM validation
        if moneyness < 0.5 and option_type.lower() == 'call':  # Deep ITM call
            time_value_max = spot_price * 0.05  # Assume max 5% time value
            summary.add_result(ValidationResult(
                True, ValidationSeverity.WARNING,
                f"Deep ITM call: Strike/Spot = {moneyness:.3f}. "
                f"Option value will be mostly intrinsic (${intrinsic_value:.2f}), "
                f"minimal time value (<${time_value_max:.2f}). High delta (~1.0), low gamma."
            ))
            
            # Check for early exercise conditions (American options)
            if risk_free_rate > 0.01:  # If rates are meaningful
                summary.add_result(ValidationResult(
                    True, ValidationSeverity.INFO,
                    f"Deep ITM call may be candidate for early exercise if American-style, "
                    f"especially with dividend yield > risk-free rate"
                ))
        
        elif moneyness > 2.0 and option_type.lower() == 'call':  # Deep OTM call
            summary.add_result(ValidationResult(
                True, ValidationSeverity.WARNING,
                f"Deep OTM call: Strike/Spot = {moneyness:.3f}. "
                f"Very low probability of finishing ITM. Delta near 0, minimal gamma. "
                f"Consider if premium justifies tail risk."
            ))
        
        # Similar logic for puts
        elif moneyness > 2.0 and option_type.lower() == 'put':  # Deep ITM put
            summary.add_result(ValidationResult(
                True, ValidationSeverity.WARNING,
                f"Deep ITM put: Strike/Spot = {moneyness:.3f}. "
                f"High intrinsic value, delta near -1.0, early exercise considerations apply."
            ))
        
        elif moneyness < 0.5 and option_type.lower() == 'put':  # Deep OTM put
            summary.add_result(ValidationResult(
                True, ValidationSeverity.WARNING,
                f"Deep OTM put: Strike/Spot = {moneyness:.3f}. "
                f"Very low probability of finishing ITM unless major market crash."
            ))
        
        # Numerical stability warnings for extreme moneyness
        if moneyness < 0.01 or moneyness > 100:
            summary.add_result(ValidationResult(
                False, ValidationSeverity.ERROR,
                f"Extreme moneyness ratio {moneyness:.4f} may cause numerical instability "
                f"in Black-Scholes calculations. Consider alternative valuation methods."
            ))
        
        return summary

    def validate_near_zero_time_scenarios(
        self,
        time_to_expiration: float,
        volatility: float,
        spot_price: float,
        strike_price: float,
        option_type: str
    ) -> ValidationSummary:
        """Validate scenarios with very short time to expiration"""
        
        summary = ValidationSummary(True, [], [], [], 0)
        
        days_to_expiry = time_to_expiration * 365
        hours_to_expiry = days_to_expiry * 24
        
        # Time-based warnings
        if days_to_expiry < 1:
            summary.add_result(ValidationResult(
                True, ValidationSeverity.WARNING,
                f"Less than 1 day to expiry ({hours_to_expiry:.1f} hours). "
                f"Time decay (theta) will be extreme."
            ))
        
        if hours_to_expiry < 24:
            # Check if near ATM - gamma explosion risk
            moneyness = spot_price / strike_price if strike_price > 0 else float('inf')
            if 0.95 <= moneyness <= 1.05:  # Within 5% of ATM
                summary.add_result(ValidationResult(
                    False, ValidationSeverity.ERROR,
                    f"GAMMA EXPLOSION RISK: {hours_to_expiry:.1f} hours to expiry "
                    f"with ATM option (moneyness = {moneyness:.3f}). "
                    f"Delta will swing wildly with small price moves."
                ))
            
            # Theta burn warning
            theoretical_theta_annual = 0.5 * volatility**2 * spot_price  # Rough estimate
            daily_theta = theoretical_theta_annual / 365
            summary.add_result(ValidationResult(
                True, ValidationSeverity.WARNING,
                f"Extreme time decay: Estimated daily theta ~${daily_theta:.2f}. "
                f"Option losing significant value every hour."
            ))
        
        if hours_to_expiry < 4:
            summary.add_result(ValidationResult(
                False, ValidationSeverity.ERROR,
                f"EXTREME NEAR EXPIRY: {hours_to_expiry:.1f} hours remaining. "
                f"Black-Scholes model may be inappropriate. Consider discrete pricing models."
            ))
        
        # Volatility interaction with short time
        vol_daily = volatility / math.sqrt(365)  # Convert annual to daily vol
        expected_daily_move = vol_daily * spot_price
        
        if days_to_expiry < 0.5 and expected_daily_move > abs(spot_price - strike_price):
            summary.add_result(ValidationResult(
                True, ValidationSeverity.INFO,
                f"High probability of crossing strike: Expected daily move "
                f"${expected_daily_move:.2f} vs strike distance ${abs(spot_price - strike_price):.2f}"
            ))
        
        return summary

    def validate_extreme_interest_rate_scenarios(
        self,
        risk_free_rate: float,
        time_to_expiration: float,
        strike_price: float,
        option_type: str
    ) -> ValidationSummary:
        """Validate extreme interest rate scenarios"""
        
        summary = ValidationSummary(True, [], [], [], 0)
        
        # Negative rates
        if risk_free_rate < -0.01:  # Less than -1%
            summary.add_result(ValidationResult(
                True, ValidationSeverity.WARNING,
                f"Negative interest rates ({risk_free_rate:.2%}) detected. "
                f"This affects put-call parity and early exercise decisions."
            ))
            
            if option_type.lower() == 'put':
                summary.add_result(ValidationResult(
                    True, ValidationSeverity.INFO,
                    f"Negative rates reduce put values due to negative discounting effect. "
                    f"Early exercise of American puts less attractive."
                ))
        
        # Very high rates (hyperinflation scenario)
        elif risk_free_rate > 0.20:  # >20%
            summary.add_result(ValidationResult(
                True, ValidationSeverity.WARNING,
                f"Very high interest rates ({risk_free_rate:.1%}) suggest "
                f"hyperinflationary environment. Model assumptions may not hold."
            ))
            
            # Calculate present value impact
            pv_factor = math.exp(-risk_free_rate * time_to_expiration)
            if pv_factor < 0.5:  # Strike PV less than half its face value
                summary.add_result(ValidationResult(
                    True, ValidationSeverity.INFO,
                    f"High rates reduce strike PV to {pv_factor:.1%} of face value. "
                    f"Major impact on put values and put-call parity."
                ))
        
        # Zero or near-zero rates
        elif abs(risk_free_rate) < 0.001:  # Effectively zero
            summary.add_result(ValidationResult(
                True, ValidationSeverity.INFO,
                f"Near-zero interest rates: Minimal discounting effect. "
                f"Put-call parity simplifies to C - P ≈ S - K."
            ))
        
        return summary

    def validate_liquidity_crisis_scenarios(
        self,
        bid_ask_spread_bps: float,
        depth_50bps: float,
        depth_100bps: float,
        depth_200bps: float,
        daily_volume: float,
        asset_price: float
    ) -> ValidationSummary:
        """Validate parameters during liquidity crisis"""
        
        summary = ValidationSummary(True, [], [], [], 0)
        
        # Extreme spread detection
        if bid_ask_spread_bps > 1000:  # >10% spread
            summary.add_result(ValidationResult(
                False, ValidationSeverity.ERROR,
                f"LIQUIDITY CRISIS: Bid-ask spread {bid_ask_spread_bps/100:.1f}% "
                f"indicates severe liquidity shortage. Market making models unreliable."
            ))
        elif bid_ask_spread_bps > 500:  # >5% spread
            summary.add_result(ValidationResult(
                True, ValidationSeverity.WARNING,
                f"Wide spreads ({bid_ask_spread_bps/100:.1f}%) suggest liquidity stress. "
                f"Adjust model parameters for higher adverse selection."
            ))
        
        # Depth collapse detection
        total_depth = depth_50bps + depth_100bps + depth_200bps
        if total_depth < daily_volume * 0.01:  # Less than 1% of daily volume
            summary.add_result(ValidationResult(
                False, ValidationSeverity.ERROR,
                f"DEPTH COLLAPSE: Total depth ${total_depth:,.0f} is only "
                f"{total_depth/daily_volume:.2%} of daily volume ${daily_volume:,.0f}. "
                f"Market impact models will be highly inaccurate."
            ))
        
        # Inverted depth structure (liquidity at wider spreads vanishes first)
        if depth_200bps < depth_50bps * 0.5 and depth_200bps > 0:
            summary.add_result(ValidationResult(
                True, ValidationSeverity.WARNING,
                f"Inverted depth structure: Depth at 200bps (${depth_200bps:,.0f}) "
                f"much less than 50bps (${depth_50bps:,.0f}). "
                f"Suggests liquidity providers pulling back at wider spreads."
            ))
        
        # Volume-to-depth ratio
        if daily_volume > 0 and total_depth > 0:
            turnover_ratio = daily_volume / total_depth
            if turnover_ratio > 50:  # Daily volume >50x total depth
                summary.add_result(ValidationResult(
                    True, ValidationSeverity.WARNING,
                    f"High turnover ratio: Daily volume is {turnover_ratio:.0f}x "
                    f"total depth. Market impact will be severe."
                ))
        
        return summary

    def validate_crypto_specific_edge_cases(
        self,
        volatility: float,
        asset_price: float,
        exchange_name: str,
        time_to_expiration: float
    ) -> ValidationSummary:
        """Validate crypto-specific edge cases"""
        
        summary = ValidationSummary(True, [], [], [], 0)
        
        # Exchange-specific risks
        if "FTX" in exchange_name.upper() or "TERRA" in exchange_name.upper():
            summary.add_result(ValidationResult(
                False, ValidationSeverity.ERROR,
                f"COUNTERPARTY RISK: Exchange {exchange_name} has history of "
                f"collapse/issues. Model assumes functional market infrastructure."
            ))
        
        # Defi/DEX specific risks
        defi_exchanges = ["UNISWAP", "SUSHISWAP", "PANCAKESWAP", "CURVE"]
        if any(dex in exchange_name.upper() for dex in defi_exchanges):
            summary.add_result(ValidationResult(
                True, ValidationSeverity.WARNING,
                f"DeFi DEX detected ({exchange_name}): Consider impermanent loss, "
                f"MEV, and smart contract risks not captured in standard models."
            ))
        
        # Stablecoin depeg scenarios
        if asset_price < 0.95 and "USD" in exchange_name.upper():
            summary.add_result(ValidationResult(
                True, ValidationSeverity.WARNING,
                f"Possible stablecoin depeg: Price ${asset_price:.4f} below $0.95. "
                f"Standard option models may not apply."
            ))
        
        # Weekend/holiday effects in crypto
        if time_to_expiration < 7/365:  # Less than a week
            summary.add_result(ValidationResult(
                True, ValidationSeverity.INFO,
                f"Short-term crypto option: Consider that crypto trades 24/7 "
                f"including weekends, unlike traditional markets."
            ))
        
        # Extreme crypto volatility
        if volatility > 5.0:  # >500% annual
            summary.add_result(ValidationResult(
                True, ValidationSeverity.WARNING,
                f"Extreme crypto volatility ({volatility:.1%}): May reflect "
                f"token economic issues, regulatory risks, or manipulation."
            ))
        
        return summary

    def _detect_scenario_type(self, volatility: float, time_to_expiration: float) -> ExtremeCaseType:
        """Automatically detect the type of extreme scenario"""
        
        if volatility > 5.0 and time_to_expiration < 0.02:  # >500% vol, <1 week
            return ExtremeCaseType.FLASH_CRASH
        elif volatility > 10.0:
            return ExtremeCaseType.CRYPTO_COLLAPSE  
        elif volatility > 3.0:
            return ExtremeCaseType.VOLATILITY_EXPLOSION
        elif time_to_expiration < 0.01:  # <4 days
            return ExtremeCaseType.NEAR_EXPIRY_GAMMA
        else:
            return ExtremeCaseType.MARKET_STRESS

    def validate_numerical_stability(
        self,
        spot_price: float,
        strike_price: float,
        time_to_expiration: float,
        risk_free_rate: float,
        volatility: float
    ) -> ValidationSummary:
        """Validate numerical stability of Black-Scholes calculation"""
        
        summary = ValidationSummary(True, [], [], [], 0)
        
        # Calculate d1 and d2 components for stability analysis
        if strike_price <= 0 or spot_price <= 0 or volatility <= 0 or time_to_expiration <= 0:
            summary.add_result(ValidationResult(
                False, ValidationSeverity.ERROR,
                "Cannot validate numerical stability: Non-positive parameters detected"
            ))
            return summary
        
        log_moneyness = math.log(spot_price / strike_price)
        drift_term = (risk_free_rate + 0.5 * volatility**2) * time_to_expiration
        vol_sqrt_t = volatility * math.sqrt(time_to_expiration)
        
        # Check for extreme d1/d2 values
        d1 = (log_moneyness + drift_term) / vol_sqrt_t
        d2 = d1 - vol_sqrt_t
        
        if abs(d1) > 10 or abs(d2) > 10:
            summary.add_result(ValidationResult(
                False, ValidationSeverity.ERROR,
                f"Numerical instability: d1={d1:.2f}, d2={d2:.2f} are extreme. "
                f"Normal CDF calculations will lose precision."
            ))
        elif abs(d1) > 5 or abs(d2) > 5:
            summary.add_result(ValidationResult(
                True, ValidationSeverity.WARNING,
                f"Potential numerical issues: d1={d1:.2f}, d2={d2:.2f} are large. "
                f"Consider using high-precision arithmetic."
            ))
        
        # Check for underflow/overflow conditions
        if vol_sqrt_t < 1e-10:
            summary.add_result(ValidationResult(
                False, ValidationSeverity.ERROR,
                f"Numerical underflow risk: vol*sqrt(T) = {vol_sqrt_t:.2e} is tiny"
            ))
        
        if abs(log_moneyness) > 50:  # e^50 is huge
            summary.add_result(ValidationResult(
                False, ValidationSeverity.ERROR,
                f"Numerical overflow risk: log(S/K) = {log_moneyness:.2f} is extreme"
            ))
        
        # Rate-time product
        rate_time_product = abs(risk_free_rate * time_to_expiration)
        if rate_time_product > 10:
            summary.add_result(ValidationResult(
                True, ValidationSeverity.WARNING,
                f"Large rate-time product {rate_time_product:.2f} may affect discounting precision"
            ))
        
        return summary

    def comprehensive_edge_case_validation(
        self,
        spot_price: float,
        strike_price: float,
        time_to_expiration: float,
        risk_free_rate: float,
        volatility: float,
        option_type: str,
        market_context: Dict[str, Any] = None
    ) -> ValidationSummary:
        """Run comprehensive edge case validation combining all checks"""
        
        # Combine all edge case validations
        all_summaries = []
        
        # 1. Extreme volatility scenarios
        all_summaries.append(
            self.validate_extreme_volatility_scenarios(
                volatility, time_to_expiration, spot_price, strike_price
            )
        )
        
        # 2. Deep ITM/OTM validation
        all_summaries.append(
            self.validate_deep_itm_otm_options(
                spot_price, strike_price, time_to_expiration, risk_free_rate, option_type
            )
        )
        
        # 3. Near-zero time scenarios
        all_summaries.append(
            self.validate_near_zero_time_scenarios(
                time_to_expiration, volatility, spot_price, strike_price, option_type
            )
        )
        
        # 4. Interest rate extremes
        all_summaries.append(
            self.validate_extreme_interest_rate_scenarios(
                risk_free_rate, time_to_expiration, strike_price, option_type
            )
        )
        
        # 5. Numerical stability
        all_summaries.append(
            self.validate_numerical_stability(
                spot_price, strike_price, time_to_expiration, risk_free_rate, volatility
            )
        )
        
        # 6. Market-specific validation
        if market_context:
            if market_context.get('market_type') == 'crypto':
                all_summaries.append(
                    self.validate_crypto_specific_edge_cases(
                        volatility, spot_price, 
                        market_context.get('exchange', 'Unknown'),
                        time_to_expiration
                    )
                )
            
            # Liquidity crisis validation if depth data available
            if all(k in market_context for k in ['bid_ask_spread', 'depth_50bps', 'depth_100bps', 'depth_200bps', 'daily_volume']):
                all_summaries.append(
                    self.validate_liquidity_crisis_scenarios(
                        market_context['bid_ask_spread'],
                        market_context['depth_50bps'],
                        market_context['depth_100bps'],
                        market_context['depth_200bps'],
                        market_context['daily_volume'],
                        spot_price
                    )
                )
        
        # Combine all summaries
        combined = ValidationSummary(True, [], [], [], 0)
        for summary in all_summaries:
            for error in summary.errors:
                combined.add_result(error)
            for warning in summary.warnings:
                combined.add_result(warning)
            for info in summary.infos:
                combined.add_result(info)
        
        return combined


# Global instance
extreme_validator = ExtremeMarketValidator()
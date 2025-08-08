"""
Comprehensive Financial Input Validation for Options Pricing and Market Analysis

This module provides robust validation for all financial parameters used in the options
pricing and market depth analysis application, with special focus on edge cases and
realistic market bounds.
"""

import math
import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Validation severity levels"""
    ERROR = "error"      # Invalid input - must be rejected
    WARNING = "warning"  # Questionable input - allow with warning
    INFO = "info"        # Edge case but valid - informational only


class MarketType(Enum):
    """Market types for context-aware validation"""
    TRADITIONAL_EQUITY = "traditional_equity"
    CRYPTO = "crypto"
    COMMODITY = "commodity"
    FX = "fx"


class AssetClass(Enum):
    """Asset classes for validation bounds"""
    LARGE_CAP_EQUITY = "large_cap_equity"
    SMALL_CAP_EQUITY = "small_cap_equity"
    CRYPTO_MAJOR = "crypto_major"      # BTC, ETH
    CRYPTO_ALT = "crypto_alt"          # Altcoins
    COMMODITY = "commodity"
    BOND = "bond"


@dataclass
class ValidationResult:
    """Result of a validation check"""
    is_valid: bool
    severity: ValidationSeverity
    message: str
    suggested_range: Optional[Tuple[float, float]] = None
    corrected_value: Optional[float] = None


@dataclass
class ValidationSummary:
    """Summary of all validation results"""
    is_valid: bool
    errors: List[ValidationResult]
    warnings: List[ValidationResult]
    infos: List[ValidationResult]
    total_checks: int
    
    def add_result(self, result: ValidationResult) -> None:
        """Add a validation result to appropriate category"""
        if result.severity == ValidationSeverity.ERROR:
            self.errors.append(result)
            self.is_valid = False
        elif result.severity == ValidationSeverity.WARNING:
            self.warnings.append(result)
        else:
            self.infos.append(result)
        self.total_checks += 1


class FinancialValidator:
    """
    Comprehensive financial parameter validator with market-aware bounds
    and sophisticated edge case handling
    """
    
    def __init__(self, market_type: MarketType = MarketType.CRYPTO):
        self.market_type = market_type
        self._setup_market_bounds()
        
    def _setup_market_bounds(self) -> None:
        """Setup validation bounds based on market type"""
        if self.market_type == MarketType.CRYPTO:
            self.volatility_bounds = {
                AssetClass.CRYPTO_MAJOR: (0.001, 5.0),    # 0.1% to 500% annualized
                AssetClass.CRYPTO_ALT: (0.001, 10.0),     # 0.1% to 1000% annualized
            }
            self.risk_free_bounds = (-0.05, 0.15)         # -5% to 15% (DeFi rates)
            self.spread_bounds_bps = (0.1, 10000)         # 0.01% to 100%
            self.time_bounds_years = (0.0001, 10.0)       # 1 hour to 10 years
        else:  # Traditional markets
            self.volatility_bounds = {
                AssetClass.LARGE_CAP_EQUITY: (0.05, 2.0), # 5% to 200% annualized
                AssetClass.SMALL_CAP_EQUITY: (0.1, 4.0),  # 10% to 400% annualized
            }
            self.risk_free_bounds = (-0.01, 0.20)         # -1% to 20%
            self.spread_bounds_bps = (0.1, 1000)          # 0.01% to 10%
            self.time_bounds_years = (0.0027, 5.0)        # 1 day to 5 years

    def validate_black_scholes_parameters(
        self, 
        spot_price: float,
        strike_price: float,
        time_to_expiration: float,
        risk_free_rate: float,
        volatility: float,
        asset_class: AssetClass = AssetClass.CRYPTO_MAJOR,
        option_type: str = "call"
    ) -> ValidationSummary:
        """
        Comprehensive validation of Black-Scholes parameters
        
        Args:
            spot_price: Current asset price (S)
            strike_price: Strike price (K)
            time_to_expiration: Time to expiration in years (T)
            risk_free_rate: Risk-free rate (r)
            volatility: Volatility (σ)
            asset_class: Asset class for context-aware bounds
            option_type: "call" or "put"
        """
        summary = ValidationSummary(True, [], [], [], 0)
        
        # 1. Spot Price Validation
        result = self._validate_spot_price(spot_price)
        summary.add_result(result)
        
        # 2. Strike Price Validation
        result = self._validate_strike_price(strike_price, spot_price)
        summary.add_result(result)
        
        # 3. Time to Expiration Validation
        result = self._validate_time_to_expiration(time_to_expiration)
        summary.add_result(result)
        
        # 4. Risk-Free Rate Validation
        result = self._validate_risk_free_rate(risk_free_rate)
        summary.add_result(result)
        
        # 5. Volatility Validation
        result = self._validate_volatility(volatility, asset_class)
        summary.add_result(result)
        
        # 6. Option Type Validation
        result = self._validate_option_type(option_type)
        summary.add_result(result)
        
        # 7. Cross-Parameter Validation
        cross_results = self._validate_bs_cross_parameters(
            spot_price, strike_price, time_to_expiration, 
            risk_free_rate, volatility, option_type
        )
        for result in cross_results:
            summary.add_result(result)
        
        return summary

    def _validate_spot_price(self, spot_price: float) -> ValidationResult:
        """Validate spot/current price"""
        if not isinstance(spot_price, (int, float)):
            return ValidationResult(
                False, ValidationSeverity.ERROR,
                "Spot price must be numeric",
                suggested_range=(0.0001, float('inf'))
            )
        
        if spot_price <= 0:
            return ValidationResult(
                False, ValidationSeverity.ERROR,
                "Spot price must be positive",
                suggested_range=(0.0001, float('inf'))
            )
        
        if spot_price < 0.0001:
            return ValidationResult(
                False, ValidationSeverity.WARNING,
                f"Spot price {spot_price:.6f} is very small - may cause numerical instability",
                suggested_range=(0.0001, 100000)
            )
        
        if spot_price > 1e8:
            return ValidationResult(
                False, ValidationSeverity.WARNING,
                f"Spot price {spot_price:,.0f} is extremely large - may cause overflow",
                suggested_range=(0.0001, 100000)
            )
        
        return ValidationResult(
            True, ValidationSeverity.INFO,
            f"Spot price {spot_price:.4f} is valid"
        )

    def _validate_strike_price(self, strike_price: float, spot_price: float) -> ValidationResult:
        """Validate strike price with spot price context"""
        if not isinstance(strike_price, (int, float)):
            return ValidationResult(
                False, ValidationSeverity.ERROR,
                "Strike price must be numeric",
                suggested_range=(0.0001, float('inf'))
            )
        
        if strike_price <= 0:
            return ValidationResult(
                False, ValidationSeverity.ERROR,
                "Strike price must be positive",
                suggested_range=(0.0001, float('inf'))
            )
        
        # Moneyness validation
        moneyness = strike_price / spot_price if spot_price > 0 else 0
        
        if moneyness < 0.01:  # Strike is 1% of spot or less
            return ValidationResult(
                False, ValidationSeverity.WARNING,
                f"Strike/Spot ratio {moneyness:.4f} indicates extremely deep ITM option - "
                f"may have minimal time value",
                suggested_range=(spot_price * 0.1, spot_price * 10)
            )
        
        if moneyness > 100:  # Strike is 100x spot or more
            return ValidationResult(
                False, ValidationSeverity.WARNING,
                f"Strike/Spot ratio {moneyness:.2f} indicates extremely deep OTM option - "
                f"may have minimal intrinsic value",
                suggested_range=(spot_price * 0.1, spot_price * 10)
            )
        
        if 0.01 <= moneyness <= 0.5:
            severity = ValidationSeverity.INFO
            message = f"Deep ITM option (Strike/Spot = {moneyness:.3f})"
        elif 0.5 < moneyness < 0.8:
            severity = ValidationSeverity.INFO
            message = f"ITM option (Strike/Spot = {moneyness:.3f})"
        elif 0.8 <= moneyness <= 1.2:
            severity = ValidationSeverity.INFO
            message = f"Near-the-money option (Strike/Spot = {moneyness:.3f})"
        elif 1.2 < moneyness <= 2.0:
            severity = ValidationSeverity.INFO
            message = f"OTM option (Strike/Spot = {moneyness:.3f})"
        else:
            severity = ValidationSeverity.INFO
            message = f"Deep OTM option (Strike/Spot = {moneyness:.3f})"
        
        return ValidationResult(True, severity, message)

    def _validate_time_to_expiration(self, time_to_expiration: float) -> ValidationResult:
        """Validate time to expiration"""
        if not isinstance(time_to_expiration, (int, float)):
            return ValidationResult(
                False, ValidationSeverity.ERROR,
                "Time to expiration must be numeric",
                suggested_range=self.time_bounds_years
            )
        
        if time_to_expiration <= 0:
            return ValidationResult(
                False, ValidationSeverity.ERROR,
                "Time to expiration must be positive",
                suggested_range=self.time_bounds_years
            )
        
        min_time, max_time = self.time_bounds_years
        
        if time_to_expiration < min_time:
            hours = time_to_expiration * 365 * 24
            return ValidationResult(
                False, ValidationSeverity.WARNING,
                f"Time to expiration {hours:.2f} hours is very short - "
                f"may cause gamma explosion near expiry",
                suggested_range=self.time_bounds_years
            )
        
        if time_to_expiration > max_time:
            return ValidationResult(
                False, ValidationSeverity.WARNING,
                f"Time to expiration {time_to_expiration:.2f} years is very long - "
                f"model assumptions may not hold",
                suggested_range=self.time_bounds_years
            )
        
        # Special warnings for near-expiry
        days_to_expiry = time_to_expiration * 365
        if days_to_expiry < 1:
            return ValidationResult(
                True, ValidationSeverity.WARNING,
                f"Near-expiry option ({days_to_expiry:.2f} days) - "
                f"Greeks will be very sensitive to price moves"
            )
        
        return ValidationResult(
            True, ValidationSeverity.INFO,
            f"Time to expiration {time_to_expiration:.4f} years ({days_to_expiry:.1f} days) is valid"
        )

    def _validate_risk_free_rate(self, risk_free_rate: float) -> ValidationResult:
        """Validate risk-free rate"""
        if not isinstance(risk_free_rate, (int, float)):
            return ValidationResult(
                False, ValidationSeverity.ERROR,
                "Risk-free rate must be numeric",
                suggested_range=self.risk_free_bounds
            )
        
        min_rate, max_rate = self.risk_free_bounds
        
        if risk_free_rate < min_rate:
            return ValidationResult(
                False, ValidationSeverity.WARNING,
                f"Risk-free rate {risk_free_rate:.3%} is below typical range - "
                f"negative rates are unusual",
                suggested_range=self.risk_free_bounds
            )
        
        if risk_free_rate > max_rate:
            return ValidationResult(
                False, ValidationSeverity.WARNING,
                f"Risk-free rate {risk_free_rate:.3%} is above typical range - "
                f"very high rates may indicate economic stress",
                suggested_range=self.risk_free_bounds
            )
        
        return ValidationResult(
            True, ValidationSeverity.INFO,
            f"Risk-free rate {risk_free_rate:.3%} is valid"
        )

    def _validate_volatility(self, volatility: float, asset_class: AssetClass) -> ValidationResult:
        """Validate volatility with asset class context"""
        if not isinstance(volatility, (int, float)):
            return ValidationResult(
                False, ValidationSeverity.ERROR,
                "Volatility must be numeric",
                suggested_range=(0.001, 2.0)
            )
        
        if volatility <= 0:
            return ValidationResult(
                False, ValidationSeverity.ERROR,
                "Volatility must be positive",
                suggested_range=(0.001, 2.0)
            )
        
        # Get bounds for asset class
        if asset_class in self.volatility_bounds:
            min_vol, max_vol = self.volatility_bounds[asset_class]
        else:
            min_vol, max_vol = (0.05, 2.0)  # Default bounds
        
        if volatility < min_vol:
            return ValidationResult(
                False, ValidationSeverity.WARNING,
                f"Volatility {volatility:.1%} is below typical range for {asset_class.value} "
                f"({min_vol:.1%} - {max_vol:.1%}) - market may be unusually calm",
                suggested_range=(min_vol, max_vol)
            )
        
        if volatility > max_vol:
            return ValidationResult(
                False, ValidationSeverity.WARNING,
                f"Volatility {volatility:.1%} is above typical range for {asset_class.value} "
                f"({min_vol:.1%} - {max_vol:.1%}) - may indicate extreme market stress",
                suggested_range=(min_vol, max_vol)
            )
        
        # Special cases
        if volatility > 3.0:  # 300% annual volatility
            return ValidationResult(
                True, ValidationSeverity.WARNING,
                f"Extreme volatility {volatility:.1%} - model may be unreliable in crash scenarios"
            )
        
        if volatility < 0.01:  # Less than 1% annual volatility
            return ValidationResult(
                True, ValidationSeverity.WARNING,
                f"Very low volatility {volatility:.1%} - option may have minimal time value"
            )
        
        return ValidationResult(
            True, ValidationSeverity.INFO,
            f"Volatility {volatility:.1%} is valid for {asset_class.value}"
        )

    def _validate_option_type(self, option_type: str) -> ValidationResult:
        """Validate option type"""
        if not isinstance(option_type, str):
            return ValidationResult(
                False, ValidationSeverity.ERROR,
                "Option type must be a string",
                suggested_range=None
            )
        
        option_type = option_type.lower().strip()
        valid_types = ['call', 'put']
        
        if option_type not in valid_types:
            return ValidationResult(
                False, ValidationSeverity.ERROR,
                f"Option type must be one of {valid_types}, got '{option_type}'",
                suggested_range=None
            )
        
        return ValidationResult(
            True, ValidationSeverity.INFO,
            f"Option type '{option_type}' is valid"
        )

    def _validate_bs_cross_parameters(
        self, 
        spot: float, 
        strike: float, 
        time: float, 
        rate: float, 
        vol: float, 
        option_type: str
    ) -> List[ValidationResult]:
        """Cross-parameter validation for Black-Scholes"""
        results = []
        
        # 1. Numerical stability check
        if vol * math.sqrt(time) < 0.001:
            results.append(ValidationResult(
                False, ValidationSeverity.WARNING,
                f"Vol * sqrt(T) = {vol * math.sqrt(time):.6f} is very small - "
                f"may cause numerical instability in d1/d2 calculations"
            ))
        
        # 2. Arbitrage condition check
        if option_type.lower() == 'call':
            # Call option value should be at least max(S - K*e^(-rT), 0)
            intrinsic = max(spot - strike * math.exp(-rate * time), 0)
            if intrinsic / spot > 0.99:
                results.append(ValidationResult(
                    True, ValidationSeverity.INFO,
                    f"Call option is {intrinsic/spot:.1%} of spot price - "
                    f"mostly intrinsic value with minimal time value"
                ))
        else:  # put
            # Put option value should be at least max(K*e^(-rT) - S, 0)
            intrinsic = max(strike * math.exp(-rate * time) - spot, 0)
            if intrinsic / spot > 0.99:
                results.append(ValidationResult(
                    True, ValidationSeverity.INFO,
                    f"Put option intrinsic value is {intrinsic/spot:.1%} of spot price - "
                    f"mostly intrinsic value with minimal time value"
                ))
        
        # 3. Extreme scenario detection
        d1_term = math.log(spot/strike) + (rate + 0.5*vol**2)*time
        d1_denominator = vol * math.sqrt(time)
        
        if abs(d1_term) > 10 * d1_denominator:
            results.append(ValidationResult(
                True, ValidationSeverity.WARNING,
                "Option is extremely deep ITM/OTM - d1 calculation may be numerically unstable"
            ))
        
        return results

    def validate_depth_parameters(
        self,
        bid_ask_spread_bps: float,
        depth_50bps: float,
        depth_100bps: float, 
        depth_200bps: float,
        asset_price: float,
        exchange_name: str = "Unknown"
    ) -> ValidationSummary:
        """
        Validate market depth parameters
        """
        summary = ValidationSummary(True, [], [], [], 0)
        
        # 1. Bid-Ask Spread Validation
        result = self._validate_bid_ask_spread(bid_ask_spread_bps, exchange_name)
        summary.add_result(result)
        
        # 2. Depth Values Validation
        depths = [depth_50bps, depth_100bps, depth_200bps]
        depth_names = ["50bps", "100bps", "200bps"]
        
        for depth, name in zip(depths, depth_names):
            result = self._validate_depth_value(depth, name, asset_price)
            summary.add_result(result)
        
        # 3. Depth Structure Validation
        result = self._validate_depth_structure(depth_50bps, depth_100bps, depth_200bps)
        summary.add_result(result)
        
        # 4. Exchange-specific validation
        result = self._validate_exchange_name(exchange_name)
        summary.add_result(result)
        
        return summary

    def _validate_bid_ask_spread(self, spread_bps: float, exchange: str) -> ValidationResult:
        """Validate bid-ask spread"""
        if not isinstance(spread_bps, (int, float)):
            return ValidationResult(
                False, ValidationSeverity.ERROR,
                "Bid-ask spread must be numeric",
                suggested_range=self.spread_bounds_bps
            )
        
        if spread_bps <= 0:
            return ValidationResult(
                False, ValidationSeverity.ERROR,
                "Bid-ask spread must be positive",
                suggested_range=self.spread_bounds_bps
            )
        
        min_spread, max_spread = self.spread_bounds_bps
        
        if spread_bps < min_spread:
            return ValidationResult(
                False, ValidationSeverity.WARNING,
                f"Spread {spread_bps:.2f}bps is extremely tight - "
                f"may indicate subsidized market making or data error",
                suggested_range=self.spread_bounds_bps
            )
        
        if spread_bps > max_spread:
            return ValidationResult(
                False, ValidationSeverity.WARNING,
                f"Spread {spread_bps:.0f}bps is extremely wide - "
                f"may indicate illiquid or stressed market conditions",
                suggested_range=self.spread_bounds_bps
            )
        
        # Context-aware warnings
        if self.market_type == MarketType.CRYPTO:
            if "Binance" in exchange and spread_bps > 50:
                return ValidationResult(
                    True, ValidationSeverity.WARNING,
                    f"Spread {spread_bps:.1f}bps seems high for Binance (typically <20bps for major pairs)"
                )
            elif "Coinbase" in exchange and spread_bps > 100:
                return ValidationResult(
                    True, ValidationSeverity.WARNING,
                    f"Spread {spread_bps:.1f}bps seems high for Coinbase Pro"
                )
        
        return ValidationResult(
            True, ValidationSeverity.INFO,
            f"Bid-ask spread {spread_bps:.2f}bps is valid for {exchange}"
        )

    def _validate_depth_value(self, depth: float, depth_name: str, asset_price: float) -> ValidationResult:
        """Validate individual depth value"""
        if not isinstance(depth, (int, float)):
            return ValidationResult(
                False, ValidationSeverity.ERROR,
                f"Depth {depth_name} must be numeric",
                suggested_range=(0, float('inf'))
            )
        
        if depth < 0:
            return ValidationResult(
                False, ValidationSeverity.ERROR,
                f"Depth {depth_name} cannot be negative",
                suggested_range=(0, float('inf'))
            )
        
        if depth == 0:
            return ValidationResult(
                True, ValidationSeverity.WARNING,
                f"Depth {depth_name} is zero - no liquidity at this level"
            )
        
        # Relative size checks
        if asset_price > 0:
            depth_as_pct_of_price = depth / asset_price
            if depth_as_pct_of_price > 10000:  # Depth is 10000x the price
                return ValidationResult(
                    True, ValidationSeverity.WARNING,
                    f"Depth {depth_name} (${depth:,.0f}) is {depth_as_pct_of_price:.0f}x "
                    f"the asset price - unusually high"
                )
        
        return ValidationResult(
            True, ValidationSeverity.INFO,
            f"Depth {depth_name} ${depth:,.0f} is valid"
        )

    def _validate_depth_structure(self, depth_50: float, depth_100: float, depth_200: float) -> ValidationResult:
        """Validate depth structure makes economic sense"""
        depths = [depth_50, depth_100, depth_200]
        
        # All depths should be non-negative (individual validation handles this)
        if any(d < 0 for d in depths):
            return ValidationResult(
                False, ValidationSeverity.ERROR,
                "All depth values must be non-negative"
            )
        
        # Generally expect depth to increase with spread tolerance
        # (though this isn't always true in practice)
        if depth_50 > 0 and depth_100 > 0 and depth_50 > depth_100 * 2:
            return ValidationResult(
                True, ValidationSeverity.WARNING,
                f"Depth at 50bps (${depth_50:,.0f}) is more than 2x depth at 100bps "
                f"(${depth_100:,.0f}) - unusual depth structure"
            )
        
        if depth_100 > 0 and depth_200 > 0 and depth_100 > depth_200 * 1.5:
            return ValidationResult(
                True, ValidationSeverity.WARNING,
                f"Depth at 100bps (${depth_100:,.0f}) is more than 1.5x depth at 200bps "
                f"(${depth_200:,.0f}) - unusual depth structure"
            )
        
        # Check for reasonable depth progression
        non_zero_depths = [d for d in depths if d > 0]
        if len(non_zero_depths) >= 2:
            # Calculate average growth rate
            ratios = []
            for i in range(len(depths) - 1):
                if depths[i] > 0 and depths[i+1] > 0:
                    ratios.append(depths[i+1] / depths[i])
            
            if ratios and max(ratios) > 10:
                return ValidationResult(
                    True, ValidationSeverity.INFO,
                    "Large depth increases between levels - may indicate concentrated liquidity"
                )
        
        return ValidationResult(
            True, ValidationSeverity.INFO,
            "Depth structure appears reasonable"
        )

    def _validate_exchange_name(self, exchange: str) -> ValidationResult:
        """Validate exchange name"""
        if not isinstance(exchange, str):
            return ValidationResult(
                False, ValidationSeverity.ERROR,
                "Exchange name must be a string"
            )
        
        exchange = exchange.strip()
        if not exchange:
            return ValidationResult(
                False, ValidationSeverity.WARNING,
                "Exchange name is empty"
            )
        
        # Known exchange validation for crypto
        if self.market_type == MarketType.CRYPTO:
            major_exchanges = [
                'Binance', 'Coinbase', 'Kraken', 'Bitstamp', 'OKX', 
                'Bybit', 'KuCoin', 'Huobi', 'Gate', 'MEXC'
            ]
            
            if exchange not in major_exchanges and exchange != "Other":
                return ValidationResult(
                    True, ValidationSeverity.INFO,
                    f"Exchange '{exchange}' not in list of major crypto exchanges"
                )
        
        return ValidationResult(
            True, ValidationSeverity.INFO,
            f"Exchange name '{exchange}' is valid"
        )

    def validate_market_maker_parameters(
        self,
        daily_volume: float,
        asset_price: float,
        volatility: float,
        mm_volume_contribution: float,
        model_params: Optional[Dict[str, float]] = None
    ) -> ValidationSummary:
        """Validate market maker model parameters"""
        summary = ValidationSummary(True, [], [], [], 0)
        
        # 1. Daily Volume Validation
        result = self._validate_daily_volume(daily_volume, asset_price)
        summary.add_result(result)
        
        # 2. Asset Price Validation (same as spot price)
        result = self._validate_spot_price(asset_price)
        summary.add_result(result)
        
        # 3. Volatility Validation
        result = self._validate_volatility(volatility, AssetClass.CRYPTO_MAJOR)
        summary.add_result(result)
        
        # 4. MM Volume Contribution
        result = self._validate_mm_volume_contribution(mm_volume_contribution, daily_volume)
        summary.add_result(result)
        
        # 5. Model Parameters (if provided)
        if model_params:
            model_results = self._validate_model_parameters(model_params)
            for result in model_results:
                summary.add_result(result)
        
        return summary

    def _validate_daily_volume(self, daily_volume: float, asset_price: float) -> ValidationResult:
        """Validate daily trading volume"""
        if not isinstance(daily_volume, (int, float)):
            return ValidationResult(
                False, ValidationSeverity.ERROR,
                "Daily volume must be numeric",
                suggested_range=(0, float('inf'))
            )
        
        if daily_volume < 0:
            return ValidationResult(
                False, ValidationSeverity.ERROR,
                "Daily volume cannot be negative",
                suggested_range=(0, float('inf'))
            )
        
        if daily_volume == 0:
            return ValidationResult(
                True, ValidationSeverity.WARNING,
                "Daily volume is zero - no trading activity"
            )
        
        # Volume-to-market cap checks
        if asset_price > 0:
            # Assume some reasonable market cap multiples
            if daily_volume / asset_price > 1000:  # Daily volume > 1000x price
                return ValidationResult(
                    True, ValidationSeverity.WARNING,
                    f"Daily volume ${daily_volume:,.0f} is {daily_volume/asset_price:.0f}x "
                    f"the asset price - extremely high turnover"
                )
        
        return ValidationResult(
            True, ValidationSeverity.INFO,
            f"Daily volume ${daily_volume:,.0f} is valid"
        )

    def _validate_mm_volume_contribution(self, mm_volume: float, daily_volume: float) -> ValidationResult:
        """Validate market maker volume contribution"""
        if not isinstance(mm_volume, (int, float)):
            return ValidationResult(
                False, ValidationSeverity.ERROR,
                "MM volume contribution must be numeric",
                suggested_range=(0, daily_volume)
            )
        
        if mm_volume < 0:
            return ValidationResult(
                False, ValidationSeverity.ERROR,
                "MM volume contribution cannot be negative",
                suggested_range=(0, daily_volume)
            )
        
        if daily_volume > 0:
            mm_percentage = mm_volume / daily_volume
            
            if mm_percentage > 1.0:
                return ValidationResult(
                    False, ValidationSeverity.WARNING,
                    f"MM volume (${mm_volume:,.0f}) exceeds total daily volume "
                    f"(${daily_volume:,.0f}) - {mm_percentage:.1%}",
                    suggested_range=(0, daily_volume)
                )
            
            if mm_percentage > 0.5:
                return ValidationResult(
                    True, ValidationSeverity.WARNING,
                    f"MM contributes {mm_percentage:.1%} of daily volume - "
                    f"very high market maker dominance"
                )
            
            if mm_percentage < 0.01 and mm_volume > 0:
                return ValidationResult(
                    True, ValidationSeverity.INFO,
                    f"MM contributes only {mm_percentage:.2%} of daily volume - "
                    f"minimal market impact"
                )
        
        return ValidationResult(
            True, ValidationSeverity.INFO,
            f"MM volume contribution ${mm_volume:,.0f} is valid"
        )

    def _validate_model_parameters(self, model_params: Dict[str, float]) -> List[ValidationResult]:
        """Validate specific model parameters"""
        results = []
        
        # Almgren-Chriss alpha parameter
        if 'alpha' in model_params:
            alpha = model_params['alpha']
            if not 0 <= alpha <= 1:
                results.append(ValidationResult(
                    False, ValidationSeverity.WARNING,
                    f"Almgren-Chriss alpha {alpha:.3f} outside typical range [0, 1]",
                    suggested_range=(0, 1)
                ))
        
        # Kyle's Lambda parameters
        if 'lambda_0' in model_params:
            lambda_0 = model_params['lambda_0']
            if lambda_0 <= 0:
                results.append(ValidationResult(
                    False, ValidationSeverity.ERROR,
                    "Kyle's lambda must be positive"
                ))
            elif lambda_0 > 0.1:
                results.append(ValidationResult(
                    False, ValidationSeverity.WARNING,
                    f"Kyle's lambda {lambda_0:.4f} seems high - may indicate very illiquid market"
                ))
        
        # Bouchaud power law parameters
        if 'delta' in model_params:
            delta = model_params['delta']
            if not 0.3 <= delta <= 0.8:
                results.append(ValidationResult(
                    False, ValidationSeverity.WARNING,
                    f"Bouchaud delta {delta:.2f} outside empirical range [0.3, 0.8]",
                    suggested_range=(0.3, 0.8)
                ))
        
        return results

    def validate_arbitrage_free_conditions(
        self,
        call_prices: List[float],
        put_prices: List[float], 
        strikes: List[float],
        spot_price: float,
        risk_free_rate: float,
        time_to_expiration: float
    ) -> ValidationSummary:
        """
        Validate arbitrage-free conditions for option chains
        """
        summary = ValidationSummary(True, [], [], [], 0)
        
        if not (len(call_prices) == len(put_prices) == len(strikes)):
            summary.add_result(ValidationResult(
                False, ValidationSeverity.ERROR,
                "Call prices, put prices, and strikes must have same length"
            ))
            return summary
        
        # 1. Put-Call Parity Check
        for i, (call, put, strike) in enumerate(zip(call_prices, put_prices, strikes)):
            result = self._check_put_call_parity(
                call, put, spot_price, strike, risk_free_rate, time_to_expiration, i
            )
            summary.add_result(result)
        
        # 2. Call Spread Arbitrage
        if len(strikes) > 1:
            sorted_indices = sorted(range(len(strikes)), key=lambda i: strikes[i])
            for i in range(len(sorted_indices) - 1):
                idx1, idx2 = sorted_indices[i], sorted_indices[i+1]
                result = self._check_call_spread_arbitrage(
                    call_prices[idx1], call_prices[idx2], strikes[idx1], strikes[idx2]
                )
                summary.add_result(result)
        
        # 3. Convexity Check for Calls
        if len(strikes) >= 3:
            result = self._check_call_convexity(call_prices, strikes)
            summary.add_result(result)
        
        return summary

    def _check_put_call_parity(
        self, call: float, put: float, spot: float, strike: float, 
        rate: float, time: float, index: int
    ) -> ValidationResult:
        """Check put-call parity: C - P = S - K*e^(-rT)"""
        pv_strike = strike * math.exp(-rate * time)
        theoretical_diff = spot - pv_strike
        actual_diff = call - put
        
        tolerance = max(0.01, 0.001 * spot)  # 1 cent or 0.1% of spot
        difference = abs(actual_diff - theoretical_diff)
        
        if difference > tolerance:
            return ValidationResult(
                False, ValidationSeverity.WARNING,
                f"Put-call parity violation at strike {strike}: "
                f"C-P = {actual_diff:.4f}, S-PV(K) = {theoretical_diff:.4f}, "
                f"difference = {difference:.4f}",
                suggested_range=None
            )
        
        return ValidationResult(
            True, ValidationSeverity.INFO,
            f"Put-call parity satisfied at strike {strike}"
        )

    def _check_call_spread_arbitrage(
        self, call_low: float, call_high: float, strike_low: float, strike_high: float
    ) -> ValidationResult:
        """Check call spread arbitrage: C(K1) >= C(K2) for K1 < K2"""
        if call_low < call_high:
            return ValidationResult(
                False, ValidationSeverity.ERROR,
                f"Call spread arbitrage: Call at {strike_low:.2f} ({call_low:.4f}) "
                f"should be >= call at {strike_high:.2f} ({call_high:.4f})"
            )
        
        return ValidationResult(
            True, ValidationSeverity.INFO,
            f"No call spread arbitrage between strikes {strike_low:.2f} and {strike_high:.2f}"
        )

    def _check_call_convexity(self, call_prices: List[float], strikes: List[float]) -> ValidationResult:
        """Check convexity condition for call options"""
        # For three consecutive strikes K1 < K2 < K3:
        # (C1 - C2)/(K2 - K1) >= (C2 - C3)/(K3 - K2)
        
        # Sort by strikes
        sorted_data = sorted(zip(strikes, call_prices))
        strikes_sorted = [x[0] for x in sorted_data]
        calls_sorted = [x[1] for x in sorted_data]
        
        violations = []
        for i in range(len(strikes_sorted) - 2):
            k1, k2, k3 = strikes_sorted[i:i+3]
            c1, c2, c3 = calls_sorted[i:i+3]
            
            if k2 - k1 > 0 and k3 - k2 > 0:  # Avoid division by zero
                slope1 = (c1 - c2) / (k2 - k1)
                slope2 = (c2 - c3) / (k3 - k2)
                
                if slope1 < slope2:
                    violations.append(f"Strikes {k1:.2f}-{k2:.2f}-{k3:.2f}")
        
        if violations:
            return ValidationResult(
                False, ValidationSeverity.WARNING,
                f"Convexity violations detected at: {', '.join(violations)}"
            )
        
        return ValidationResult(
            True, ValidationSeverity.INFO,
            "Call option convexity conditions satisfied"
        )

    def validate_extreme_scenarios(
        self,
        volatility: float,
        time_to_expiration: float,
        spot_price: float,
        scenario_type: str = "market_stress"
    ) -> ValidationSummary:
        """
        Validate parameters for extreme market scenarios
        """
        summary = ValidationSummary(True, [], [], [], 0)
        
        if scenario_type == "market_stress":
            # High volatility, potentially short time
            if volatility > 1.0 and time_to_expiration < 0.1:  # >100% vol, <1.2 months
                summary.add_result(ValidationResult(
                    True, ValidationSeverity.WARNING,
                    f"Extreme stress scenario: {volatility:.1%} volatility with "
                    f"{time_to_expiration*12:.1f} months to expiry - "
                    f"model predictions may be unreliable"
                ))
        
        elif scenario_type == "flash_crash":
            # Very high short-term volatility
            if volatility > 2.0 and time_to_expiration < 0.01:  # >200% vol, <4 days
                summary.add_result(ValidationResult(
                    True, ValidationSeverity.ERROR,
                    f"Flash crash scenario: {volatility:.1%} volatility with "
                    f"{time_to_expiration*365:.1f} days to expiry - "
                    f"Black-Scholes assumptions likely violated"
                ))
        
        elif scenario_type == "crypto_volatility":
            # Crypto-specific extreme scenarios
            if volatility > 5.0:  # >500% annual volatility
                summary.add_result(ValidationResult(
                    True, ValidationSeverity.WARNING,
                    f"Extreme crypto volatility: {volatility:.1%} - "
                    f"may reflect token collapse or manipulation"
                ))
        
        return summary


class ValidationFormatter:
    """Format validation results for user-friendly display"""
    
    @staticmethod
    def format_summary(summary: ValidationSummary) -> str:
        """Format validation summary as readable text"""
        output = []
        
        # Header
        status = "✅ PASSED" if summary.is_valid else "❌ FAILED"
        output.append(f"Validation Status: {status}")
        output.append(f"Total Checks: {summary.total_checks}")
        output.append(f"Errors: {len(summary.errors)}, Warnings: {len(summary.warnings)}, Info: {len(summary.infos)}")
        output.append("-" * 50)
        
        # Errors (highest priority)
        if summary.errors:
            output.append("🚨 ERRORS (Must Fix):")
            for i, error in enumerate(summary.errors, 1):
                output.append(f"  {i}. {error.message}")
                if error.suggested_range:
                    output.append(f"     Suggested range: {error.suggested_range}")
            output.append("")
        
        # Warnings
        if summary.warnings:
            output.append("⚠️  WARNINGS (Recommend Review):")
            for i, warning in enumerate(summary.warnings, 1):
                output.append(f"  {i}. {warning.message}")
                if warning.suggested_range:
                    output.append(f"     Suggested range: {warning.suggested_range}")
            output.append("")
        
        # Info (lowest priority, only show if requested)
        if summary.infos and len(summary.infos) <= 5:  # Don't overwhelm with info
            output.append("ℹ️  INFO:")
            for i, info in enumerate(summary.infos, 1):
                output.append(f"  {i}. {info.message}")
            output.append("")
        
        return "\n".join(output)

    @staticmethod
    def format_for_streamlit(summary: ValidationSummary) -> Dict[str, Any]:
        """Format validation results for Streamlit display"""
        return {
            'is_valid': summary.is_valid,
            'status_emoji': "✅" if summary.is_valid else "❌",
            'total_checks': summary.total_checks,
            'error_count': len(summary.errors),
            'warning_count': len(summary.warnings),
            'info_count': len(summary.infos),
            'errors': [{'message': r.message, 'suggested_range': r.suggested_range} for r in summary.errors],
            'warnings': [{'message': r.message, 'suggested_range': r.suggested_range} for r in summary.warnings],
            'infos': [{'message': r.message} for r in summary.infos]
        }


# Convenience functions for common validation tasks
def validate_basic_option_inputs(S: float, K: float, T: float, r: float, sigma: float, 
                               option_type: str = "call", 
                               market_type: MarketType = MarketType.CRYPTO,
                               asset_class: AssetClass = AssetClass.CRYPTO_MAJOR) -> ValidationSummary:
    """Quick validation for basic Black-Scholes inputs"""
    validator = FinancialValidator(market_type)
    return validator.validate_black_scholes_parameters(S, K, T, r, sigma, asset_class, option_type)


def validate_depth_inputs(spread_bps: float, depth_50: float, depth_100: float, 
                         depth_200: float, price: float, exchange: str = "Unknown",
                         market_type: MarketType = MarketType.CRYPTO) -> ValidationSummary:
    """Quick validation for market depth inputs"""
    validator = FinancialValidator(market_type)
    return validator.validate_depth_parameters(spread_bps, depth_50, depth_100, depth_200, price, exchange)


def validate_mm_inputs(daily_vol: float, price: float, vol: float, mm_vol: float,
                      market_type: MarketType = MarketType.CRYPTO) -> ValidationSummary:
    """Quick validation for market maker model inputs"""
    validator = FinancialValidator(market_type)
    return validator.validate_market_maker_parameters(daily_vol, price, vol, mm_vol)
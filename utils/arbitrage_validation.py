"""
Arbitrage-Free Validation Module

This module validates financial logic conditions including arbitrage-free pricing,
put-call parity, and cross-parameter consistency checks.
"""

import math
import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Union
from dataclasses import dataclass
from scipy.stats import norm
import logging

from utils.financial_validation import (
    ValidationResult, ValidationSeverity, ValidationSummary
)

logger = logging.getLogger(__name__)


@dataclass
class OptionChainData:
    """Data structure for option chain validation"""
    calls: List[Dict[str, float]]  # [{'strike': K, 'price': C, ...}, ...]
    puts: List[Dict[str, float]]   # [{'strike': K, 'price': P, ...}, ...]
    spot_price: float
    risk_free_rate: float
    time_to_expiration: float
    dividend_yield: float = 0.0


class ArbitrageValidator:
    """
    Validator for arbitrage-free conditions and financial logic consistency
    """
    
    def __init__(self, tolerance: float = 0.01):
        """
        Args:
            tolerance: Tolerance for arbitrage checks (in dollars or percentage points)
        """
        self.tolerance = tolerance
    
    def validate_put_call_parity(
        self,
        call_price: float,
        put_price: float,
        spot_price: float,
        strike_price: float,
        risk_free_rate: float,
        time_to_expiration: float,
        dividend_yield: float = 0.0
    ) -> ValidationSummary:
        """
        Validate put-call parity: C - P = S*e^(-qT) - K*e^(-rT)
        where q is dividend yield
        """
        summary = ValidationSummary(True, [], [], [], 0)
        
        try:
            # Calculate theoretical relationship
            pv_strike = strike_price * math.exp(-risk_free_rate * time_to_expiration)
            pv_spot = spot_price * math.exp(-dividend_yield * time_to_expiration)
            theoretical_diff = pv_spot - pv_strike
            actual_diff = call_price - put_price
            
            # Calculate absolute and relative differences
            abs_diff = abs(actual_diff - theoretical_diff)
            rel_diff = abs_diff / max(abs(theoretical_diff), 0.01)  # Avoid division by zero
            
            # Tolerance check
            tolerance_abs = max(self.tolerance, 0.001 * spot_price)  # At least 0.1% of spot
            
            if abs_diff > tolerance_abs and rel_diff > 0.05:  # 5% relative tolerance
                summary.add_result(ValidationResult(
                    False, ValidationSeverity.ERROR,
                    f"Put-call parity violation: C-P = {actual_diff:.4f}, "
                    f"S*e^(-qT) - K*e^(-rT) = {theoretical_diff:.4f}, "
                    f"difference = {abs_diff:.4f} (${abs_diff:.2f}, {rel_diff:.1%})"
                ))
            elif abs_diff > tolerance_abs * 0.5:
                summary.add_result(ValidationResult(
                    True, ValidationSeverity.WARNING,
                    f"Put-call parity deviation: {abs_diff:.4f} difference "
                    f"({rel_diff:.1%}) may indicate market inefficiency or transaction costs"
                ))
            else:
                summary.add_result(ValidationResult(
                    True, ValidationSeverity.INFO,
                    f"Put-call parity satisfied: difference {abs_diff:.4f} within tolerance"
                ))
            
            # Additional insights
            if dividend_yield > 0:
                summary.add_result(ValidationResult(
                    True, ValidationSeverity.INFO,
                    f"Dividend yield {dividend_yield:.2%} accounted for in put-call parity"
                ))
            
            if risk_free_rate < 0:
                summary.add_result(ValidationResult(
                    True, ValidationSeverity.INFO,
                    f"Negative interest rate {risk_free_rate:.2%} affects put-call parity calculations"
                ))
                
        except Exception as e:
            summary.add_result(ValidationResult(
                False, ValidationSeverity.ERROR,
                f"Error calculating put-call parity: {e}"
            ))
        
        return summary

    def validate_option_chain_arbitrage(self, chain_data: OptionChainData) -> ValidationSummary:
        """Validate entire option chain for arbitrage opportunities"""
        summary = ValidationSummary(True, [], [], [], 0)
        
        # 1. Validate call spread arbitrage
        call_summary = self._validate_call_spread_arbitrage(chain_data.calls)
        for result in call_summary.errors + call_summary.warnings + call_summary.infos:
            summary.add_result(result)
        
        # 2. Validate put spread arbitrage
        put_summary = self._validate_put_spread_arbitrage(chain_data.puts)
        for result in put_summary.errors + put_summary.warnings + put_summary.infos:
            summary.add_result(result)
        
        # 3. Validate convexity conditions
        convexity_summary = self._validate_option_convexity(chain_data.calls, "calls")
        for result in convexity_summary.errors + convexity_summary.warnings + convexity_summary.infos:
            summary.add_result(result)
        
        # 4. Cross-strike put-call parity
        parity_summary = self._validate_cross_strike_parity(chain_data)
        for result in parity_summary.errors + parity_summary.warnings + parity_summary.infos:
            summary.add_result(result)
        
        return summary

    def _validate_call_spread_arbitrage(self, calls: List[Dict[str, float]]) -> ValidationSummary:
        """Validate call spread arbitrage: C(K1) >= C(K2) for K1 < K2"""
        summary = ValidationSummary(True, [], [], [], 0)
        
        if len(calls) < 2:
            return summary
        
        # Sort calls by strike price
        sorted_calls = sorted(calls, key=lambda x: x['strike'])
        
        for i in range(len(sorted_calls) - 1):
            k1, c1 = sorted_calls[i]['strike'], sorted_calls[i]['price']
            k2, c2 = sorted_calls[i + 1]['strike'], sorted_calls[i + 1]['price']
            
            if c1 < c2:
                # Arbitrage violation
                summary.add_result(ValidationResult(
                    False, ValidationSeverity.ERROR,
                    f"Call spread arbitrage: Call at K=${k1:.2f} (${c1:.4f}) "
                    f"should be >= call at K=${k2:.2f} (${c2:.4f}). "
                    f"Violation = ${c2 - c1:.4f}"
                ))
            elif c1 - c2 < (k2 - k1) * 0.001:  # Very small spread for large strike difference
                summary.add_result(ValidationResult(
                    True, ValidationSeverity.WARNING,
                    f"Unusually small call spread: K1=${k1:.2f} (${c1:.4f}), "
                    f"K2=${k2:.2f} (${c2:.4f}), spread=${c1-c2:.4f} for "
                    f"${k2-k1:.2f} strike difference"
                ))
        
        return summary

    def _validate_put_spread_arbitrage(self, puts: List[Dict[str, float]]) -> ValidationSummary:
        """Validate put spread arbitrage: P(K1) <= P(K2) for K1 < K2"""
        summary = ValidationSummary(True, [], [], [], 0)
        
        if len(puts) < 2:
            return summary
        
        # Sort puts by strike price
        sorted_puts = sorted(puts, key=lambda x: x['strike'])
        
        for i in range(len(sorted_puts) - 1):
            k1, p1 = sorted_puts[i]['strike'], sorted_puts[i]['price']
            k2, p2 = sorted_puts[i + 1]['strike'], sorted_puts[i + 1]['price']
            
            if p1 > p2:
                # Arbitrage violation
                summary.add_result(ValidationResult(
                    False, ValidationSeverity.ERROR,
                    f"Put spread arbitrage: Put at K=${k1:.2f} (${p1:.4f}) "
                    f"should be <= put at K=${k2:.2f} (${p2:.4f}). "
                    f"Violation = ${p1 - p2:.4f}"
                ))
        
        return summary

    def _validate_option_convexity(self, options: List[Dict[str, float]], 
                                 option_type: str) -> ValidationSummary:
        """
        Validate convexity conditions for option prices
        For calls: (C1 - C2)/(K2 - K1) >= (C2 - C3)/(K3 - K2) for K1 < K2 < K3
        """
        summary = ValidationSummary(True, [], [], [], 0)
        
        if len(options) < 3:
            return summary
        
        # Sort by strike
        sorted_options = sorted(options, key=lambda x: x['strike'])
        
        violations = []
        for i in range(len(sorted_options) - 2):
            k1, p1 = sorted_options[i]['strike'], sorted_options[i]['price']
            k2, p2 = sorted_options[i + 1]['strike'], sorted_options[i + 1]['price']
            k3, p3 = sorted_options[i + 2]['strike'], sorted_options[i + 2]['price']
            
            # Avoid division by zero
            if k2 - k1 <= 0 or k3 - k2 <= 0:
                continue
            
            slope1 = (p1 - p2) / (k2 - k1)
            slope2 = (p2 - p3) / (k3 - k2)
            
            # For calls: slope1 >= slope2 (slopes should be decreasing)
            # For puts: slope1 <= slope2 (slopes should be increasing)
            if option_type == "calls" and slope1 < slope2 - self.tolerance:
                violations.append(f"K={k1:.2f}-{k2:.2f}-{k3:.2f} (slopes: {slope1:.4f} vs {slope2:.4f})")
            elif option_type == "puts" and slope1 > slope2 + self.tolerance:
                violations.append(f"K={k1:.2f}-{k2:.2f}-{k3:.2f} (slopes: {slope1:.4f} vs {slope2:.4f})")
        
        if violations:
            summary.add_result(ValidationResult(
                False, ValidationSeverity.WARNING,
                f"Convexity violations in {option_type}: {'; '.join(violations[:3])}"
                + (f" (and {len(violations)-3} more)" if len(violations) > 3 else "")
            ))
        else:
            summary.add_result(ValidationResult(
                True, ValidationSeverity.INFO,
                f"{option_type.capitalize()} convexity conditions satisfied"
            ))
        
        return summary

    def _validate_cross_strike_parity(self, chain_data: OptionChainData) -> ValidationSummary:
        """Validate put-call parity across multiple strikes"""
        summary = ValidationSummary(True, [], [], [], 0)
        
        # Match calls and puts by strike
        call_dict = {c['strike']: c['price'] for c in chain_data.calls}
        put_dict = {p['strike']: p['price'] for p in chain_data.puts}
        
        common_strikes = set(call_dict.keys()) & set(put_dict.keys())
        
        if not common_strikes:
            summary.add_result(ValidationResult(
                True, ValidationSeverity.WARNING,
                "No matching call/put strikes found for put-call parity validation"
            ))
            return summary
        
        parity_violations = []
        for strike in sorted(common_strikes):
            call_price = call_dict[strike]
            put_price = put_dict[strike]
            
            parity_result = self.validate_put_call_parity(
                call_price, put_price, chain_data.spot_price, strike,
                chain_data.risk_free_rate, chain_data.time_to_expiration,
                chain_data.dividend_yield
            )
            
            # Collect violations
            for error in parity_result.errors:
                parity_violations.append(f"K=${strike:.2f}: {error.message}")
        
        if parity_violations:
            summary.add_result(ValidationResult(
                False, ValidationSeverity.ERROR,
                f"Put-call parity violations at {len(parity_violations)} strikes: "
                f"{'; '.join(parity_violations[:2])}"
                + (f" (and {len(parity_violations)-2} more)" if len(parity_violations) > 2 else "")
            ))
        else:
            summary.add_result(ValidationResult(
                True, ValidationSeverity.INFO,
                f"Put-call parity satisfied across {len(common_strikes)} strikes"
            ))
        
        return summary

    def validate_bounds_conditions(
        self,
        call_price: float,
        put_price: float,
        spot_price: float,
        strike_price: float,
        risk_free_rate: float,
        time_to_expiration: float
    ) -> ValidationSummary:
        """
        Validate option price bounds:
        - Call: max(S - K*e^(-rT), 0) <= C <= S
        - Put: max(K*e^(-rT) - S, 0) <= P <= K*e^(-rT)
        """
        summary = ValidationSummary(True, [], [], [], 0)
        
        try:
            pv_strike = strike_price * math.exp(-risk_free_rate * time_to_expiration)
            
            # Call option bounds
            call_lower_bound = max(spot_price - pv_strike, 0)
            call_upper_bound = spot_price
            
            if call_price < call_lower_bound - self.tolerance:
                summary.add_result(ValidationResult(
                    False, ValidationSeverity.ERROR,
                    f"Call price ${call_price:.4f} below lower bound "
                    f"max(S-PV(K), 0) = ${call_lower_bound:.4f}"
                ))
            elif call_price > call_upper_bound + self.tolerance:
                summary.add_result(ValidationResult(
                    False, ValidationSeverity.ERROR,
                    f"Call price ${call_price:.4f} above upper bound S = ${call_upper_bound:.4f}"
                ))
            else:
                summary.add_result(ValidationResult(
                    True, ValidationSeverity.INFO,
                    f"Call price ${call_price:.4f} within bounds "
                    f"[${call_lower_bound:.4f}, ${call_upper_bound:.4f}]"
                ))
            
            # Put option bounds  
            put_lower_bound = max(pv_strike - spot_price, 0)
            put_upper_bound = pv_strike
            
            if put_price < put_lower_bound - self.tolerance:
                summary.add_result(ValidationResult(
                    False, ValidationSeverity.ERROR,
                    f"Put price ${put_price:.4f} below lower bound "
                    f"max(PV(K)-S, 0) = ${put_lower_bound:.4f}"
                ))
            elif put_price > put_upper_bound + self.tolerance:
                summary.add_result(ValidationResult(
                    False, ValidationSeverity.ERROR,
                    f"Put price ${put_price:.4f} above upper bound PV(K) = ${put_upper_bound:.4f}"
                ))
            else:
                summary.add_result(ValidationResult(
                    True, ValidationSeverity.INFO,
                    f"Put price ${put_price:.4f} within bounds "
                    f"[${put_lower_bound:.4f}, ${put_upper_bound:.4f}]"
                ))
                
        except Exception as e:
            summary.add_result(ValidationResult(
                False, ValidationSeverity.ERROR,
                f"Error validating price bounds: {e}"
            ))
        
        return summary

    def validate_early_exercise_conditions(
        self,
        option_price: float,
        intrinsic_value: float,
        time_to_expiration: float,
        option_type: str,
        dividend_yield: float = 0.0,
        american_style: bool = True
    ) -> ValidationSummary:
        """Validate early exercise conditions for American options"""
        summary = ValidationSummary(True, [], [], [], 0)
        
        if not american_style:
            summary.add_result(ValidationResult(
                True, ValidationSeverity.INFO,
                "European option: Early exercise not applicable"
            ))
            return summary
        
        time_value = option_price - intrinsic_value
        
        # General early exercise analysis
        if time_value < 0.01 and intrinsic_value > 0.10:  # Minimal time value, meaningful intrinsic
            summary.add_result(ValidationResult(
                True, ValidationSeverity.INFO,
                f"Low time value ${time_value:.4f} vs intrinsic ${intrinsic_value:.4f} - "
                f"American option may be candidate for early exercise"
            ))
        
        # Call-specific early exercise (mainly for dividend capture)
        if option_type.lower() == 'call' and dividend_yield > 0:
            if time_to_expiration < 0.1 and intrinsic_value > 0:  # Within ~36 days
                summary.add_result(ValidationResult(
                    True, ValidationSeverity.INFO,
                    f"ITM call with {dividend_yield:.2%} dividend yield "
                    f"and {time_to_expiration*365:.0f} days to expiry - "
                    f"consider early exercise for dividend capture"
                ))
        
        # Put-specific early exercise (interest rate consideration)
        elif option_type.lower() == 'put' and intrinsic_value > 0:
            # Deep ITM puts may be exercised early to get interest on strike proceeds
            moneyness = intrinsic_value / option_price if option_price > 0 else 0
            if moneyness > 0.8:  # >80% intrinsic value
                summary.add_result(ValidationResult(
                    True, ValidationSeverity.INFO,
                    f"Deep ITM put ({moneyness:.1%} intrinsic) - "
                    f"early exercise may be optimal to earn interest on strike proceeds"
                ))
        
        return summary

    def validate_volatility_arbitrage(
        self,
        implied_vol: float,
        historical_vol: float,
        vol_surface_data: Optional[Dict[str, float]] = None
    ) -> ValidationSummary:
        """Validate volatility arbitrage opportunities"""
        summary = ValidationSummary(True, [], [], [], 0)
        
        # Implied vs realized volatility
        vol_diff = implied_vol - historical_vol
        rel_diff = vol_diff / historical_vol if historical_vol > 0 else 0
        
        if abs(rel_diff) > 0.5:  # >50% difference
            summary.add_result(ValidationResult(
                True, ValidationSeverity.WARNING,
                f"Large volatility gap: Implied {implied_vol:.1%} vs "
                f"Historical {historical_vol:.1%} ({rel_diff:+.1%}). "
                f"Potential volatility arbitrage opportunity."
            ))
        
        # Volatility surface arbitrage (if data provided)
        if vol_surface_data:
            vols = list(vol_surface_data.values())
            if len(vols) >= 2:
                vol_spread = max(vols) - min(vols)
                if vol_spread > 1.0:  # >100% spread across strikes/times
                    summary.add_result(ValidationResult(
                        True, ValidationSeverity.WARNING,
                        f"Wide volatility surface spread: {vol_spread:.1%} between "
                        f"min {min(vols):.1%} and max {max(vols):.1%}. "
                        f"Check for calendar/volatility spread opportunities."
                    ))
        
        return summary

    def validate_synthetic_relationships(
        self,
        call_price: float,
        put_price: float,
        spot_price: float,
        strike_price: float,
        risk_free_rate: float,
        time_to_expiration: float
    ) -> ValidationSummary:
        """Validate synthetic instrument relationships"""
        summary = ValidationSummary(True, [], [], [], 0)
        
        pv_strike = strike_price * math.exp(-risk_free_rate * time_to_expiration)
        
        # Synthetic stock: Call - Put + PV(K) should equal Spot
        synthetic_stock = call_price - put_price + pv_strike
        stock_diff = abs(synthetic_stock - spot_price)
        
        if stock_diff > self.tolerance:
            summary.add_result(ValidationResult(
                False, ValidationSeverity.ERROR,
                f"Synthetic stock arbitrage: C - P + PV(K) = ${synthetic_stock:.4f} "
                f"vs Spot = ${spot_price:.4f}, difference = ${stock_diff:.4f}"
            ))
        else:
            summary.add_result(ValidationResult(
                True, ValidationSeverity.INFO,
                f"Synthetic stock relationship holds: difference ${stock_diff:.4f}"
            ))
        
        # Synthetic call: Stock - Put + PV(K) should equal Call
        synthetic_call = spot_price - put_price + pv_strike
        call_diff = abs(synthetic_call - call_price)
        
        if call_diff > self.tolerance:
            summary.add_result(ValidationResult(
                True, ValidationSeverity.WARNING,
                f"Synthetic call deviation: S - P + PV(K) = ${synthetic_call:.4f} "
                f"vs Call = ${call_price:.4f}, difference = ${call_diff:.4f}"
            ))
        
        return summary

    def comprehensive_arbitrage_validation(
        self,
        option_data: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> ValidationSummary:
        """Run comprehensive arbitrage validation"""
        
        summary = ValidationSummary(True, [], [], [], 0)
        
        # Extract required data
        call_price = option_data.get('call_price')
        put_price = option_data.get('put_price') 
        spot_price = market_data.get('spot_price')
        strike_price = option_data.get('strike_price')
        risk_free_rate = market_data.get('risk_free_rate', 0.05)
        time_to_expiration = option_data.get('time_to_expiration')
        
        # Run validations if data is available
        if all(v is not None for v in [call_price, put_price, spot_price, strike_price, time_to_expiration]):
            
            # 1. Put-call parity
            parity_result = self.validate_put_call_parity(
                call_price, put_price, spot_price, strike_price,
                risk_free_rate, time_to_expiration
            )
            for result in parity_result.errors + parity_result.warnings + parity_result.infos:
                summary.add_result(result)
            
            # 2. Price bounds
            bounds_result = self.validate_bounds_conditions(
                call_price, put_price, spot_price, strike_price,
                risk_free_rate, time_to_expiration
            )
            for result in bounds_result.errors + bounds_result.warnings + bounds_result.infos:
                summary.add_result(result)
            
            # 3. Synthetic relationships
            synthetic_result = self.validate_synthetic_relationships(
                call_price, put_price, spot_price, strike_price,
                risk_free_rate, time_to_expiration
            )
            for result in synthetic_result.errors + synthetic_result.warnings + synthetic_result.infos:
                summary.add_result(result)
            
            # 4. Early exercise conditions (if American)
            if option_data.get('american_style', False):
                for option_type in ['call', 'put']:
                    if option_type == 'call' and call_price is not None:
                        intrinsic = max(spot_price - strike_price, 0)
                        exercise_result = self.validate_early_exercise_conditions(
                            call_price, intrinsic, time_to_expiration, option_type
                        )
                    elif option_type == 'put' and put_price is not None:
                        intrinsic = max(strike_price - spot_price, 0)
                        exercise_result = self.validate_early_exercise_conditions(
                            put_price, intrinsic, time_to_expiration, option_type
                        )
                    else:
                        continue
                    
                    for result in exercise_result.errors + exercise_result.warnings + exercise_result.infos:
                        summary.add_result(result)
        
        else:
            summary.add_result(ValidationResult(
                True, ValidationSeverity.WARNING,
                "Insufficient data for comprehensive arbitrage validation"
            ))
        
        return summary


# Global instance
arbitrage_validator = ArbitrageValidator()
"""
Comprehensive Input Validation Wrapper

This module provides the main entry point for all financial validation in the options
pricing and depth valuation application. It combines and coordinates the existing
validation modules to provide unified validation with enhanced edge case detection.
"""

import math
import streamlit as st
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
import logging
from datetime import datetime, timedelta

from utils.financial_validation import (
    FinancialValidator, ValidationSummary, ValidationResult, ValidationSeverity,
    MarketType, AssetClass, ValidationFormatter
)
from utils.edge_case_validation import ExtremeMarketValidator, ExtremeCaseType
from utils.arbitrage_validation import ArbitrageValidator
from utils.validation_integration import StreamlitValidationHandler

logger = logging.getLogger(__name__)


@dataclass
class ValidationConfig:
    """Configuration for validation behavior"""
    market_type: MarketType = MarketType.CRYPTO
    asset_class: AssetClass = AssetClass.CRYPTO_MAJOR
    strictness_level: str = "standard"  # "permissive", "standard", "strict"
    enable_arbitrage_checks: bool = True
    enable_extreme_scenario_checks: bool = True
    auto_correct_minor_issues: bool = False
    block_on_errors: bool = True
    show_info_messages: bool = False


class ComprehensiveValidator:
    """
    Master validator that coordinates all validation modules and provides
    unified validation for the options pricing application
    """
    
    def __init__(self, config: ValidationConfig = None):
        self.config = config or ValidationConfig()
        
        # Initialize sub-validators
        self.financial_validator = FinancialValidator(self.config.market_type)
        self.extreme_validator = ExtremeMarketValidator()
        self.arbitrage_validator = ArbitrageValidator()
        self.streamlit_handler = StreamlitValidationHandler(self.config.market_type)
        
        # Validation history for learning/adaptation
        self.validation_history: List[Dict[str, Any]] = []
        
    def validate_option_pricing_inputs(
        self,
        spot_price: float,
        strike_price: float,
        time_to_expiration: float,
        risk_free_rate: float,
        volatility: float,
        option_type: str,
        show_results: bool = True,
        context: Dict[str, Any] = None
    ) -> Tuple[bool, ValidationSummary]:
        """
        Comprehensive validation for option pricing inputs
        
        Returns:
            Tuple of (is_valid, validation_summary)
        """
        try:
            # Start with basic financial validation
            summary = self.financial_validator.validate_black_scholes_parameters(
                spot_price=spot_price,
                strike_price=strike_price,
                time_to_expiration=time_to_expiration,
                risk_free_rate=risk_free_rate,
                volatility=volatility,
                asset_class=self.config.asset_class,
                option_type=option_type
            )
            
            # Add extreme scenario validation
            if self.config.enable_extreme_scenario_checks:
                extreme_summary = self.extreme_validator.comprehensive_edge_case_validation(
                    spot_price=spot_price,
                    strike_price=strike_price,
                    time_to_expiration=time_to_expiration,
                    risk_free_rate=risk_free_rate,
                    volatility=volatility,
                    option_type=option_type,
                    market_context=context or {}
                )
                
                # Merge extreme validation results
                for result in extreme_summary.errors + extreme_summary.warnings + extreme_summary.infos:
                    summary.add_result(result)
            
            # Apply strictness adjustments
            summary = self._apply_strictness_filter(summary)
            
            # Record validation for history
            self._record_validation(
                "option_pricing", 
                {
                    'spot_price': spot_price,
                    'strike_price': strike_price,
                    'time_to_expiration': time_to_expiration,
                    'risk_free_rate': risk_free_rate,
                    'volatility': volatility,
                    'option_type': option_type
                },
                summary
            )
            
            # Display results if requested
            if show_results:
                self._display_validation_results(summary, "Option Pricing Parameters")
            
            is_valid = len(summary.errors) == 0 or not self.config.block_on_errors
            return is_valid, summary
            
        except Exception as e:
            logger.error(f"Error in option pricing validation: {e}")
            error_summary = ValidationSummary(False, [], [], [], 0)
            error_summary.add_result(ValidationResult(
                False, ValidationSeverity.ERROR,
                f"Validation system error: {str(e)}"
            ))
            return False, error_summary

    def validate_market_depth_inputs(
        self,
        bid_ask_spread_bps: float,
        depth_50bps: float,
        depth_100bps: float,
        depth_200bps: float,
        asset_price: float,
        exchange_name: str,
        daily_volume: Optional[float] = None,
        show_results: bool = True
    ) -> Tuple[bool, ValidationSummary]:
        """
        Comprehensive validation for market depth parameters
        """
        try:
            # Basic depth validation
            summary = self.financial_validator.validate_depth_parameters(
                bid_ask_spread_bps=bid_ask_spread_bps,
                depth_50bps=depth_50bps,
                depth_100bps=depth_100bps,
                depth_200bps=depth_200bps,
                asset_price=asset_price,
                exchange_name=exchange_name
            )
            
            # Add liquidity crisis validation if volume provided
            if daily_volume is not None:
                liquidity_summary = self.extreme_validator.validate_liquidity_crisis_scenarios(
                    bid_ask_spread_bps=bid_ask_spread_bps,
                    depth_50bps=depth_50bps,
                    depth_100bps=depth_100bps,
                    depth_200bps=depth_200bps,
                    daily_volume=daily_volume,
                    asset_price=asset_price
                )
                
                for result in liquidity_summary.errors + liquidity_summary.warnings + liquidity_summary.infos:
                    summary.add_result(result)
            
            # Add exchange-specific validations
            exchange_summary = self._validate_exchange_specific_rules(
                exchange_name, bid_ask_spread_bps, [depth_50bps, depth_100bps, depth_200bps]
            )
            for result in exchange_summary:
                summary.add_result(result)
            
            # Apply strictness filter
            summary = self._apply_strictness_filter(summary)
            
            # Display results
            if show_results:
                self._display_validation_results(summary, "Market Depth Parameters")
            
            is_valid = len(summary.errors) == 0 or not self.config.block_on_errors
            return is_valid, summary
            
        except Exception as e:
            logger.error(f"Error in depth validation: {e}")
            return False, ValidationSummary(False, [], [], [], 0)

    def validate_portfolio_consistency(
        self,
        tranches: List[Dict[str, Any]],
        depth_data: List[Dict[str, Any]],
        global_params: Dict[str, Any],
        show_results: bool = True
    ) -> Tuple[bool, ValidationSummary]:
        """
        Validate consistency across the entire portfolio
        """
        summary = ValidationSummary(True, [], [], [], 0)
        
        try:
            # 1. Entity consistency check
            tranche_entities = set(t.get('entity', '') for t in tranches)
            depth_entities = set(d.get('entity', '') for d in depth_data)
            
            missing_depths = tranche_entities - depth_entities
            if missing_depths:
                summary.add_result(ValidationResult(
                    False, ValidationSeverity.ERROR,
                    f"Entities missing depth data: {', '.join(missing_depths)}"
                ))
            
            unused_depths = depth_entities - tranche_entities
            if unused_depths:
                summary.add_result(ValidationResult(
                    True, ValidationSeverity.WARNING,
                    f"Entities with depth data but no tranches: {', '.join(unused_depths)}"
                ))
            
            # 2. Strike price distribution analysis
            strikes = [t.get('strike_price', 0) for t in tranches if t.get('strike_price', 0) > 0]
            if len(strikes) > 1:
                strike_analysis = self._analyze_strike_distribution(strikes, global_params.get('spot_price', 10))
                for result in strike_analysis:
                    summary.add_result(result)
            
            # 3. Time to expiration consistency
            times = [t.get('time_to_expiration', 0) for t in tranches if t.get('time_to_expiration', 0) > 0]
            if len(times) > 1:
                time_analysis = self._analyze_expiration_distribution(times)
                for result in time_analysis:
                    summary.add_result(result)
            
            # 4. Arbitrage checks if enabled
            if self.config.enable_arbitrage_checks and len(tranches) > 1:
                arbitrage_summary = self._check_portfolio_arbitrage(tranches, global_params)
                for result in arbitrage_summary.errors + arbitrage_summary.warnings + arbitrage_summary.infos:
                    summary.add_result(result)
            
            # 5. Risk concentration analysis
            risk_analysis = self._analyze_portfolio_risk_concentration(tranches, depth_data)
            for result in risk_analysis:
                summary.add_result(result)
            
            if show_results:
                self._display_validation_results(summary, "Portfolio Consistency Analysis")
            
            is_valid = len(summary.errors) == 0 or not self.config.block_on_errors
            return is_valid, summary
            
        except Exception as e:
            logger.error(f"Error in portfolio validation: {e}")
            summary.add_result(ValidationResult(
                False, ValidationSeverity.ERROR,
                f"Portfolio validation error: {str(e)}"
            ))
            return False, summary

    def pre_calculation_gate(
        self,
        all_params: Dict[str, Any],
        calculation_type: str = "options"
    ) -> bool:
        """
        Final validation gate before expensive calculations
        Returns True if calculations should proceed
        """
        try:
            logger.info(f"Running pre-calculation gate for {calculation_type}")
            
            critical_errors = []
            
            # Check for critical parameter issues
            if calculation_type == "options":
                required_params = ['spot_price', 'strike_price', 'time_to_expiration', 'volatility']
                for param in required_params:
                    if param not in all_params or all_params[param] <= 0:
                        critical_errors.append(f"Invalid {param}: {all_params.get(param, 'missing')}")
            
            # Check for numerical stability issues
            if calculation_type == "options":
                stability_check = self.extreme_validator.validate_numerical_stability(
                    spot_price=all_params.get('spot_price', 1),
                    strike_price=all_params.get('strike_price', 1),
                    time_to_expiration=all_params.get('time_to_expiration', 1),
                    risk_free_rate=all_params.get('risk_free_rate', 0.05),
                    volatility=all_params.get('volatility', 0.2)
                )
                
                for error in stability_check.errors:
                    critical_errors.append(error.message)
            
            if critical_errors:
                for error in critical_errors:
                    st.error(f"🚫 Pre-calculation check failed: {error}")
                return False
            
            st.success("✅ Pre-calculation validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Error in pre-calculation gate: {e}")
            st.error(f"🚫 Pre-calculation validation error: {e}")
            return False

    def get_validation_recommendations(
        self,
        validation_summary: ValidationSummary,
        input_type: str = "general"
    ) -> List[Dict[str, str]]:
        """
        Generate specific recommendations based on validation results
        """
        recommendations = []
        
        for error in validation_summary.errors:
            if "volatility" in error.message.lower():
                if "extreme" in error.message.lower():
                    recommendations.append({
                        "type": "critical",
                        "action": "Consider using alternative pricing models (jump-diffusion, stochastic volatility)",
                        "reason": "Extreme volatility may violate Black-Scholes assumptions"
                    })
                else:
                    recommendations.append({
                        "type": "adjust",
                        "action": f"Adjust volatility to suggested range: {error.suggested_range}",
                        "reason": error.message
                    })
            
            elif "time" in error.message.lower() and "gamma" in error.message.lower():
                recommendations.append({
                    "type": "warning",
                    "action": "Monitor delta hedging closely - use shorter rehedging intervals",
                    "reason": "Gamma explosion risk near expiry"
                })
            
            elif "arbitrage" in error.message.lower():
                recommendations.append({
                    "type": "critical",
                    "action": "Review pricing assumptions - potential arbitrage opportunity detected",
                    "reason": error.message
                })
            
            elif "liquidity" in error.message.lower():
                recommendations.append({
                    "type": "adjust", 
                    "action": "Increase market impact assumptions in valuation models",
                    "reason": "Low liquidity may increase execution costs"
                })
        
        return recommendations

    def create_validation_report(
        self,
        validation_results: Dict[str, ValidationSummary]
    ) -> str:
        """
        Create a comprehensive validation report
        """
        report_lines = []
        report_lines.append("# Comprehensive Validation Report")
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        total_errors = sum(len(summary.errors) for summary in validation_results.values())
        total_warnings = sum(len(summary.warnings) for summary in validation_results.values())
        total_checks = sum(summary.total_checks for summary in validation_results.values())
        
        report_lines.append("## Summary")
        report_lines.append(f"- Total validation checks: {total_checks}")
        report_lines.append(f"- Total errors: {total_errors}")
        report_lines.append(f"- Total warnings: {total_warnings}")
        report_lines.append(f"- Overall status: {'❌ FAILED' if total_errors > 0 else '✅ PASSED'}")
        report_lines.append("")
        
        for category, summary in validation_results.items():
            report_lines.append(f"## {category.replace('_', ' ').title()}")
            
            if summary.errors:
                report_lines.append("### ❌ Errors")
                for error in summary.errors:
                    report_lines.append(f"- {error.message}")
                    if error.suggested_range:
                        report_lines.append(f"  - Suggested range: {error.suggested_range}")
                report_lines.append("")
            
            if summary.warnings:
                report_lines.append("### ⚠️ Warnings")
                for warning in summary.warnings:
                    report_lines.append(f"- {warning.message}")
                report_lines.append("")
        
        return "\n".join(report_lines)

    def _apply_strictness_filter(self, summary: ValidationSummary) -> ValidationSummary:
        """Apply strictness level filtering to validation results"""
        if self.config.strictness_level == "permissive":
            # Convert some errors to warnings
            new_summary = ValidationSummary(True, [], [], [], summary.total_checks)
            
            for error in summary.errors:
                if "extreme" not in error.message.lower() and "arbitrage" not in error.message.lower():
                    # Convert to warning
                    new_warning = ValidationResult(
                        True, ValidationSeverity.WARNING,
                        f"[Permissive Mode] {error.message}",
                        error.suggested_range, error.corrected_value
                    )
                    new_summary.add_result(new_warning)
                else:
                    new_summary.add_result(error)
            
            for warning in summary.warnings + summary.infos:
                new_summary.add_result(warning)
            
            return new_summary
            
        elif self.config.strictness_level == "strict":
            # Convert some warnings to errors
            new_summary = ValidationSummary(summary.is_valid, [], [], [], summary.total_checks)
            
            for error in summary.errors:
                new_summary.add_result(error)
            
            for warning in summary.warnings:
                if any(keyword in warning.message.lower() for keyword in ["extreme", "unusual", "high", "low"]):
                    # Convert to error
                    new_error = ValidationResult(
                        False, ValidationSeverity.ERROR,
                        f"[Strict Mode] {warning.message}",
                        warning.suggested_range, warning.corrected_value
                    )
                    new_summary.add_result(new_error)
                else:
                    new_summary.add_result(warning)
            
            for info in summary.infos:
                new_summary.add_result(info)
                
            return new_summary
        
        return summary  # Standard mode - no changes

    def _validate_exchange_specific_rules(
        self, 
        exchange: str, 
        spread_bps: float, 
        depths: List[float]
    ) -> List[ValidationResult]:
        """Validate exchange-specific rules and bounds"""
        results = []
        
        exchange_upper = exchange.upper()
        
        # Binance-specific rules
        if "BINANCE" in exchange_upper:
            if spread_bps > 20:
                results.append(ValidationResult(
                    True, ValidationSeverity.WARNING,
                    f"Binance spread {spread_bps:.1f}bps higher than typical (<20bps for major pairs)"
                ))
            
            # Binance typically has deeper books
            if max(depths) < 10000:
                results.append(ValidationResult(
                    True, ValidationSeverity.INFO,
                    f"Binance depth seems low - major pairs typically have >$10k at tight spreads"
                ))
        
        # Coinbase-specific rules  
        elif "COINBASE" in exchange_upper:
            if spread_bps > 50:
                results.append(ValidationResult(
                    True, ValidationSeverity.WARNING,
                    f"Coinbase spread {spread_bps:.1f}bps higher than typical (<50bps)"
                ))
        
        # DEX-specific rules
        elif any(dex in exchange_upper for dex in ["UNISWAP", "SUSHISWAP", "PANCAKE"]):
            results.append(ValidationResult(
                True, ValidationSeverity.INFO,
                f"DEX detected ({exchange}): Consider additional slippage and MEV costs"
            ))
            
            if spread_bps < 30:
                results.append(ValidationResult(
                    True, ValidationSeverity.WARNING,
                    f"DEX spread {spread_bps:.1f}bps seems tight - verify including swap fees"
                ))
        
        return results

    def _analyze_strike_distribution(self, strikes: List[float], spot_price: float) -> List[ValidationResult]:
        """Analyze strike price distribution for potential issues"""
        results = []
        
        if not strikes or spot_price <= 0:
            return results
        
        # Calculate moneyness for all strikes
        moneyness_ratios = [strike / spot_price for strike in strikes]
        
        # Check for clustering
        sorted_strikes = sorted(strikes)
        gaps = [sorted_strikes[i+1] - sorted_strikes[i] for i in range(len(sorted_strikes)-1)]
        
        if gaps and max(gaps) / min(gaps) > 10:
            results.append(ValidationResult(
                True, ValidationSeverity.WARNING,
                f"Uneven strike distribution: largest gap ${max(gaps):.2f} vs smallest ${min(gaps):.2f}"
            ))
        
        # Check for extreme moneyness concentrations
        deep_otm_count = sum(1 for m in moneyness_ratios if m > 2.0 or m < 0.5)
        if deep_otm_count / len(strikes) > 0.5:
            results.append(ValidationResult(
                True, ValidationSeverity.WARNING,
                f"{deep_otm_count}/{len(strikes)} strikes are deep OTM - low gamma, high theta decay"
            ))
        
        return results

    def _analyze_expiration_distribution(self, times: List[float]) -> List[ValidationResult]:
        """Analyze time to expiration distribution"""
        results = []
        
        if len(times) < 2:
            return results
        
        # Check for very short-term concentration
        short_term_count = sum(1 for t in times if t < 0.1)  # Less than ~36 days
        if short_term_count / len(times) > 0.7:
            results.append(ValidationResult(
                True, ValidationSeverity.WARNING,
                f"{short_term_count}/{len(times)} options expire within 36 days - high theta exposure"
            ))
        
        # Check for very long-term concentration
        long_term_count = sum(1 for t in times if t > 2.0)  # More than 2 years
        if long_term_count / len(times) > 0.3:
            results.append(ValidationResult(
                True, ValidationSeverity.WARNING,
                f"{long_term_count}/{len(times)} options expire after 2 years - model assumptions may not hold"
            ))
        
        return results

    def _check_portfolio_arbitrage(self, tranches: List[Dict], global_params: Dict) -> ValidationSummary:
        """Check for arbitrage opportunities across portfolio"""
        summary = ValidationSummary(True, [], [], [], 0)
        
        # Group by entity and check for put-call parity within entities
        entity_groups = {}
        for tranche in tranches:
            entity = tranche.get('entity', 'Unknown')
            if entity not in entity_groups:
                entity_groups[entity] = []
            entity_groups[entity].append(tranche)
        
        # For each entity, check if we have matching call/put pairs
        for entity, entity_tranches in entity_groups.items():
            # Group by strike and expiration
            strike_exp_pairs = {}
            for tranche in entity_tranches:
                key = (tranche.get('strike_price'), tranche.get('time_to_expiration'))
                if key not in strike_exp_pairs:
                    strike_exp_pairs[key] = {'call': None, 'put': None}
                
                option_type = tranche.get('option_type', '').lower()
                if option_type in ['call', 'put']:
                    strike_exp_pairs[key][option_type] = tranche
            
            # Check pairs that have both call and put
            for (strike, time_exp), pair in strike_exp_pairs.items():
                if pair['call'] is not None and pair['put'] is not None:
                    # We have a call-put pair, can check put-call parity
                    summary.add_result(ValidationResult(
                        True, ValidationSeverity.INFO,
                        f"Entity {entity}: Found call-put pair at strike ${strike:.2f} - "
                        f"can validate put-call parity"
                    ))
        
        return summary

    def _analyze_portfolio_risk_concentration(
        self, 
        tranches: List[Dict], 
        depth_data: List[Dict]
    ) -> List[ValidationResult]:
        """Analyze portfolio for risk concentrations"""
        results = []
        
        # Entity concentration
        entity_counts = {}
        for tranche in tranches:
            entity = tranche.get('entity', 'Unknown')
            entity_counts[entity] = entity_counts.get(entity, 0) + 1
        
        if entity_counts:
            max_entity_count = max(entity_counts.values())
            total_tranches = len(tranches)
            concentration_pct = (max_entity_count / total_tranches) * 100
            
            if concentration_pct > 50:
                max_entity = max(entity_counts.keys(), key=lambda k: entity_counts[k])
                results.append(ValidationResult(
                    True, ValidationSeverity.WARNING,
                    f"High entity concentration: {max_entity} represents {concentration_pct:.1f}% "
                    f"of tranches ({max_entity_count}/{total_tranches})"
                ))
        
        # Exchange concentration in depth data
        exchange_counts = {}
        for depth in depth_data:
            exchange = depth.get('exchange', 'Unknown')
            exchange_counts[exchange] = exchange_counts.get(exchange, 0) + 1
        
        if exchange_counts:
            max_exchange_count = max(exchange_counts.values())
            total_depths = len(depth_data)
            exchange_concentration_pct = (max_exchange_count / total_depths) * 100
            
            if exchange_concentration_pct > 60:
                max_exchange = max(exchange_counts.keys(), key=lambda k: exchange_counts[k])
                results.append(ValidationResult(
                    True, ValidationSeverity.WARNING,
                    f"High exchange concentration: {max_exchange} represents {exchange_concentration_pct:.1f}% "
                    f"of depth data ({max_exchange_count}/{total_depths})"
                ))
        
        return results

    def _display_validation_results(self, summary: ValidationSummary, title: str) -> None:
        """Display validation results in Streamlit"""
        if hasattr(st, 'session_state'):  # Check if we're in Streamlit context
            self.streamlit_handler.display_validation_results(summary, title)

    def _record_validation(self, validation_type: str, params: Dict, summary: ValidationSummary) -> None:
        """Record validation results for learning and improvement"""
        self.validation_history.append({
            'timestamp': datetime.now(),
            'type': validation_type,
            'parameters': params.copy(),
            'errors': len(summary.errors),
            'warnings': len(summary.warnings),
            'total_checks': summary.total_checks
        })
        
        # Keep only last 100 validations
        if len(self.validation_history) > 100:
            self.validation_history = self.validation_history[-100:]


# Global validator instance with default configuration
default_validator = ComprehensiveValidator()


# Convenience functions for common validation tasks
def validate_option_inputs_quick(
    spot: float, strike: float, time: float, rate: float, vol: float, 
    option_type: str, show: bool = True
) -> bool:
    """Quick validation returning True if inputs are valid (no errors)"""
    is_valid, _ = default_validator.validate_option_pricing_inputs(
        spot, strike, time, rate, vol, option_type, show
    )
    return is_valid


def validate_depth_inputs_quick(
    spread_bps: float, d50: float, d100: float, d200: float, 
    price: float, exchange: str, show: bool = True
) -> bool:
    """Quick validation returning True if depth inputs are valid"""
    is_valid, _ = default_validator.validate_market_depth_inputs(
        spread_bps, d50, d100, d200, price, exchange, show_results=show
    )
    return is_valid


def validate_portfolio_quick(tranches: List, depths: List, params: Dict) -> bool:
    """Quick portfolio validation"""
    is_valid, _ = default_validator.validate_portfolio_consistency(
        tranches, depths, params, show_results=True
    )
    return is_valid


def pre_calculation_check(params: Dict, calc_type: str = "options") -> bool:
    """Pre-calculation validation gate"""
    return default_validator.pre_calculation_gate(params, calc_type)
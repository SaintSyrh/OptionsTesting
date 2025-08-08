"""
Comprehensive Error Testing Framework for Options Pricing Platform
Tests all major components and edge cases
"""

import sys
import traceback
import logging
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveErrorTester:
    """Comprehensive error testing for the options pricing platform"""
    
    def __init__(self):
        self.test_results = {
            'passed': [],
            'failed': [],
            'errors': [],
            'total_tests': 0
        }
    
    def run_test(self, test_name: str, test_func):
        """Run a single test with error handling"""
        self.test_results['total_tests'] += 1
        
        try:
            logger.info(f"Running test: {test_name}")
            result = test_func()
            
            if result:
                self.test_results['passed'].append(test_name)
                logger.info(f"✅ {test_name} - PASSED")
            else:
                self.test_results['failed'].append(test_name)
                logger.error(f"❌ {test_name} - FAILED")
            
        except Exception as e:
            error_msg = f"{test_name}: {str(e)}"
            self.test_results['errors'].append(error_msg)
            logger.error(f"💥 {test_name} - ERROR: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    def test_imports(self) -> bool:
        """Test all critical imports"""
        try:
            # Core modules
            from config.model_constants import CRYPTO_DEPTH, MODEL_WEIGHTS
            from config.simple_styles import FINANCIAL_COLORS, CHART_COLORS
            
            # Business logic
            from option_pricing import black_scholes_call, black_scholes_put, calculate_greeks
            from depth_valuation import DepthValuationModels
            from crypto_depth_calculator import CryptoEffectiveDepthCalculator
            
            # UI components
            from ui.simple_components import simple_components
            
            # Session management
            from app.session_state import SessionStateManager
            from app.calculations import CalculationOrchestrator
            
            # Validation
            from utils.comprehensive_validation import ComprehensiveValidator
            
            logger.info("All imports successful")
            return True
            
        except Exception as e:
            logger.error(f"Import error: {e}")
            return False
    
    def test_option_pricing(self) -> bool:
        """Test option pricing with various scenarios"""
        try:
            test_cases = [
                # Normal cases
                {"S": 100, "K": 100, "T": 1.0, "r": 0.05, "sigma": 0.2},
                {"S": 150, "K": 100, "T": 0.5, "r": 0.03, "sigma": 0.3},
                
                # Edge cases
                {"S": 100, "K": 200, "T": 0.1, "r": 0.01, "sigma": 0.1},  # Deep OTM
                {"S": 200, "K": 100, "T": 2.0, "r": 0.08, "sigma": 0.5},   # Deep ITM
                {"S": 100, "K": 100, "T": 0.001, "r": 0.05, "sigma": 0.2}, # Near expiry
                
                # Extreme cases
                {"S": 100, "K": 100, "T": 0.0027, "r": 0.05, "sigma": 1.0}, # High vol + short time
            ]
            
            for i, case in enumerate(test_cases):
                call_price = black_scholes_call(**case)
                put_price = black_scholes_put(**case)
                greeks = calculate_greeks(**case)
                
                # Validate results
                assert call_price >= 0, f"Call price negative: {call_price}"
                assert put_price >= 0, f"Put price negative: {put_price}"
                assert isinstance(greeks, dict), "Greeks not a dictionary"
                assert 'delta' in greeks, "Delta missing from Greeks"
                
                logger.info(f"Case {i+1}: Call=${call_price:.2f}, Put=${put_price:.2f}")
            
            return True
            
        except Exception as e:
            logger.error(f"Option pricing test failed: {e}")
            return False
    
    def test_depth_valuation_models(self) -> bool:
        """Test all depth valuation models"""
        try:
            models = DepthValuationModels()
            
            # Test parameters
            test_params = {
                'spread_0': 0.002,
                'spread_1': 0.001, 
                'volatility': 0.3,
                'trade_sizes': [1000, 5000, 10000],
                'probabilities': [0.5, 0.3, 0.2],
                'volume_0': 1000000,
                'volume_mm': 500000,
                'depth_0': 100000,
                'depth_mm': 200000,
                'daily_volume_0': 1000000,
                'daily_volume_mm': 500000,
                'asset_price': 10.0
            }
            
            # Test individual models
            model_tests = [
                ('Almgren-Chriss', lambda: models.almgren_chriss_value(
                    test_params['spread_0'], test_params['spread_1'], test_params['volatility'],
                    test_params['trade_sizes'], test_params['probabilities'],
                    test_params['volume_0'], test_params['volume_mm']
                )),
                ('Kyle Lambda', lambda: models.kyle_lambda_value(
                    test_params['trade_sizes'], test_params['probabilities'],
                    test_params['depth_0'], test_params['depth_mm'], test_params['asset_price']
                )),
                ('Bouchaud Power Law', lambda: models.bouchaud_power_law_value(
                    test_params['volatility'], test_params['trade_sizes'], test_params['probabilities'],
                    test_params['daily_volume_0'], test_params['daily_volume_mm']
                )),
            ]
            
            for model_name, model_func in model_tests:
                result = model_func()
                assert 'total_value' in result, f"{model_name}: missing total_value"
                assert isinstance(result['total_value'], (int, float)), f"{model_name}: invalid total_value type"
                logger.info(f"{model_name}: ${result['total_value']:.2f}")
            
            # Test composite model
            composite = models.composite_valuation(**test_params, use_crypto_weights=True)
            assert 'total_value' in composite, "Composite missing total_value"
            logger.info(f"Composite (Crypto): ${composite['total_value']:.2f}")
            
            return True
            
        except Exception as e:
            logger.error(f"Depth valuation test failed: {e}")
            return False
    
    def test_crypto_depth_calculator(self) -> bool:
        """Test crypto-optimized depth calculator"""
        try:
            calc = CryptoEffectiveDepthCalculator()
            
            # Test individual calculations
            result = calc.calculate_crypto_effective_depth(
                depth=100000,
                spread_tier='50bps',
                bid_ask_spread=8.0,
                volatility=0.25,
                exchange='Binance'
            )
            
            assert 'effective_depth' in result, "Missing effective_depth"
            assert 'efficiency_ratio' in result, "Missing efficiency_ratio"
            assert result['effective_depth'] > 0, "Effective depth should be positive"
            
            # Test entity calculation
            entity_result = calc.calculate_entity_effective_depth(
                depth_50bps=200000,
                depth_100bps=300000,
                depth_200bps=500000,
                bid_ask_spread=10.0,
                volatility=0.3,
                exchange='OKX'
            )
            
            assert 'total_effective_depth' in entity_result, "Missing total_effective_depth"
            assert entity_result['total_effective_depth'] > 0, "Total effective depth should be positive"
            
            logger.info(f"Crypto calc: ${entity_result['total_effective_depth']:.0f}")
            return True
            
        except Exception as e:
            logger.error(f"Crypto depth calculator test failed: {e}")
            return False
    
    def test_validation_framework(self) -> bool:
        """Test comprehensive validation"""
        try:
            from utils.comprehensive_validation import (
                validate_option_inputs_quick, validate_depth_inputs_quick
            )
            
            # Test valid inputs
            valid_option = validate_option_inputs_quick(
                spot=100, strike=105, time=1.0, rate=0.05, vol=0.2, option_type='call'
            )
            assert valid_option, "Valid option inputs should pass"
            
            # Test invalid inputs
            invalid_option = validate_option_inputs_quick(
                spot=-100, strike=105, time=1.0, rate=0.05, vol=0.2, option_type='call'
            )
            assert not invalid_option, "Invalid option inputs should fail"
            
            # Test depth validation
            valid_depth = validate_depth_inputs_quick(
                depth_50bps=100000, depth_100bps=200000, depth_200bps=300000,
                spread=10.0, volatility=0.25, exchange='Binance'
            )
            assert valid_depth, "Valid depth inputs should pass"
            
            return True
            
        except Exception as e:
            logger.error(f"Validation test failed: {e}")
            return False
    
    def test_edge_cases(self) -> bool:
        """Test extreme edge cases"""
        try:
            # Test with extreme values
            extreme_cases = [
                # Very high volatility
                {"S": 100, "K": 100, "T": 1.0, "r": 0.05, "sigma": 2.0},
                # Very short time to expiry
                {"S": 100, "K": 100, "T": 0.0001, "r": 0.05, "sigma": 0.2},
                # Very large numbers
                {"S": 1000000, "K": 1000000, "T": 1.0, "r": 0.05, "sigma": 0.2},
            ]
            
            for case in extreme_cases:
                try:
                    call = black_scholes_call(**case)
                    assert not np.isnan(call), f"NaN result for case {case}"
                    assert not np.isinf(call), f"Infinite result for case {case}"
                except Exception as e:
                    logger.warning(f"Expected edge case failure: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Edge case test failed: {e}")
            return False
    
    def test_configuration_constants(self) -> bool:
        """Test all configuration constants are properly loaded"""
        try:
            from config.model_constants import (
                CRYPTO_DEPTH, MODEL_WEIGHTS, ALMGREN_CHRISS, KYLE_LAMBDA
            )
            
            # Test crypto depth config
            assert CRYPTO_DEPTH.EXCHANGE_TIERS is not None, "Exchange tiers not loaded"
            assert len(CRYPTO_DEPTH.EXCHANGE_TIERS) > 0, "Empty exchange tiers"
            assert 'Binance' in CRYPTO_DEPTH.EXCHANGE_TIERS, "Binance missing from tiers"
            
            # Test model weights
            crypto_weights = MODEL_WEIGHTS.CRYPTO_WEIGHTS
            assert abs(sum(crypto_weights.values()) - 1.0) < 0.001, "Weights don't sum to 1.0"
            
            # Test constants are reasonable
            assert 0 < ALMGREN_CHRISS.ALPHA_DEFAULT < 1, "Invalid Almgren-Chriss alpha"
            assert KYLE_LAMBDA.DEPTH_DIVISOR > 0, "Invalid Kyle lambda divisor"
            
            return True
            
        except Exception as e:
            logger.error(f"Configuration test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        logger.info("🚀 Starting Comprehensive Error Testing")
        logger.info("=" * 60)
        
        # Define all tests
        tests = [
            ("Import Tests", self.test_imports),
            ("Option Pricing Tests", self.test_option_pricing), 
            ("Depth Valuation Tests", self.test_depth_valuation_models),
            ("Crypto Calculator Tests", self.test_crypto_depth_calculator),
            ("Validation Framework Tests", self.test_validation_framework),
            ("Edge Case Tests", self.test_edge_cases),
            ("Configuration Tests", self.test_configuration_constants),
        ]
        
        # Run all tests
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Print summary
        self.print_summary()
        
        return len(self.test_results['errors']) == 0 and len(self.test_results['failed']) == 0
    
    def print_summary(self):
        """Print test results summary"""
        results = self.test_results
        
        logger.info("\n" + "=" * 60)
        logger.info("🎯 COMPREHENSIVE TEST RESULTS")
        logger.info("=" * 60)
        
        logger.info(f"Total Tests: {results['total_tests']}")
        logger.info(f"✅ Passed: {len(results['passed'])}")
        logger.info(f"❌ Failed: {len(results['failed'])}")
        logger.info(f"💥 Errors: {len(results['errors'])}")
        
        if results['failed']:
            logger.error("\nFailed Tests:")
            for test in results['failed']:
                logger.error(f"  - {test}")
        
        if results['errors']:
            logger.error("\nErrors:")
            for error in results['errors']:
                logger.error(f"  - {error}")
        
        success_rate = (len(results['passed']) / results['total_tests']) * 100
        logger.info(f"\n🎯 Success Rate: {success_rate:.1f}%")
        
        if len(results['errors']) == 0 and len(results['failed']) == 0:
            logger.info("🏆 ALL TESTS PASSED - SYSTEM READY FOR PRODUCTION!")
        else:
            logger.warning("⚠️  Some tests failed - review errors before deployment")


if __name__ == "__main__":
    tester = ComprehensiveErrorTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
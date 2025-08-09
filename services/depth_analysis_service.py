"""
Service for handling the complex depth analysis functionality.
Breaks down the large phase_3_depth_analysis function into manageable components.
"""

from typing import Dict, List, Any, Tuple, Optional
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime

from models.data_models import MarketDepth, EffectiveDepthResult, MarketMakerValuation, EntitySummary
from services.calculation_service import CalculationOrchestrator
from config.constants import UI, MARKET_MAKER, SUCCESS, ERRORS
from utils.error_handling import (
    error_handler, DepthDataValidator, display_validation_results,
    with_error_boundary
)


class DepthDataManager:
    """Manages depth data input and validation"""
    
    def __init__(self):
        self.validator = DepthDataValidator()
    
    @with_error_boundary("Depth Data Input")
    def render_depth_input_form(self, entities: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Render the depth data input form"""
        with st.form("depth_setup"):
            col1, col2 = st.columns(2)
            
            with col1:
                entity_names = [e['name'] for e in entities]
                entity = st.selectbox("Entity", entity_names)
                exchange = st.selectbox("Exchange", ["Binance", "OKX", "Coinbase", "Other"])
            
            with col2:
                spread = st.number_input("Bid-Ask Spread (bps)", value=10.0, key="depth_spread")
            
            col3, col4, col5 = st.columns(3)
            with col3:
                depth_50 = st.number_input("Depth @ 50bps ($)", value=100000.0, key="depth_50bps")
            with col4:
                depth_100 = st.number_input("Depth @ 100bps ($)", value=200000.0, key="depth_100bps")
            with col5:
                depth_200 = st.number_input("Depth @ 200bps ($)", value=300000.0, key="depth_200bps")
            
            if st.form_submit_button("Add Depth Data"):
                depth_data = {
                    'entity': entity,
                    'exchange': exchange,
                    'spread': spread,
                    'depth_50': depth_50,
                    'depth_100': depth_100,
                    'depth_200': depth_200
                }
                
                # Validate the data
                validation_errors = self.validator.validate_depth(depth_data)
                if display_validation_results(validation_errors):
                    return depth_data
        
        return None
    
    @with_error_boundary("Depth Data Display")
    def render_depth_data_table(self, depths_data: List[Dict[str, Any]]) -> bool:
        """
        Render the depth data table with remove functionality
        
        Returns:
            True if any data was removed (requiring a rerun)
        """
        if not depths_data:
            return False
        
        st.markdown("### Current Depth Data")
        
        # Headers
        col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 1, 1, 1, 1, 1, 1])
        with col1:
            st.write("**Entity**")
        with col2:
            st.write("**Exchange**")
        with col3:
            st.write("**Spread**")
        with col4:
            st.write("**50bps**")
        with col5:
            st.write("**100bps**")
        with col6:
            st.write("**200bps**")
        with col7:
            st.write("**Remove**")
        st.markdown("---")
        
        # Data rows
        for i, depth in enumerate(depths_data):
            col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 1, 1, 1, 1, 1, 1])
            with col1:
                st.write(f"**{depth['entity']}**")
            with col2:
                st.write(f"{depth['exchange']}")
            with col3:
                st.write(f"{depth['spread']:.0f}bps")
            with col4:
                st.write(f"${depth['depth_50']/1000:.0f}k")
            with col5:
                st.write(f"${depth['depth_100']/1000:.0f}k")
            with col6:
                st.write(f"${depth['depth_200']/1000:.0f}k")
            with col7:
                if st.button("❌", key=f"remove_depth_{i}", help="Remove depth data"):
                    depths_data.pop(i)
                    return True
        
        return False


class EffectiveDepthCalculator:
    """Handles effective depth calculations and display"""
    
    def __init__(self):
        self.orchestrator = CalculationOrchestrator()
    
    @error_handler(context="Effective Depth Calculation")
    def calculate_and_display_effective_depths(self, depths_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate and display effective depths
        
        Returns:
            Dictionary mapping entity to effective depth
        """
        if not depths_data:
            st.warning("No depth data available")
            return {}
        
        # Calculate effective depths using the service
        entity_depths = self.orchestrator.depth_service.calculate_cumulative_depths_by_entity(
            [MarketDepth(**depth) for depth in depths_data]
        )
        
        # Prepare data for display
        individual_results = []
        cumulative_results = []
        total_raw = 0
        total_effective = 0
        
        for depth_data in depths_data:
            depth = MarketDepth(**depth_data)
            result = self.orchestrator.depth_service.calculate_entity_effective_depth(depth)
            
            individual_results.append({
                'Entity': result.entity,
                'Exchange': result.exchange,
                'Raw Depth': f"${result.total_raw_depth:,.0f}",
                'Effective Depth': f"${result.total_effective_depth:,.0f}",
                'Efficiency': f"{result.efficiency_percentage:.1f}%"
            })
        
        # Show individual results
        st.markdown("### Individual Exchange Results")
        st.dataframe(pd.DataFrame(individual_results), use_container_width=True)
        
        # Show cumulative results by entity
        st.markdown("### Cumulative Effective Depths by Entity")
        for entity, totals in entity_depths.items():
            total_raw += totals['raw_depth']
            total_effective += totals['effective_depth']
            
            cumulative_results.append({
                'Entity': entity,
                'Exchanges': ', '.join(set(totals['exchanges'])),
                'Total Raw Depth': f"${totals['raw_depth']:,.0f}",
                'Total Effective Depth': f"${totals['effective_depth']:,.0f}",
                'Overall Efficiency': f"{totals['overall_efficiency']:.1%}"
            })
        
        # Add grand total
        grand_efficiency = total_effective / total_raw if total_raw > 0 else 0
        cumulative_results.append({
            'Entity': '**TOTAL**',
            'Exchanges': 'All',
            'Total Raw Depth': f"**${total_raw:,.0f}**",
            'Total Effective Depth': f"**${total_effective:,.0f}**",
            'Overall Efficiency': f"**{grand_efficiency:.1%}**"
        })
        
        st.dataframe(pd.DataFrame(cumulative_results), use_container_width=True)
        
        # Return effective depths for use by other components
        return {entity: data['effective_depth'] for entity, data in entity_depths.items()}


class MarketMakerValuationCalculator:
    """Handles market maker valuation calculations and display"""
    
    def __init__(self):
        self.orchestrator = CalculationOrchestrator()
    
    @error_handler(context="Market Maker Valuation")
    def calculate_and_display_mm_valuation(
        self,
        depths_data: List[Dict[str, Any]],
        tranches_data: List[Dict[str, Any]],
        market_params: Dict[str, float],
        effective_depths: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Calculate and display market maker valuation
        
        Returns:
            Dictionary with calculation results
        """
        if not depths_data or not tranches_data:
            st.warning("Need both depth data and option configurations")
            return {}
        
        try:
            # Use the calculation orchestrator for comprehensive analysis
            from models.data_models import MarketParameters
            
            params = MarketParameters(
                total_valuation=market_params['total_valuation'],
                total_tokens=market_params.get('total_tokens', 100000),
                volatility=market_params['volatility'],
                risk_free_rate=market_params['risk_free_rate']
            )
            
            # Get entities list (assuming it exists in the session state)
            entities = st.session_state.get('entities_data', [])
            
            results = self.orchestrator.calculate_comprehensive_analysis(
                entities, tranches_data, depths_data, params
            )
            
            if 'error' in results:
                st.error(f"Calculation failed: {results['error']}")
                return {}
            
            # Display results
            self._display_mm_results(results, effective_depths)
            self._display_charts(results['entity_summaries'])
            
            return results
            
        except Exception as e:
            st.error(f"Market Maker valuation failed: {str(e)}")
            return {}
    
    def _display_mm_results(self, results: Dict[str, Any], effective_depths: Dict[str, float]):
        """Display market maker calculation results"""
        st.success(f"Total Market Maker Value: ${results['total_mm_value']:,.2f}")
        
        # Display entity summary table
        st.markdown("### Market Maker Value by Entity")
        
        if results['entity_summaries']:
            summary_data = []
            for summary in results['entity_summaries']:
                summary_data.append({
                    'Entity': summary.entity,
                    'Exchanges': ', '.join(summary.exchanges),
                    'Model Value': f"${summary.total_mm_value:,.2f}",
                    'Spread Cost': f"${summary.total_spread_cost:,.2f}",
                    'Net MM Value': f"${summary.total_net_value:,.2f}",
                    'Option Value': f"${summary.option_value:,.2f}",
                    'MM Efficiency': f"{summary.mm_efficiency:.1f}%",
                    'Effective Depth': f"${summary.effective_depth:,.0f}",
                    'Depth Coverage': f"{summary.depth_coverage:.1f}x",
                    'Risk Score': summary.risk_score,
                    'Risk Level': summary.risk_level
                })
            
            st.dataframe(pd.DataFrame(summary_data), use_container_width=True)
        
        # Add explanation
        st.info("""
        **Model Value**: Advanced market microstructure models (Almgren-Chriss, Kyle Lambda, etc.)  
        **Spread Cost**: Adverse selection losses from being picked off by informed traders  
        **Net MM Value**: Model value minus adverse selection costs - the real MM profitability  
        **MM Efficiency**: Net MM value as % of option value (higher = better returns after costs)  
        **Depth Coverage**: How many times effective depth covers option value (higher = lower risk)  
        **Risk Score**: 1 = Low Risk (≥10x coverage), 2 = Medium Risk (5-10x), 3 = High Risk (2-5x), 4 = Very High Risk (<2x)
        """)
    
    def _display_charts(self, entity_summaries: List[EntitySummary]):
        """Display analytical charts"""
        if not entity_summaries:
            return
        
        st.markdown("### Visual Analytics")
        
        try:
            # Chart 1: Market Maker Value by Entity
            self._create_mm_value_chart(entity_summaries)
            
            # Chart 2: MM Efficiency Comparison
            self._create_efficiency_chart(entity_summaries)
            
        except Exception as e:
            st.error(f"Error creating charts: {str(e)}")
    
    def _create_mm_value_chart(self, summaries: List[EntitySummary]):
        """Create market maker value chart"""
        fig, ax = plt.subplots(figsize=(UI.CHART_WIDTH, UI.CHART_HEIGHT))
        
        entities = [s.entity for s in summaries]
        model_values = [s.total_mm_value for s in summaries]
        spread_costs = [s.total_spread_cost for s in summaries]
        net_values = [s.total_net_value for s in summaries]
        
        # Create stacked bar chart
        bars1 = ax.bar(entities, model_values, color=UI.MODEL_VALUE_COLOR, label='Model Value')
        bars2 = ax.bar(entities, [-cost for cost in spread_costs], 
                      bottom=model_values, color=UI.SPREAD_COST_COLOR, label='Spread Cost (Loss)')
        
        # Add value labels
        for i, net_val in enumerate(net_values):
            y_pos = max(net_values) + max(model_values)*0.01 if net_val >= 0 else net_val - max(model_values)*0.01
            ax.text(i, y_pos, f'${net_val:,.0f}', ha='center', 
                   va='bottom' if net_val >= 0 else 'top', fontweight='bold')
        
        ax.legend()
        ax.set_title('Market Maker Net Value by Entity\n(Model Value minus Adverse Selection Costs)', 
                    fontweight='bold', fontsize=14)
        ax.set_xlabel('Entities', fontweight='bold')
        ax.set_ylabel('Market Maker Value ($)', fontweight='bold')
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        ax.grid(axis='y', alpha=0.3)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    def _create_efficiency_chart(self, summaries: List[EntitySummary]):
        """Create MM efficiency chart"""
        fig, ax = plt.subplots(figsize=(UI.CHART_WIDTH, UI.CHART_HEIGHT))
        
        entities = [s.entity for s in summaries]
        efficiencies = [s.mm_efficiency for s in summaries]
        
        bars = ax.bar(entities, efficiencies, 
                     color=UI.CHART_COLORS[:len(entities)])
        
        # Add value labels
        for i, (bar, eff) in enumerate(zip(bars, efficiencies)):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(efficiencies)*0.01,
                   f'{eff:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        ax.set_title('MM Efficiency by Entity\n(Market Maker Value as % of Option Value)', 
                    fontweight='bold', fontsize=14)
        ax.set_xlabel('Entities', fontweight='bold')
        ax.set_ylabel('MM Efficiency (%)', fontweight='bold')
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.1f}%'))
        ax.grid(axis='y', alpha=0.3)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()


class DepthAnalysisOrchestrator:
    """Main orchestrator for the depth analysis phase"""
    
    def __init__(self):
        self.data_manager = DepthDataManager()
        self.depth_calculator = EffectiveDepthCalculator()
        self.mm_calculator = MarketMakerValuationCalculator()
    
    def run_depth_analysis_phase(
        self,
        entities_data: List[Dict[str, Any]],
        tranches_data: List[Dict[str, Any]],
        depths_data: List[Dict[str, Any]],
        market_params: Dict[str, float]
    ) -> bool:
        """
        Run the complete depth analysis phase
        
        Returns:
            True if a rerun is needed (due to data changes)
        """
        st.markdown("## Phase 3: Market Depth Analysis")
        
        if not tranches_data:
            st.warning("Configure options first!")
            if st.button("Back to Phase 2"):
                st.session_state.current_phase = 2
                st.rerun()
            return False
        
        # Handle depth data input
        new_depth_data = self.data_manager.render_depth_input_form(entities_data)
        if new_depth_data:
            depths_data.append(new_depth_data)
            st.success(f"Added depth data for {new_depth_data['entity']}")
            return True
        
        # Display current depth data
        if self.data_manager.render_depth_data_table(depths_data):
            return True
        
        if depths_data:
            st.markdown("---")
            
            # Effective depth calculation
            if st.button("Calculate Effective Depths"):
                effective_depths = self.depth_calculator.calculate_and_display_effective_depths(depths_data)
                # Store in session state for use by MM calculation
                st.session_state['effective_depths'] = effective_depths
            
            # Market maker valuation
            if st.button("Run Market Maker Valuation"):
                effective_depths = st.session_state.get('effective_depths', {})
                results = self.mm_calculator.calculate_and_display_mm_valuation(
                    depths_data, tranches_data, market_params, effective_depths
                )
                if results:
                    st.session_state['calculation_results'] = results
        
        return False
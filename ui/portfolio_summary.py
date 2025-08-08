"""
Professional Portfolio Summary Components
Bloomberg/TradingView-inspired portfolio analytics and summary displays
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging

from ui.professional_components import professional_components
from ui.professional_charts import professional_charts
from ui.dashboard_layout import dashboard_layout
from config.styles import ICONS, FINANCIAL_COLORS
from config.settings import COLORS

logger = logging.getLogger(__name__)


class PortfolioSummary:
    """Professional portfolio summary and analytics components"""
    
    def __init__(self):
        self.components = professional_components
        self.charts = professional_charts
        self.dashboard = dashboard_layout
        self.icons = ICONS
        self.colors = FINANCIAL_COLORS
    
    def create_portfolio_overview(
        self, 
        portfolio_data: Dict[str, Any],
        show_charts: bool = True
    ) -> None:
        """Create comprehensive portfolio overview dashboard"""
        try:
            if not portfolio_data:
                st.info("📊 Configure entities and tranches to see portfolio overview")
                return
            
            # Header
            st.markdown("## 📊 Portfolio Overview")
            
            # Key metrics cards
            self._create_key_metrics_cards(portfolio_data)
            
            # Charts section
            if show_charts:
                self._create_portfolio_charts(portfolio_data)
            
            # Detailed breakdown
            self._create_portfolio_breakdown(portfolio_data)
            
        except Exception as e:
            logger.error(f"Error creating portfolio overview: {e}")
            st.error("Error creating portfolio overview")
    
    def _create_key_metrics_cards(self, portfolio_data: Dict[str, Any]) -> None:
        """Create key portfolio metrics cards"""
        try:
            metrics_data = []
            
            # Total Portfolio Value
            total_value = portfolio_data.get('total_portfolio_value', 0)
            prev_value = portfolio_data.get('prev_total_value', total_value)
            value_change = ((total_value - prev_value) / prev_value * 100) if prev_value > 0 else 0
            
            metrics_data.append({
                'title': 'Total Portfolio Value',
                'value': f"${total_value:,.0f}",
                'change': f"{'+' if value_change >= 0 else ''}{value_change:.2f}%",
                'change_type': 'positive' if value_change >= 0 else 'negative',
                'icon': self.icons['portfolio'],
                'description': 'Current portfolio valuation'
            })
            
            # Active Entities
            active_entities = portfolio_data.get('active_entities', 0)
            metrics_data.append({
                'title': 'Active Entities',
                'value': str(active_entities),
                'icon': self.icons['entity'],
                'description': 'Configured entities'
            })
            
            # Total Options
            total_options = portfolio_data.get('total_options', 0)
            metrics_data.append({
                'title': 'Total Options',
                'value': str(total_options),
                'icon': self.icons['tranche'],
                'description': 'Options tranches'
            })
            
            # Average Strike
            avg_strike = portfolio_data.get('average_strike_price', 0)
            metrics_data.append({
                'title': 'Average Strike',
                'value': f"${avg_strike:.2f}",
                'icon': self.icons['analytics'],
                'description': 'Weighted average strike price'
            })
            
            # Risk Metrics
            portfolio_risk = portfolio_data.get('portfolio_risk', 0)
            risk_change = portfolio_data.get('risk_change', 0)
            
            metrics_data.append({
                'title': 'Portfolio Risk',
                'value': f"{portfolio_risk:.1f}%",
                'change': f"{'+' if risk_change >= 0 else ''}{risk_change:.1f}%",
                'change_type': 'warning' if portfolio_risk > 30 else 'success',
                'icon': self.icons['risk'],
                'description': 'Risk exposure level'
            })
            
            # Volatility
            avg_volatility = portfolio_data.get('average_volatility', 0)
            metrics_data.append({
                'title': 'Average Volatility',
                'value': f"{avg_volatility*100:.1f}%",
                'icon': '📈',
                'description': 'Portfolio volatility'
            })
            
            # Time to Expiration
            avg_time_to_exp = portfolio_data.get('average_time_to_expiration', 0)
            metrics_data.append({
                'title': 'Avg Time to Exp',
                'value': f"{avg_time_to_exp:.2f}y",
                'icon': '⏰',
                'description': 'Average time to expiration'
            })
            
            # Market Depth Coverage
            depth_coverage = portfolio_data.get('depth_coverage', 0)
            metrics_data.append({
                'title': 'Depth Coverage',
                'value': f"{depth_coverage:.1f}%",
                'change_type': 'success' if depth_coverage > 80 else 'warning' if depth_coverage > 60 else 'error',
                'icon': self.icons['depth'],
                'description': 'Market depth adequacy'
            })
            
            # Create metrics grid
            self.dashboard.create_metrics_grid(metrics_data, columns=4)
            
        except Exception as e:
            logger.error(f"Error creating key metrics cards: {e}")
            st.error("Error creating portfolio metrics")
    
    def _create_portfolio_charts(self, portfolio_data: Dict[str, Any]) -> None:
        """Create portfolio analysis charts"""
        try:
            st.markdown("### 📈 Portfolio Analytics")
            
            # Create chart columns
            col1, col2 = st.columns(2)
            
            with col1:
                # Portfolio composition by entity
                if 'entity_breakdown' in portfolio_data:
                    composition_chart = self.charts.create_portfolio_composition_chart(
                        portfolio_data['entity_breakdown'],
                        chart_type="donut"
                    )
                    if composition_chart:
                        st.plotly_chart(composition_chart, use_container_width=True)
                
                # Greeks breakdown
                if 'greeks_summary' in portfolio_data:
                    greeks_chart = self.charts.create_greeks_dashboard(
                        portfolio_data['greeks_summary']
                    )
                    if greeks_chart:
                        st.plotly_chart(greeks_chart, use_container_width=True)
            
            with col2:
                # Option type breakdown
                if 'option_type_breakdown' in portfolio_data:
                    fig = self.charts.create_portfolio_composition_chart(
                        portfolio_data['option_type_breakdown'],
                        chart_type="treemap"
                    )
                    if fig:
                        fig.update_layout(title="Options by Type")
                        st.plotly_chart(fig, use_container_width=True)
                
                # Risk metrics heatmap
                if 'risk_matrix' in portfolio_data:
                    risk_df = pd.DataFrame(portfolio_data['risk_matrix'])
                    if not risk_df.empty:
                        heatmap_chart = self.charts.create_risk_metrics_heatmap(risk_df)
                        if heatmap_chart:
                            st.plotly_chart(heatmap_chart, use_container_width=True)
            
            # Full-width payoff diagram
            if 'payoff_data' in portfolio_data:
                st.markdown("#### Portfolio Payoff Analysis")
                payoff_chart = self.charts.create_options_payoff_diagram(
                    portfolio_data['payoff_data']
                )
                if payoff_chart:
                    st.plotly_chart(payoff_chart, use_container_width=True)
                    
        except Exception as e:
            logger.error(f"Error creating portfolio charts: {e}")
            st.error("Error creating portfolio charts")
    
    def _create_portfolio_breakdown(self, portfolio_data: Dict[str, Any]) -> None:
        """Create detailed portfolio breakdown tables"""
        try:
            st.markdown("### 📋 Portfolio Breakdown")
            
            # Entity breakdown table
            if 'entities' in portfolio_data and portfolio_data['entities']:
                entity_data = []
                
                for entity_name, entity_info in portfolio_data['entities'].items():
                    entity_data.append({
                        'Entity': entity_name,
                        'Options Count': entity_info.get('options_count', 0),
                        'Total Value ($)': f"${entity_info.get('total_value', 0):,.0f}",
                        'Avg Strike ($)': f"${entity_info.get('avg_strike', 0):.2f}",
                        'Total Delta': f"{entity_info.get('total_delta', 0):.3f}",
                        'Total Gamma': f"{entity_info.get('total_gamma', 0):.4f}",
                        'Total Theta': f"{entity_info.get('total_theta', 0):.3f}",
                        'Total Vega': f"{entity_info.get('total_vega', 0):.2f}",
                        'Risk Level': f"{entity_info.get('risk_level', 0):.1f}%"
                    })
                
                if entity_data:
                    entity_df = pd.DataFrame(entity_data)
                    self.dashboard.create_data_table_enhanced(
                        entity_df,
                        "Entity Summary",
                        self.icons['entity']
                    )
            
            # Options breakdown table
            if 'options_details' in portfolio_data and portfolio_data['options_details']:
                options_df = pd.DataFrame(portfolio_data['options_details'])
                
                # Format columns
                format_columns = {
                    'option_value': 'currency',
                    'strike_price': 'currency',
                    'delta': 'decimal',
                    'gamma': 'decimal',
                    'theta': 'decimal',
                    'vega': 'decimal'
                }
                
                self.dashboard.create_data_table_enhanced(
                    options_df,
                    "Options Details",
                    self.icons['tranche'],
                    format_columns=format_columns
                )
            
            # Market depth summary
            if 'depth_summary' in portfolio_data and portfolio_data['depth_summary']:
                depth_data = []
                
                for entity_name, depth_info in portfolio_data['depth_summary'].items():
                    depth_data.append({
                        'Entity': entity_name,
                        'Exchanges': depth_info.get('exchanges_count', 0),
                        'Total Depth ($)': f"${depth_info.get('total_depth', 0):,.0f}",
                        'Effective Depth ($)': f"${depth_info.get('effective_depth', 0):,.0f}",
                        'Depth Efficiency (%)': f"{depth_info.get('efficiency', 0):.1f}%",
                        'Coverage Ratio': f"{depth_info.get('coverage_ratio', 0):.2f}x",
                        'Risk Adjusted Depth ($)': f"${depth_info.get('risk_adjusted_depth', 0):,.0f}"
                    })
                
                if depth_data:
                    depth_df = pd.DataFrame(depth_data)
                    self.dashboard.create_data_table_enhanced(
                        depth_df,
                        "Market Depth Summary",
                        self.icons['depth']
                    )
                    
        except Exception as e:
            logger.error(f"Error creating portfolio breakdown: {e}")
            st.error("Error creating portfolio breakdown")
    
    def create_risk_dashboard(self, risk_data: Dict[str, Any]) -> None:
        """Create professional risk management dashboard"""
        try:
            if not risk_data:
                st.info("🎯 Risk analysis will appear here after calculations")
                return
            
            st.markdown("## 🎯 Risk Management Dashboard")
            
            # Risk metrics cards
            risk_metrics = []
            
            # VaR (Value at Risk)
            var_95 = risk_data.get('var_95', 0)
            var_99 = risk_data.get('var_99', 0)
            
            risk_metrics.extend([
                {
                    'title': 'VaR (95%)',
                    'value': f"${abs(var_95):,.0f}",
                    'change_type': 'error' if abs(var_95) > 50000 else 'warning' if abs(var_95) > 25000 else 'success',
                    'icon': '⚠️',
                    'description': '95% confidence Value at Risk'
                },
                {
                    'title': 'VaR (99%)',
                    'value': f"${abs(var_99):,.0f}",
                    'change_type': 'error' if abs(var_99) > 100000 else 'warning' if abs(var_99) > 50000 else 'success',
                    'icon': '🚨',
                    'description': '99% confidence Value at Risk'
                }
            ])
            
            # Portfolio Greeks risk
            delta_exposure = risk_data.get('delta_exposure', 0)
            gamma_risk = risk_data.get('gamma_risk', 0)
            
            risk_metrics.extend([
                {
                    'title': 'Delta Exposure',
                    'value': f"{delta_exposure:.3f}",
                    'change_type': 'warning' if abs(delta_exposure) > 0.5 else 'success',
                    'icon': 'Δ',
                    'description': 'Portfolio delta exposure'
                },
                {
                    'title': 'Gamma Risk',
                    'value': f"{gamma_risk:.4f}",
                    'change_type': 'warning' if gamma_risk > 0.1 else 'success',
                    'icon': 'Γ',
                    'description': 'Portfolio gamma risk'
                }
            ])
            
            self.dashboard.create_metrics_grid(risk_metrics, columns=4)
            
            # Risk charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Risk contribution by entity
                if 'risk_contribution' in risk_data:
                    risk_chart = self.charts.create_portfolio_composition_chart(
                        risk_data['risk_contribution'],
                        chart_type="donut"
                    )
                    if risk_chart:
                        risk_chart.update_layout(title="Risk Contribution by Entity")
                        st.plotly_chart(risk_chart, use_container_width=True)
            
            with col2:
                # Risk scenarios
                if 'scenario_analysis' in risk_data:
                    scenario_df = pd.DataFrame(risk_data['scenario_analysis'])
                    if not scenario_df.empty:
                        # Create scenario analysis chart
                        import plotly.graph_objects as go
                        
                        fig = go.Figure()
                        fig.add_trace(go.Bar(
                            x=scenario_df['Scenario'],
                            y=scenario_df['P&L'],
                            marker_color=[
                                self.colors['bullish'] if x >= 0 else self.colors['bearish'] 
                                for x in scenario_df['P&L']
                            ]
                        ))
                        
                        fig.update_layout(
                            title="Scenario Analysis",
                            xaxis_title="Market Scenarios",
                            yaxis_title="Profit/Loss ($)",
                            paper_bgcolor='#1E293B',
                            plot_bgcolor='#334155',
                            font=dict(color='#F8FAFC', family='Inter'),
                            height=400
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            logger.error(f"Error creating risk dashboard: {e}")
            st.error("Error creating risk dashboard")
    
    def create_performance_dashboard(self, performance_data: Dict[str, Any]) -> None:
        """Create professional performance tracking dashboard"""
        try:
            if not performance_data:
                st.info("🚀 Performance tracking will appear here after calculations")
                return
            
            st.markdown("## 🚀 Performance Dashboard")
            
            # Performance metrics
            perf_metrics = []
            
            total_pnl = performance_data.get('total_pnl', 0)
            pnl_change = performance_data.get('pnl_change', 0)
            
            perf_metrics.extend([
                {
                    'title': 'Total P&L',
                    'value': f"${total_pnl:,.0f}",
                    'change': f"{'+' if pnl_change >= 0 else ''}{pnl_change:,.0f}",
                    'change_type': 'positive' if total_pnl >= 0 else 'negative',
                    'icon': self.icons['performance'],
                    'description': 'Total profit/loss'
                },
                {
                    'title': 'Win Rate',
                    'value': f"{performance_data.get('win_rate', 0):.1f}%",
                    'change_type': 'success' if performance_data.get('win_rate', 0) > 60 else 'warning',
                    'icon': '🎯',
                    'description': 'Percentage of profitable trades'
                }
            ])
            
            # Sharpe ratio
            sharpe_ratio = performance_data.get('sharpe_ratio', 0)
            perf_metrics.append({
                'title': 'Sharpe Ratio',
                'value': f"{sharpe_ratio:.2f}",
                'change_type': 'success' if sharpe_ratio > 1.0 else 'warning' if sharpe_ratio > 0.5 else 'error',
                'icon': '📊',
                'description': 'Risk-adjusted return'
            })
            
            # Max drawdown
            max_drawdown = performance_data.get('max_drawdown', 0)
            perf_metrics.append({
                'title': 'Max Drawdown',
                'value': f"{max_drawdown:.1f}%",
                'change_type': 'success' if max_drawdown > -10 else 'warning' if max_drawdown > -20 else 'error',
                'icon': '📉',
                'description': 'Maximum peak-to-trough decline'
            })
            
            self.dashboard.create_metrics_grid(perf_metrics, columns=4)
            
            # Performance charts
            if 'historical_performance' in performance_data:
                perf_df = pd.DataFrame(performance_data['historical_performance'])
                if not perf_df.empty:
                    perf_chart = self.charts.create_performance_chart(perf_df)
                    if perf_chart:
                        st.plotly_chart(perf_chart, use_container_width=True)
                        
        except Exception as e:
            logger.error(f"Error creating performance dashboard: {e}")
            st.error("Error creating performance dashboard")


# Global instance
portfolio_summary = PortfolioSummary()
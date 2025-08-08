"""
Professional Charts and Data Visualization for Financial Dashboard
Bloomberg/TradingView-style charts with advanced financial analytics
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
import logging

from config.styles import FINANCIAL_COLORS, CHART_COLORS, MATPLOTLIB_STYLES
from config.settings import COLORS

logger = logging.getLogger(__name__)


class ProfessionalCharts:
    """Professional chart components for financial applications"""
    
    def __init__(self):
        self.colors = FINANCIAL_COLORS
        self.chart_colors = CHART_COLORS
        self.matplotlib_styles = MATPLOTLIB_STYLES
        self._setup_matplotlib_theme()
    
    def _setup_matplotlib_theme(self):
        """Setup professional matplotlib theme"""
        plt.style.use('dark_background')
        plt.rcParams.update({
            'figure.facecolor': '#1E293B',
            'axes.facecolor': '#334155',
            'axes.edgecolor': '#475569',
            'axes.labelcolor': '#F8FAFC',
            'text.color': '#F8FAFC',
            'xtick.color': '#CBD5E1',
            'ytick.color': '#CBD5E1',
            'grid.color': '#475569',
            'grid.alpha': 0.3,
            'font.family': 'sans-serif',
            'font.sans-serif': ['Inter', 'Arial', 'sans-serif'],
            'font.size': 10,
            'axes.titlesize': 14,
            'axes.labelsize': 12,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'legend.fontsize': 10,
            'figure.titlesize': 16
        })
    
    def create_options_payoff_diagram(
        self, 
        option_data: Dict[str, Any],
        spot_prices: Optional[np.ndarray] = None
    ) -> go.Figure:
        """Create professional options payoff diagram"""
        try:
            if not option_data:
                st.warning("No option data available for payoff diagram")
                return None
            
            # Generate spot price range if not provided
            if spot_prices is None:
                current_spot = option_data.get('spot_price', 100)
                spot_prices = np.linspace(current_spot * 0.5, current_spot * 1.5, 100)
            
            strike = option_data.get('strike_price', 100)
            option_type = option_data.get('option_type', 'call')
            premium = option_data.get('option_premium', 5)
            
            # Calculate payoffs
            if option_type.lower() == 'call':
                payoffs = np.maximum(spot_prices - strike, 0) - premium
                title = f"Call Option Payoff - Strike: ${strike:.2f}"
            else:
                payoffs = np.maximum(strike - spot_prices, 0) - premium
                title = f"Put Option Payoff - Strike: ${strike:.2f}"
            
            # Create figure
            fig = go.Figure()
            
            # Add payoff line
            fig.add_trace(go.Scatter(
                x=spot_prices,
                y=payoffs,
                mode='lines',
                name='Payoff at Expiration',
                line=dict(color=self.colors['volume'], width=3),
                fill='tonexty',
                fillcolor=f"rgba(59, 130, 246, 0.1)"
            ))
            
            # Add zero line
            fig.add_hline(y=0, line_dash="dash", line_color=self.colors['neutral'])
            
            # Add strike line
            fig.add_vline(x=strike, line_dash="dash", line_color=self.colors['warning'])
            
            # Add current spot price
            current_spot = option_data.get('spot_price', strike)
            fig.add_vline(x=current_spot, line_dash="dot", line_color=self.colors['bullish'])
            
            # Annotations
            fig.add_annotation(
                x=strike, y=max(payoffs) * 0.8,
                text=f"Strike: ${strike:.2f}",
                showarrow=True, arrowhead=2,
                bgcolor=self.colors['warning'], bordercolor=self.colors['warning']
            )
            
            fig.add_annotation(
                x=current_spot, y=max(payoffs) * 0.6,
                text=f"Current: ${current_spot:.2f}",
                showarrow=True, arrowhead=2,
                bgcolor=self.colors['bullish'], bordercolor=self.colors['bullish']
            )
            
            # Professional styling
            fig.update_layout(
                title=dict(
                    text=title,
                    x=0.5,
                    font=dict(size=18, color='#F8FAFC', family='Inter')
                ),
                xaxis_title="Spot Price at Expiration ($)",
                yaxis_title="Profit/Loss ($)",
                paper_bgcolor='#1E293B',
                plot_bgcolor='#334155',
                font=dict(color='#F8FAFC', family='Inter'),
                xaxis=dict(
                    gridcolor='rgba(255,255,255,0.1)',
                    showgrid=True,
                    zeroline=False
                ),
                yaxis=dict(
                    gridcolor='rgba(255,255,255,0.1)',
                    showgrid=True,
                    zeroline=False
                ),
                height=500,
                hovermode='x unified',
                showlegend=True
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating options payoff diagram: {e}")
            st.error("Error creating options payoff diagram")
            return None
    
    def create_greeks_dashboard(self, greeks_data: Dict[str, float]) -> go.Figure:
        """Create Greeks dashboard with gauge charts"""
        try:
            if not greeks_data:
                st.warning("No Greeks data available")
                return None
            
            # Create subplots for multiple gauges
            fig = make_subplots(
                rows=2, cols=3,
                subplot_titles=['Delta', 'Gamma', 'Theta', 'Vega', 'Rho', 'Portfolio'],
                specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
                       [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]]
            )
            
            # Greeks configuration
            greeks_config = {
                'delta': {'range': [-1, 1], 'color': self.colors['volume'], 'format': '.3f'},
                'gamma': {'range': [0, 1], 'color': self.colors['bullish'], 'format': '.4f'},
                'theta': {'range': [-1, 0], 'color': self.colors['bearish'], 'format': '.3f'},
                'vega': {'range': [0, 100], 'color': self.colors['warning'], 'format': '.2f'},
                'rho': {'range': [-1, 1], 'color': self.colors['neutral'], 'format': '.3f'},
                'portfolio': {'range': [0, 1], 'color': self.colors['portfolio'], 'format': '.2%'}
            }
            
            positions = [(1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3)]
            
            for i, (greek, config) in enumerate(greeks_config.items()):
                value = greeks_data.get(greek, 0)
                row, col = positions[i]
                
                fig.add_trace(
                    go.Indicator(
                        mode="gauge+number",
                        value=value,
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': greek.capitalize()},
                        gauge={
                            'axis': {'range': [None, config['range'][1]]},
                            'bar': {'color': config['color']},
                            'steps': [
                                {'range': [config['range'][0], config['range'][1] * 0.5], 'color': "rgba(255,255,255,0.1)"},
                                {'range': [config['range'][1] * 0.5, config['range'][1]], 'color': "rgba(255,255,255,0.2)"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': config['range'][1] * 0.9
                            }
                        }
                    ),
                    row=row, col=col
                )
            
            fig.update_layout(
                title=dict(
                    text="Option Greeks Dashboard",
                    x=0.5,
                    font=dict(size=20, color='#F8FAFC', family='Inter')
                ),
                paper_bgcolor='#1E293B',
                plot_bgcolor='#334155',
                font=dict(color='#F8FAFC', family='Inter'),
                height=600,
                margin=dict(l=60, r=60, t=80, b=60)
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating Greeks dashboard: {e}")
            st.error("Error creating Greeks dashboard")
            return None
    
    def create_volatility_surface(
        self, 
        strike_prices: List[float],
        time_to_expiry: List[float],
        implied_vols: np.ndarray
    ) -> go.Figure:
        """Create 3D volatility surface plot"""
        try:
            if len(strike_prices) == 0 or len(time_to_expiry) == 0:
                st.warning("Insufficient data for volatility surface")
                return None
            
            # Create meshgrid
            X, Y = np.meshgrid(strike_prices, time_to_expiry)
            
            fig = go.Figure(data=[
                go.Surface(
                    x=X,
                    y=Y,
                    z=implied_vols,
                    colorscale='Viridis',
                    opacity=0.8,
                    name="Implied Volatility"
                )
            ])
            
            fig.update_layout(
                title=dict(
                    text="Implied Volatility Surface",
                    x=0.5,
                    font=dict(size=18, color='#F8FAFC', family='Inter')
                ),
                scene=dict(
                    xaxis_title="Strike Price",
                    yaxis_title="Time to Expiry",
                    zaxis_title="Implied Volatility",
                    bgcolor='#334155',
                    xaxis=dict(backgroundcolor='#334155', gridcolor='rgba(255,255,255,0.1)'),
                    yaxis=dict(backgroundcolor='#334155', gridcolor='rgba(255,255,255,0.1)'),
                    zaxis=dict(backgroundcolor='#334155', gridcolor='rgba(255,255,255,0.1)')
                ),
                paper_bgcolor='#1E293B',
                font=dict(color='#F8FAFC', family='Inter'),
                height=600,
                margin=dict(l=60, r=60, t=60, b=60)
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating volatility surface: {e}")
            st.error("Error creating volatility surface")
            return None
    
    def create_portfolio_composition_chart(
        self, 
        portfolio_data: Dict[str, float],
        chart_type: str = "donut"
    ) -> go.Figure:
        """Create portfolio composition chart"""
        try:
            if not portfolio_data:
                st.warning("No portfolio data available")
                return None
            
            labels = list(portfolio_data.keys())
            values = list(portfolio_data.values())
            
            if chart_type == "donut":
                fig = go.Figure(data=[
                    go.Pie(
                        labels=labels,
                        values=values,
                        hole=0.4,
                        marker=dict(
                            colors=self.chart_colors[:len(labels)],
                            line=dict(color='#334155', width=2)
                        )
                    )
                ])
            else:  # treemap
                fig = go.Figure(go.Treemap(
                    labels=labels,
                    values=values,
                    parents=[""] * len(labels),
                    marker=dict(
                        colors=self.chart_colors[:len(labels)],
                        line=dict(color='#334155', width=2)
                    )
                ))
            
            fig.update_layout(
                title=dict(
                    text="Portfolio Composition",
                    x=0.5,
                    font=dict(size=18, color='#F8FAFC', family='Inter')
                ),
                paper_bgcolor='#1E293B',
                plot_bgcolor='#334155',
                font=dict(color='#F8FAFC', family='Inter'),
                height=500,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating portfolio composition chart: {e}")
            st.error("Error creating portfolio composition chart")
            return None
    
    def create_risk_metrics_heatmap(
        self, 
        risk_data: pd.DataFrame
    ) -> go.Figure:
        """Create risk metrics heatmap"""
        try:
            if risk_data.empty:
                st.warning("No risk data available for heatmap")
                return None
            
            fig = go.Figure(data=go.Heatmap(
                z=risk_data.values,
                x=risk_data.columns,
                y=risk_data.index,
                colorscale='RdYlGn_r',
                showscale=True,
                hoverongaps=False
            ))
            
            fig.update_layout(
                title=dict(
                    text="Risk Metrics Heatmap",
                    x=0.5,
                    font=dict(size=18, color='#F8FAFC', family='Inter')
                ),
                paper_bgcolor='#1E293B',
                plot_bgcolor='#334155',
                font=dict(color='#F8FAFC', family='Inter'),
                height=500,
                margin=dict(l=100, r=60, t=60, b=60)
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating risk metrics heatmap: {e}")
            st.error("Error creating risk metrics heatmap")
            return None
    
    def create_performance_chart(
        self, 
        performance_data: pd.DataFrame,
        benchmark_data: Optional[pd.DataFrame] = None
    ) -> go.Figure:
        """Create performance comparison chart"""
        try:
            if performance_data.empty:
                st.warning("No performance data available")
                return None
            
            fig = go.Figure()
            
            # Add portfolio performance
            fig.add_trace(go.Scatter(
                x=performance_data.index,
                y=performance_data.iloc[:, 0],
                mode='lines',
                name='Portfolio',
                line=dict(color=self.colors['portfolio'], width=3),
                fill='tonexty'
            ))
            
            # Add benchmark if available
            if benchmark_data is not None and not benchmark_data.empty:
                fig.add_trace(go.Scatter(
                    x=benchmark_data.index,
                    y=benchmark_data.iloc[:, 0],
                    mode='lines',
                    name='Benchmark',
                    line=dict(color=self.colors['benchmark'], width=2, dash='dash')
                ))
            
            fig.update_layout(
                title=dict(
                    text="Portfolio Performance",
                    x=0.5,
                    font=dict(size=18, color='#F8FAFC', family='Inter')
                ),
                xaxis_title="Date",
                yaxis_title="Cumulative Return (%)",
                paper_bgcolor='#1E293B',
                plot_bgcolor='#334155',
                font=dict(color='#F8FAFC', family='Inter'),
                xaxis=dict(
                    gridcolor='rgba(255,255,255,0.1)',
                    showgrid=True,
                    zeroline=False
                ),
                yaxis=dict(
                    gridcolor='rgba(255,255,255,0.1)',
                    showgrid=True,
                    zeroline=False
                ),
                height=450,
                hovermode='x unified',
                showlegend=True
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating performance chart: {e}")
            st.error("Error creating performance chart")
            return None
    
    def create_depth_analysis_chart(
        self, 
        depth_data: Dict[str, Any]
    ) -> go.Figure:
        """Create market depth analysis chart"""
        try:
            if not depth_data:
                st.warning("No depth data available")
                return None
            
            # Extract data
            entities = list(depth_data.keys())
            depth_50bps = [depth_data[entity].get('depth_50bps', 0) for entity in entities]
            depth_100bps = [depth_data[entity].get('depth_100bps', 0) for entity in entities]
            depth_200bps = [depth_data[entity].get('depth_200bps', 0) for entity in entities]
            
            fig = go.Figure()
            
            # Add bars for different depth levels
            fig.add_trace(go.Bar(
                name='50bps Depth',
                x=entities,
                y=depth_50bps,
                marker_color=self.colors['bullish'],
                opacity=0.8
            ))
            
            fig.add_trace(go.Bar(
                name='100bps Depth',
                x=entities,
                y=depth_100bps,
                marker_color=self.colors['volume'],
                opacity=0.8
            ))
            
            fig.add_trace(go.Bar(
                name='200bps Depth',
                x=entities,
                y=depth_200bps,
                marker_color=self.colors['warning'],
                opacity=0.8
            ))
            
            fig.update_layout(
                title=dict(
                    text="Market Depth Analysis by Entity",
                    x=0.5,
                    font=dict(size=18, color='#F8FAFC', family='Inter')
                ),
                xaxis_title="Entities",
                yaxis_title="Depth ($)",
                paper_bgcolor='#1E293B',
                plot_bgcolor='#334155',
                font=dict(color='#F8FAFC', family='Inter'),
                barmode='group',
                xaxis=dict(
                    gridcolor='rgba(255,255,255,0.1)',
                    showgrid=True,
                    zeroline=False
                ),
                yaxis=dict(
                    gridcolor='rgba(255,255,255,0.1)',
                    showgrid=True,
                    zeroline=False
                ),
                height=500,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating depth analysis chart: {e}")
            st.error("Error creating depth analysis chart")
            return None


# Global instance
professional_charts = ProfessionalCharts()
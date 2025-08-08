"""
Professional UI Components for Financial Dashboard
Bloomberg/TradingView-inspired components for institutional-grade interface
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

from config.simple_styles import ICONS, FINANCIAL_COLORS, CHART_COLORS
from config.settings import COLORS

logger = logging.getLogger(__name__)


class ProfessionalComponents:
    """Professional UI components for financial applications"""
    
    def __init__(self):
        self.colors = FINANCIAL_COLORS
        self.icons = ICONS
        self.chart_colors = CHART_COLORS
    
    def create_summary_card(
        self, 
        title: str, 
        value: str, 
        change: Optional[str] = None, 
        change_type: str = "neutral",
        icon: Optional[str] = None,
        description: Optional[str] = None,
        key: Optional[str] = None
    ) -> None:
        """Create a professional summary card with metrics"""
        try:
            card_html = f"""
            <div class="summary-card slide-in-up" style="animation-delay: 0.{key if key else '1'}s;">
                <div class="metric-label">
                    {icon + ' ' if icon else ''}{title}
                </div>
                <div class="metric-value">{value}</div>
                {f'<div class="metric-change {change_type}">{change}</div>' if change else ''}
                {f'<div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.5rem;">{description}</div>' if description else ''}
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            
        except Exception as e:
            logger.error(f"Error creating summary card: {e}")
            st.error(f"Error creating summary card for {title}")
    
    def create_status_indicator(
        self, 
        status: str, 
        message: str, 
        status_type: str = "info"
    ) -> None:
        """Create a professional status indicator"""
        try:
            icon_map = {
                "success": "✅",
                "warning": "⚠️", 
                "error": "❌",
                "info": "ℹ️"
            }
            
            icon = icon_map.get(status_type, "ℹ️")
            
            status_html = f"""
            <div class="status-indicator {status_type}">
                <span>{icon}</span>
                <strong>{status}</strong>
                <span>{message}</span>
            </div>
            """
            st.markdown(status_html, unsafe_allow_html=True)
            
        except Exception as e:
            logger.error(f"Error creating status indicator: {e}")
            st.error("Error creating status indicator")
    
    def create_progress_indicator(
        self, 
        progress: float, 
        title: str = "Progress", 
        show_percentage: bool = True
    ) -> None:
        """Create an animated progress indicator"""
        try:
            percentage = min(max(progress * 100, 0), 100)
            
            progress_html = f"""
            <div style="margin: 1rem 0;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-weight: 500; color: var(--text-secondary);">{title}</span>
                    {f'<span style="font-weight: 600; color: var(--text-primary);">{percentage:.1f}%</span>' if show_percentage else ''}
                </div>
                <div class="progress-indicator">
                    <div class="progress-bar-enhanced" style="width: {percentage}%;"></div>
                </div>
            </div>
            """
            st.markdown(progress_html, unsafe_allow_html=True)
            
        except Exception as e:
            logger.error(f"Error creating progress indicator: {e}")
            st.error("Error creating progress indicator")
    
    def create_professional_table(
        self, 
        data: pd.DataFrame, 
        title: str, 
        icon: Optional[str] = None,
        highlight_columns: Optional[List[str]] = None,
        format_columns: Optional[Dict[str, str]] = None
    ) -> None:
        """Create a professional data table with styling"""
        try:
            if data.empty:
                st.info(f"No data available for {title}")
                return
            
            # Format data
            display_df = data.copy()
            if format_columns:
                for col, format_type in format_columns.items():
                    if col in display_df.columns:
                        if format_type == "currency":
                            display_df[col] = display_df[col].apply(lambda x: f"${x:,.0f}" if pd.notnull(x) else "")
                        elif format_type == "percentage":
                            display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else "")
                        elif format_type == "decimal":
                            display_df[col] = display_df[col].apply(lambda x: f"{x:.4f}" if pd.notnull(x) else "")
            
            # Create table HTML
            table_html = f"""
            <div class="data-table-container slide-in-up">
                <div class="table-header">
                    <h3 class="table-title">
                        {icon + ' ' if icon else ''}{title}
                    </h3>
                </div>
                <div style="padding: 1rem;">
            """
            
            st.markdown(table_html, unsafe_allow_html=True)
            
            # Use Streamlit's dataframe with custom styling
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
            
            st.markdown("</div></div>", unsafe_allow_html=True)
            
        except Exception as e:
            logger.error(f"Error creating professional table: {e}")
            st.error(f"Error creating table for {title}")
    
    def create_loading_placeholder(
        self, 
        height: int = 100, 
        message: str = "Loading..."
    ) -> None:
        """Create a loading skeleton placeholder"""
        try:
            skeleton_html = f"""
            <div style="display: flex; align-items: center; justify-content: center; height: {height}px; margin: 1rem 0;">
                <div class="professional-spinner"></div>
                <span style="margin-left: 1rem; color: var(--text-secondary);">{message}</span>
            </div>
            """
            st.markdown(skeleton_html, unsafe_allow_html=True)
            
        except Exception as e:
            logger.error(f"Error creating loading placeholder: {e}")
            st.error("Error creating loading indicator")
    
    def create_professional_form_section(
        self, 
        title: str, 
        icon: Optional[str] = None,
        description: Optional[str] = None
    ):
        """Create a professional form section with styling"""
        try:
            section_html = f"""
            <div class="form-section">
                <h3 class="form-section-title">
                    {icon + ' ' if icon else ''}{title}
                </h3>
                {f'<p style="color: var(--text-secondary); margin-bottom: 1.5rem;">{description}</p>' if description else ''}
            </div>
            """
            st.markdown(section_html, unsafe_allow_html=True)
            
        except Exception as e:
            logger.error(f"Error creating form section: {e}")
            st.error(f"Error creating form section: {title}")
    
    def create_validation_feedback(
        self, 
        message: str, 
        feedback_type: str = "success"
    ) -> None:
        """Create professional validation feedback"""
        try:
            icon_map = {
                "success": "✅",
                "error": "❌",
                "warning": "⚠️",
                "info": "ℹ️"
            }
            
            icon = icon_map.get(feedback_type, "ℹ️")
            
            feedback_html = f"""
            <div class="validation-feedback {feedback_type}">
                <span>{icon}</span>
                <span>{message}</span>
            </div>
            """
            st.markdown(feedback_html, unsafe_allow_html=True)
            
        except Exception as e:
            logger.error(f"Error creating validation feedback: {e}")
            st.error("Error creating validation feedback")
    
    def create_dashboard_grid(self, content_items: List[Any]) -> None:
        """Create a responsive dashboard grid layout"""
        try:
            st.markdown('<div class="dashboard-grid">', unsafe_allow_html=True)
            
            for item in content_items:
                if callable(item):
                    item()
                else:
                    st.markdown(str(item), unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
        except Exception as e:
            logger.error(f"Error creating dashboard grid: {e}")
            st.error("Error creating dashboard layout")
    
    def create_financial_chart(
        self, 
        data: pd.DataFrame, 
        chart_type: str = "line", 
        title: str = "Financial Chart",
        x_col: str = "Date",
        y_col: str = "Value",
        color_scheme: str = "professional"
    ) -> go.Figure:
        """Create professional financial charts with Plotly"""
        try:
            if data.empty:
                st.warning(f"No data available for {title}")
                return None
            
            # Create figure based on chart type
            fig = go.Figure()
            
            if chart_type == "line":
                fig.add_trace(go.Scatter(
                    x=data[x_col] if x_col in data.columns else range(len(data)),
                    y=data[y_col] if y_col in data.columns else data.iloc[:, 0],
                    mode='lines+markers',
                    line=dict(color=self.colors['volume'], width=3),
                    marker=dict(size=6, color=self.colors['volume']),
                    name=y_col
                ))
            elif chart_type == "bar":
                fig.add_trace(go.Bar(
                    x=data[x_col] if x_col in data.columns else range(len(data)),
                    y=data[y_col] if y_col in data.columns else data.iloc[:, 0],
                    marker_color=self.colors['volume'],
                    name=y_col
                ))
            elif chart_type == "candlestick" and all(col in data.columns for col in ['Open', 'High', 'Low', 'Close']):
                fig.add_trace(go.Candlestick(
                    x=data[x_col] if x_col in data.columns else range(len(data)),
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'],
                    increasing_line_color=self.colors['bullish'],
                    decreasing_line_color=self.colors['bearish'],
                    name="Price"
                ))
            
            # Professional styling
            fig.update_layout(
                title=dict(
                    text=title,
                    x=0.5,
                    font=dict(size=18, color='#F8FAFC', family='Inter')
                ),
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
                margin=dict(l=60, r=60, t=60, b=60),
                height=400,
                hovermode='x unified',
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
            logger.error(f"Error creating financial chart: {e}")
            st.error(f"Error creating chart: {title}")
            return None
    
    def create_portfolio_overview_cards(
        self, 
        portfolio_data: Dict[str, Any]
    ) -> None:
        """Create portfolio overview cards"""
        try:
            if not portfolio_data:
                st.info("No portfolio data available")
                return
            
            # Create columns for cards
            cols = st.columns(4)
            
            cards_data = [
                {
                    "title": "Total Portfolio Value",
                    "value": f"${portfolio_data.get('total_value', 0):,.0f}",
                    "change": f"+{portfolio_data.get('value_change', 0):.1f}%",
                    "change_type": "positive" if portfolio_data.get('value_change', 0) >= 0 else "negative",
                    "icon": self.icons['portfolio'],
                    "description": "Current market value"
                },
                {
                    "title": "Active Entities", 
                    "value": str(portfolio_data.get('active_entities', 0)),
                    "change": None,
                    "change_type": "neutral",
                    "icon": self.icons['entity'],
                    "description": "Configured entities"
                },
                {
                    "title": "Risk Exposure",
                    "value": f"{portfolio_data.get('risk_level', 0):.1f}%",
                    "change": None,
                    "change_type": "warning" if portfolio_data.get('risk_level', 0) > 50 else "success",
                    "icon": self.icons['risk'],
                    "description": "Current risk level"
                },
                {
                    "title": "Performance",
                    "value": f"+{portfolio_data.get('performance', 0):.2f}%",
                    "change": f"vs benchmark",
                    "change_type": "positive" if portfolio_data.get('performance', 0) >= 0 else "negative",
                    "icon": self.icons['performance'],
                    "description": "Portfolio performance"
                }
            ]
            
            for i, card_data in enumerate(cards_data):
                with cols[i]:
                    self.create_summary_card(**card_data, key=str(i))
                    
        except Exception as e:
            logger.error(f"Error creating portfolio overview cards: {e}")
            st.error("Error creating portfolio overview")
    
    def create_phase_progress_indicator(
        self, 
        current_phase: int, 
        total_phases: int = 3,
        phase_names: Optional[List[str]] = None
    ) -> None:
        """Create a professional phase progress indicator"""
        try:
            if not phase_names:
                phase_names = ["Entity Setup", "Tranche Configuration", "Depth Analysis"]
            
            progress = (current_phase - 1) / (total_phases - 1) if total_phases > 1 else 1.0
            
            # Create phase indicator HTML
            phase_html = """
            <div style="margin: 2rem 0; padding: 1.5rem; background: var(--gradient-card); border-radius: var(--radius-xl); border: 1px solid var(--border-color);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h3 style="margin: 0; color: var(--text-primary); font-size: 1.25rem;">Phase Progress</h3>
                    <span style="color: var(--text-secondary); font-size: 0.875rem;">Phase {current_phase} of {total_phases}</span>
                </div>
            """
            
            # Progress bar
            phase_html += f"""
                <div class="progress-indicator">
                    <div class="progress-bar-enhanced" style="width: {progress * 100}%;"></div>
                </div>
            """
            
            # Phase indicators
            phase_html += '<div style="display: flex; justify-content: space-between; margin-top: 1rem;">'
            for i, phase_name in enumerate(phase_names[:total_phases], 1):
                status = "completed" if i < current_phase else "active" if i == current_phase else "pending"
                color = "var(--success-green)" if status == "completed" else "var(--accent-blue)" if status == "active" else "var(--text-muted)"
                
                phase_html += f"""
                <div style="text-align: center; flex: 1;">
                    <div style="width: 12px; height: 12px; border-radius: 50%; background: {color}; margin: 0 auto 0.5rem;"></div>
                    <span style="font-size: 0.75rem; color: {color}; font-weight: 500;">{phase_name}</span>
                </div>
                """
            
            phase_html += '</div></div>'
            
            st.markdown(phase_html, unsafe_allow_html=True)
            
        except Exception as e:
            logger.error(f"Error creating phase progress indicator: {e}")
            st.error("Error creating phase progress indicator")


# Global instance
professional_components = ProfessionalComponents()
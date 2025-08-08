"""
Simple Professional UI Components for Streamlit
Uses native Streamlit components with minimal custom CSS
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any, Optional
import pandas as pd

from config.simple_styles import FINANCIAL_COLORS, CHART_COLORS, ICONS


class SimpleComponents:
    """Simple but professional UI components"""
    
    def __init__(self):
        self.colors = FINANCIAL_COLORS
        self.icons = ICONS
    
    def create_metric_card(self, title: str, value: Any, delta: Optional[float] = None, 
                          help_text: str = None, icon: str = None) -> None:
        """Create a simple metric card using Streamlit's native metric"""
        try:
            # Format the title with icon
            display_title = f"{icon} {title}" if icon else title
            
            # Format the value
            if isinstance(value, float):
                if abs(value) >= 1000000:
                    formatted_value = f"${value/1000000:.2f}M"
                elif abs(value) >= 1000:
                    formatted_value = f"${value/1000:.1f}K" 
                else:
                    formatted_value = f"${value:.2f}"
            else:
                formatted_value = str(value)
            
            # Create the metric
            if delta is not None:
                st.metric(
                    label=display_title,
                    value=formatted_value,
                    delta=f"{delta:+.2f}" if isinstance(delta, (int, float)) else str(delta),
                    help=help_text
                )
            else:
                st.metric(
                    label=display_title,
                    value=formatted_value,
                    help=help_text
                )
                
        except Exception as e:
            st.error(f"Error creating metric card for {title}: {str(e)}")
    
    def create_status_badge(self, status: str, text: str = None) -> str:
        """Create a simple status badge"""
        status_colors = {
            'success': '🟢',
            'warning': '🟡', 
            'error': '🔴',
            'info': '🔵',
            'neutral': '⚪'
        }
        
        badge_text = text or status.title()
        emoji = status_colors.get(status, '⚪')
        return f"{emoji} {badge_text}"
    
    def create_progress_bar(self, progress: float, label: str = None) -> None:
        """Create a progress bar with label"""
        if label:
            st.text(label)
        st.progress(min(1.0, max(0.0, progress)))
    
    def create_info_box(self, content: str, box_type: str = 'info') -> None:
        """Create an information box"""
        if box_type == 'success':
            st.success(content)
        elif box_type == 'warning':
            st.warning(content)
        elif box_type == 'error':
            st.error(content)
        else:
            st.info(content)
    
    def create_summary_table(self, data: Dict[str, Any], title: str = None) -> None:
        """Create a summary table from dictionary"""
        if title:
            st.subheader(title)
        
        # Convert dict to DataFrame for better display
        df_data = []
        for key, value in data.items():
            # Format values nicely
            if isinstance(value, float):
                if abs(value) >= 1000000:
                    formatted_value = f"${value/1000000:.2f}M"
                elif abs(value) >= 1000:
                    formatted_value = f"${value/1000:.1f}K"
                else:
                    formatted_value = f"${value:.2f}"
            elif isinstance(value, (int, float)) and 'percentage' in key.lower():
                formatted_value = f"{value:.1%}"
            else:
                formatted_value = str(value)
                
            df_data.append({'Metric': key.replace('_', ' ').title(), 'Value': formatted_value})
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, hide_index=True, use_container_width=True)
    
    def create_simple_chart(self, data: pd.DataFrame, chart_type: str = 'line',
                           x_col: str = None, y_col: str = None, 
                           title: str = None) -> None:
        """Create a simple chart using Plotly"""
        try:
            if chart_type == 'line':
                fig = px.line(data, x=x_col, y=y_col, title=title,
                             color_discrete_sequence=CHART_COLORS['portfolio'])
            elif chart_type == 'bar':
                fig = px.bar(data, x=x_col, y=y_col, title=title,
                            color_discrete_sequence=CHART_COLORS['portfolio'])
            elif chart_type == 'pie':
                fig = px.pie(data, values=y_col, names=x_col, title=title,
                            color_discrete_sequence=CHART_COLORS['portfolio'])
            else:
                fig = px.scatter(data, x=x_col, y=y_col, title=title,
                               color_discrete_sequence=CHART_COLORS['portfolio'])
            
            # Update layout for dark theme
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)', 
                font_color='#F8FAFC',
                title_font_color='#F8FAFC'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error creating chart: {str(e)}")
    
    def create_option_payoff_chart(self, strikes: List[float], payoffs: List[float],
                                  option_type: str = 'call', title: str = None) -> None:
        """Create an options payoff diagram"""
        try:
            fig = go.Figure()
            
            color = FINANCIAL_COLORS['bull'] if option_type.lower() == 'call' else FINANCIAL_COLORS['bear']
            
            fig.add_trace(go.Scatter(
                x=strikes,
                y=payoffs,
                mode='lines',
                name=f'{option_type.title()} Payoff',
                line=dict(color=color, width=3)
            ))
            
            # Add break-even line
            fig.add_hline(y=0, line_dash="dash", line_color="#64748B", 
                         annotation_text="Break-even")
            
            fig.update_layout(
                title=title or f"{option_type.title()} Option Payoff Diagram",
                xaxis_title="Underlying Price",
                yaxis_title="Profit/Loss",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#F8FAFC',
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error creating payoff chart: {str(e)}")


# Global instance
simple_components = SimpleComponents()
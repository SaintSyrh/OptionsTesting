"""
Professional Dashboard Layout Manager
Bloomberg/TradingView-inspired layout system with responsive grid and advanced UI components
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Any, Optional, Callable, Tuple
from datetime import datetime
import logging

from ui.professional_components import professional_components
from ui.professional_charts import professional_charts
from config.styles import ICONS
from config.settings import COLORS, NAVIGATION

logger = logging.getLogger(__name__)


class DashboardLayoutManager:
    """Professional dashboard layout with Bloomberg/TradingView styling"""
    
    def __init__(self):
        self.components = professional_components
        self.charts = professional_charts
        self.icons = ICONS
        self.colors = COLORS
        self.navigation = NAVIGATION
    
    def create_dashboard_header(
        self, 
        title: str, 
        subtitle: Optional[str] = None,
        show_timestamp: bool = True
    ) -> None:
        """Create professional dashboard header"""
        try:
            header_html = f"""
            <div class="main-header fade-in-up">
                {title}
                {f'<div style="font-size: 1rem; font-weight: 400; margin-top: 0.5rem; opacity: 0.8;">{subtitle}</div>' if subtitle else ''}
            </div>
            """
            
            if show_timestamp:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                header_html += f"""
                <div style="text-align: center; color: var(--text-muted); font-size: 0.875rem; margin-bottom: 2rem;">
                    Last Updated: {timestamp}
                </div>
                """
            
            st.markdown(header_html, unsafe_allow_html=True)
            
        except Exception as e:
            logger.error(f"Error creating dashboard header: {e}")
            st.error("Error creating dashboard header")
    
    def create_phase_navigation_enhanced(
        self, 
        current_phase: int, 
        total_phases: int = 3,
        phase_data: Optional[Dict[int, Dict[str, Any]]] = None
    ) -> None:
        """Create enhanced phase navigation with professional styling"""
        try:
            if not phase_data:
                phase_data = self.navigation['phases']
            
            # Create phase navigation container
            nav_html = """
            <div class="slide-in-up" style="background: var(--gradient-card); border-radius: var(--radius-xl); padding: var(--space-xl); margin: var(--space-xl) 0; border: 1px solid var(--border-color); box-shadow: var(--shadow-lg);">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--space-lg);">
                    <h3 style="margin: 0; color: var(--text-primary); font-size: 1.25rem; font-weight: 600;">
                        🗺️ Project Navigation
                    </h3>
                    <div style="color: var(--text-secondary); font-size: 0.875rem;">
                        Phase {current_phase} of {total_phases}
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: var(--space-md);">
            """
            
            for phase_num in range(1, total_phases + 1):
                phase_info = phase_data.get(phase_num, {})
                phase_name = phase_info.get('name', f'Phase {phase_num}')
                phase_icon = phase_info.get('icon', '📊')
                phase_color = phase_info.get('color', self.colors['primary'])
                
                # Determine phase status
                if phase_num < current_phase:
                    status = 'completed'
                    bg_color = 'var(--success-green)'
                    text_color = 'white'
                elif phase_num == current_phase:
                    status = 'active'
                    bg_color = phase_color
                    text_color = 'white'
                else:
                    status = 'pending'
                    bg_color = 'var(--input-bg)'
                    text_color = 'var(--text-muted)'
                
                # Phase indicator
                nav_html += f"""
                <div style="display: flex; align-items: center; gap: var(--space-sm); padding: var(--space-sm) var(--space-md); background: {bg_color}; border-radius: var(--radius-md); color: {text_color}; font-weight: 500; transition: all var(--transition-normal); {'transform: scale(1.05); box-shadow: var(--shadow-glow);' if status == 'active' else ''}">
                    <span style="font-size: 1.1rem;">{phase_icon}</span>
                    <span style="font-size: 0.875rem;">{phase_name}</span>
                    {f'<span style="font-size: 0.75rem; margin-left: var(--space-xs);">✓</span>' if status == 'completed' else ''}
                </div>
                """
                
                # Add arrow between phases (except for last phase)
                if phase_num < total_phases:
                    nav_html += f"""
                    <div style="color: var(--text-muted); font-size: 1.2rem;">
                        →
                    </div>
                    """
            
            nav_html += """
                </div>
            </div>
            """
            
            st.markdown(nav_html, unsafe_allow_html=True)
            
            # Show phase progress
            progress = (current_phase - 1) / (total_phases - 1) if total_phases > 1 else 1.0
            self.components.create_progress_indicator(
                progress, 
                "Overall Progress", 
                show_percentage=True
            )
            
        except Exception as e:
            logger.error(f"Error creating enhanced phase navigation: {e}")
            st.error("Error creating phase navigation")
    
    def create_portfolio_dashboard(
        self, 
        portfolio_data: Dict[str, Any]
    ) -> None:
        """Create comprehensive portfolio dashboard"""
        try:
            st.markdown("## 📊 Portfolio Dashboard")
            
            # Portfolio overview cards
            if portfolio_data:
                self.components.create_portfolio_overview_cards(portfolio_data)
                
                # Create two columns for charts
                col1, col2 = st.columns(2)
                
                with col1:
                    # Portfolio composition
                    if 'composition' in portfolio_data:
                        composition_chart = self.charts.create_portfolio_composition_chart(
                            portfolio_data['composition']
                        )
                        if composition_chart:
                            st.plotly_chart(composition_chart, use_container_width=True)
                
                with col2:
                    # Performance chart
                    if 'performance_data' in portfolio_data:
                        performance_chart = self.charts.create_performance_chart(
                            portfolio_data['performance_data']
                        )
                        if performance_chart:
                            st.plotly_chart(performance_chart, use_container_width=True)
            else:
                st.info("Configure entities and tranches to see portfolio dashboard")
                
        except Exception as e:
            logger.error(f"Error creating portfolio dashboard: {e}")
            st.error("Error creating portfolio dashboard")
    
    def create_phase_specific_layout(
        self, 
        phase: int, 
        content_function: Callable,
        phase_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Create phase-specific layout with professional styling"""
        try:
            phase_config = self.navigation['phases'].get(phase, {})
            phase_name = phase_config.get('name', f'Phase {phase}')
            phase_icon = phase_config.get('icon', '📊')
            phase_color = phase_config.get('color', self.colors['primary'])
            phase_description = phase_config.get('description', '')
            
            # Phase header
            phase_header_html = f"""
            <div class="slide-in-up" style="background: linear-gradient(135deg, {phase_color}15 0%, {phase_color}05 100%); border: 1px solid {phase_color}30; border-radius: var(--radius-xl); padding: var(--space-xl); margin: var(--space-xl) 0;">
                <h2 style="margin: 0 0 var(--space-sm) 0; color: {phase_color}; font-size: 1.5rem; font-weight: 700; display: flex; align-items: center; gap: var(--space-sm);">
                    <span style="font-size: 1.3rem;">{phase_icon}</span>
                    {phase_name}
                </h2>
                <p style="margin: 0; color: var(--text-secondary); font-size: 1rem;">
                    {phase_description}
                </p>
            </div>
            """
            
            st.markdown(phase_header_html, unsafe_allow_html=True)
            
            # Execute phase content
            if callable(content_function):
                content_function()
            
        except Exception as e:
            logger.error(f"Error creating phase-specific layout: {e}")
            st.error(f"Error creating layout for phase {phase}")
    
    def create_data_table_enhanced(
        self, 
        data: pd.DataFrame, 
        title: str,
        icon: Optional[str] = None,
        actions: Optional[List[Dict[str, Any]]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> None:
        """Create enhanced data table with actions and filters"""
        try:
            if data.empty:
                self.components.create_status_indicator(
                    "No Data",
                    f"No data available for {title}",
                    "info"
                )
                return
            
            # Create table container
            table_html = f"""
            <div class="data-table-container slide-in-up">
                <div class="table-header">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3 class="table-title">
                            {icon + ' ' if icon else ''}{title}
                        </h3>
                        <div style="display: flex; gap: var(--space-sm);">
            """
            
            # Add action buttons
            if actions:
                for action in actions:
                    action_label = action.get('label', 'Action')
                    action_icon = action.get('icon', '⚡')
                    table_html += f"""
                    <button class="stButton" style="background: var(--gradient-primary); color: white; border: none; border-radius: var(--radius-md); padding: var(--space-sm) var(--space-md); font-size: 0.875rem;">
                        {action_icon} {action_label}
                    </button>
                    """
            
            table_html += """
                        </div>
                    </div>
                </div>
                <div style="padding: var(--space-lg);">
            """
            
            st.markdown(table_html, unsafe_allow_html=True)
            
            # Apply filters if provided
            filtered_data = data.copy()
            if filters:
                # Implementation would depend on specific filter requirements
                pass
            
            # Display the dataframe
            st.dataframe(
                filtered_data,
                use_container_width=True,
                hide_index=True
            )
            
            st.markdown("</div></div>", unsafe_allow_html=True)
            
        except Exception as e:
            logger.error(f"Error creating enhanced data table: {e}")
            st.error(f"Error creating table for {title}")
    
    def create_metrics_grid(
        self, 
        metrics_data: List[Dict[str, Any]],
        columns: int = 4
    ) -> None:
        """Create a responsive metrics grid"""
        try:
            if not metrics_data:
                st.info("No metrics data available")
                return
            
            # Create columns
            cols = st.columns(columns)
            
            for i, metric in enumerate(metrics_data):
                col_index = i % columns
                with cols[col_index]:
                    self.components.create_summary_card(
                        title=metric.get('title', 'Metric'),
                        value=metric.get('value', '0'),
                        change=metric.get('change'),
                        change_type=metric.get('change_type', 'neutral'),
                        icon=metric.get('icon'),
                        description=metric.get('description'),
                        key=str(i)
                    )
                    
        except Exception as e:
            logger.error(f"Error creating metrics grid: {e}")
            st.error("Error creating metrics grid")
    
    def create_sidebar_enhanced(
        self, 
        params: Dict[str, Any],
        show_summary: bool = True,
        show_actions: bool = True
    ) -> None:
        """Create enhanced sidebar with professional styling"""
        try:
            # Sidebar styling
            sidebar_css = """
            <style>
                .css-1d391kg {
                    background: var(--gradient-surface) !important;
                    border-right: 2px solid var(--border-color) !important;
                }
                
                .sidebar-section {
                    background: var(--gradient-card);
                    border-radius: var(--radius-lg);
                    padding: var(--space-lg);
                    margin: var(--space-md) 0;
                    border: 1px solid var(--border-color);
                }
                
                .sidebar-title {
                    color: var(--text-primary);
                    font-weight: 600;
                    font-size: 1.1rem;
                    margin-bottom: var(--space-md);
                    display: flex;
                    align-items: center;
                    gap: var(--space-sm);
                }
            </style>
            """
            
            st.markdown(sidebar_css, unsafe_allow_html=True)
            
            # Parameter summary
            if show_summary and params:
                with st.sidebar:
                    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
                    st.markdown('<h3 class="sidebar-title">📊 Portfolio Summary</h3>', unsafe_allow_html=True)
                    
                    total_value = params.get('total_valuation', 0)
                    total_tokens = params.get('total_tokens', 0)
                    token_price = total_value / total_tokens if total_tokens > 0 else 0
                    
                    summary_metrics = [
                        f"**Total Value:** ${total_value:,.0f}",
                        f"**Total Tokens:** {total_tokens:,.0f}",
                        f"**Token Price:** ${token_price:.4f}",
                        f"**Volatility:** {params.get('volatility', 0)*100:.1f}%",
                        f"**Risk-free Rate:** {params.get('risk_free_rate', 0)*100:.1f}%"
                    ]
                    
                    for metric in summary_metrics:
                        st.markdown(metric)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Action buttons
            if show_actions:
                with st.sidebar:
                    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
                    st.markdown('<h3 class="sidebar-title">⚡ Quick Actions</h3>', unsafe_allow_html=True)
                    
                    if st.button("🔄 Refresh Data", use_container_width=True):
                        st.rerun()
                    
                    if st.button("📥 Export Configuration", use_container_width=True):
                        # Implementation for export functionality
                        st.info("Export functionality would be implemented here")
                    
                    if st.button("📊 Generate Report", use_container_width=True):
                        # Implementation for report generation
                        st.info("Report generation would be implemented here")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
        except Exception as e:
            logger.error(f"Error creating enhanced sidebar: {e}")
            st.error("Error creating sidebar")
    
    def create_validation_dashboard(
        self, 
        validation_results: Dict[str, Any]
    ) -> None:
        """Create professional validation dashboard"""
        try:
            if not validation_results:
                st.info("No validation data available")
                return
            
            st.markdown("### 🔍 Validation Dashboard")
            
            # Validation summary cards
            validation_metrics = []
            
            total_checks = validation_results.get('total_checks', 0)
            passed_checks = validation_results.get('passed_checks', 0)
            failed_checks = validation_results.get('failed_checks', 0)
            warnings = validation_results.get('warnings', 0)
            
            validation_metrics.extend([
                {
                    'title': 'Total Checks',
                    'value': str(total_checks),
                    'icon': '🔍',
                    'description': 'Validation checks run'
                },
                {
                    'title': 'Passed',
                    'value': str(passed_checks),
                    'change': f"{(passed_checks/total_checks*100):.1f}%" if total_checks > 0 else "0%",
                    'change_type': 'positive',
                    'icon': '✅',
                    'description': 'Checks passed'
                },
                {
                    'title': 'Failed',
                    'value': str(failed_checks),
                    'change': f"{(failed_checks/total_checks*100):.1f}%" if total_checks > 0 else "0%",
                    'change_type': 'negative' if failed_checks > 0 else 'neutral',
                    'icon': '❌',
                    'description': 'Checks failed'
                },
                {
                    'title': 'Warnings',
                    'value': str(warnings),
                    'change_type': 'warning' if warnings > 0 else 'neutral',
                    'icon': '⚠️',
                    'description': 'Warnings issued'
                }
            ])
            
            self.create_metrics_grid(validation_metrics, columns=4)
            
            # Validation details
            if 'details' in validation_results:
                details = validation_results['details']
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'errors' in details and details['errors']:
                        st.markdown("#### ❌ Validation Errors")
                        for error in details['errors']:
                            self.components.create_validation_feedback(error, "error")
                
                with col2:
                    if 'warnings' in details and details['warnings']:
                        st.markdown("#### ⚠️ Validation Warnings")
                        for warning in details['warnings']:
                            self.components.create_validation_feedback(warning, "warning")
                            
        except Exception as e:
            logger.error(f"Error creating validation dashboard: {e}")
            st.error("Error creating validation dashboard")


# Global instance
dashboard_layout = DashboardLayoutManager()
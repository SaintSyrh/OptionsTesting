"""
Simplified Professional CSS for Streamlit
Guaranteed to work without encoding issues
"""

# Core professional styling that definitely works in Streamlit
CORE_CSS = """
<style>
    /* Import professional fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Main app styling */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #1E293B;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1E293B 0%, #334155 100%);
        border: 1px solid #475569;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        border-color: #3B82F6;
    }
    
    /* Status indicators */
    .status-success { color: #10B981; }
    .status-warning { color: #F59E0B; }
    .status-error { color: #EF4444; }
    .status-info { color: #3B82F6; }
    
    /* Professional buttons */
    .stButton > button {
        background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px -8px rgba(59, 130, 246, 0.5);
    }
    
    /* Form inputs */
    .stTextInput input, .stNumberInput input, .stSelectbox select {
        background-color: #334155 !important;
        color: #F8FAFC !important;
        border: 1px solid #475569 !important;
        border-radius: 6px !important;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #3B82F6 !important;
        box-shadow: 0 0 0 1px rgba(59, 130, 246, 0.3) !important;
    }
    
    /* Headers */
    h1 { color: #F8FAFC; font-weight: 700; }
    h2 { color: #CBD5E1; font-weight: 600; }
    h3 { color: #CBD5E1; font-weight: 500; }
    
    /* Tables */
    .stDataFrame {
        background-color: #1E293B;
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Progress bars */
    .stProgress > div > div {
        background: linear-gradient(90deg, #10B981 0%, #3B82F6 100%);
        border-radius: 4px;
    }
    
    /* Charts background */
    .js-plotly-plot {
        background-color: #1E293B !important;
        border-radius: 8px;
    }
    
    /* Success messages */
    .stSuccess {
        background-color: rgba(16, 185, 129, 0.1);
        border-left: 4px solid #10B981;
        color: #34D399;
    }
    
    /* Error messages */
    .stError {
        background-color: rgba(239, 68, 68, 0.1);
        border-left: 4px solid #EF4444;
        color: #F87171;
    }
    
    /* Warning messages */
    .stWarning {
        background-color: rgba(245, 158, 11, 0.1);
        border-left: 4px solid #F59E0B;
        color: #FBBF24;
    }
</style>
"""

# Professional header HTML
HEADER_HTML = """
<div style="background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem; text-align: center;">
    <h1 style="color: white; margin: 0; font-size: 2.5rem; font-weight: 700;">
        📈 Professional Options Pricing Platform
    </h1>
    <p style="color: #E2E8F0; margin: 0.5rem 0 0 0; font-size: 1.1rem;">
        Advanced Market Maker Valuation & Risk Management Suite
    </p>
</div>
"""

# Simple footer
FOOTER_HTML = """
<div style="text-align: center; padding: 2rem; color: #64748B; border-top: 1px solid #334155; margin-top: 3rem;">
    <p>Professional Options Pricing & Market Maker Valuation Platform</p>
    <p style="font-size: 0.9rem;">Built with sophisticated quantitative models for institutional use</p>
</div>
"""

# Color constants for components
FINANCIAL_COLORS = {
    'bull': '#10B981',
    'bear': '#EF4444',
    'neutral': '#64748B',
    'primary': '#3B82F6',
    'secondary': '#1E40AF',
    'accent': '#60A5FA',
    'warning': '#F59E0B',
    'info': '#0EA5E9'
}

CHART_COLORS = {
    'portfolio': ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'],
    'risk': ['#10B981', '#F59E0B', '#EF4444'],
    'greeks': ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6']
}

ICONS = {
    'success': '✅',
    'warning': '⚠️',  
    'error': '❌',
    'info': 'ℹ️',
    'entity': '🏢',
    'tranche': '📊',
    'depth': '💰',
    'calculation': '⚡'
}
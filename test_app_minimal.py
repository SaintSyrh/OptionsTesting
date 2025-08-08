"""
Minimal test version of the Streamlit app to isolate loading issues
"""

import streamlit as st
import traceback

# Minimal CSS that definitely works
MINIMAL_CSS = """
<style>
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    
    h1 { color: #F8FAFC; }
    h2 { color: #CBD5E1; }
    
    .stButton > button {
        background-color: #3B82F6;
        color: white;
        border: none;
        border-radius: 6px;
    }
</style>
"""

def main():
    """Minimal app for testing"""
    
    # Page config
    st.set_page_config(
        page_title="Options Pricing Test",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply minimal CSS
    st.markdown(MINIMAL_CSS, unsafe_allow_html=True)
    
    # Header
    st.title("📈 Options Pricing Calculator - Test Version")
    st.markdown("Testing basic functionality...")
    
    # Test sections
    st.subheader("🔧 System Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Status", "ONLINE", "✅")
    
    with col2:
        st.metric("Components", "Loading...", "⏳")
    
    with col3:
        st.metric("Tests", "Running", "🧪")
    
    # Test imports section
    st.subheader("📦 Component Tests")
    
    tests = []
    
    # Test 1: Basic components
    try:
        from ui.simple_components import simple_components
        tests.append("✅ Simple Components: OK")
    except Exception as e:
        tests.append(f"❌ Simple Components: {str(e)}")
    
    # Test 2: Session manager
    try:
        from app.session_state import session_manager
        tests.append("✅ Session Manager: OK")
    except Exception as e:
        tests.append(f"❌ Session Manager: {str(e)}")
    
    # Test 3: Option pricing
    try:
        from option_pricing import black_scholes_call
        price = black_scholes_call(100, 100, 1, 0.05, 0.2)
        tests.append(f"✅ Option Pricing: ${price:.2f}")
    except Exception as e:
        tests.append(f"❌ Option Pricing: {str(e)}")
    
    # Test 4: Depth models
    try:
        from depth_valuation import DepthValuationModels
        models = DepthValuationModels()
        tests.append("✅ Depth Models: OK")
    except Exception as e:
        tests.append(f"❌ Depth Models: {str(e)}")
    
    # Display test results
    for test in tests:
        st.write(test)
    
    st.markdown("---")
    
    # Interactive test
    st.subheader("🧮 Quick Option Pricing Test")
    
    with st.form("quick_test"):
        col1, col2 = st.columns(2)
        
        with col1:
            spot = st.number_input("Spot Price", value=100.0, min_value=0.1)
            strike = st.number_input("Strike Price", value=100.0, min_value=0.1)
            
        with col2:
            time_to_expiry = st.number_input("Time to Expiry (years)", value=1.0, min_value=0.001, max_value=5.0)
            volatility = st.number_input("Volatility", value=0.2, min_value=0.01, max_value=2.0)
        
        risk_free_rate = st.number_input("Risk-free Rate", value=0.05, min_value=-0.1, max_value=1.0)
        
        if st.form_submit_button("Calculate Option Price", type="primary"):
            try:
                from option_pricing import black_scholes_call, black_scholes_put, calculate_greeks
                
                call_price = black_scholes_call(spot, strike, time_to_expiry, risk_free_rate, volatility)
                put_price = black_scholes_put(spot, strike, time_to_expiry, risk_free_rate, volatility)
                greeks = calculate_greeks(spot, strike, time_to_expiry, risk_free_rate, volatility)
                
                st.success("✅ Calculation successful!")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Call Price", f"${call_price:.2f}")
                    st.metric("Delta", f"{greeks['delta']:.4f}")
                    st.metric("Gamma", f"{greeks['gamma']:.4f}")
                
                with col2:
                    st.metric("Put Price", f"${put_price:.2f}")
                    st.metric("Theta", f"{greeks['theta']:.4f}")
                    st.metric("Vega", f"{greeks['vega']:.4f}")
                
            except Exception as e:
                st.error(f"❌ Calculation failed: {str(e)}")
                st.code(traceback.format_exc())
    
    # Sidebar test
    with st.sidebar:
        st.header("🔧 Diagnostics")
        st.write("System Information:")
        st.write(f"- Streamlit Version: {st.__version__}")
        
        if st.button("Run System Check"):
            st.write("🔍 Running diagnostics...")
            
            # Check session state
            if hasattr(st, 'session_state'):
                st.write("✅ Session state available")
            else:
                st.write("❌ Session state not available")
            
            # Check if we can access configuration
            try:
                from config.simple_styles import FINANCIAL_COLORS
                st.write(f"✅ Config loaded: {len(FINANCIAL_COLORS)} colors")
            except Exception as e:
                st.write(f"❌ Config error: {str(e)}")

if __name__ == "__main__":
    main()
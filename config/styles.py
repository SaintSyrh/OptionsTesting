"""
Professional Financial Dashboard CSS Styles
Bloomberg/Refinitiv/TradingView-inspired design system
"""

# Professional Financial Dashboard CSS
MAIN_CSS = """
<style>
    /* Import professional fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500;600;700&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');
    
    /* Root variables for professional theme */
    :root {
        /* Dark Theme Colors */
        --primary-dark: #0A0E1A;
        --primary-deep: #0D1421;
        --primary-blue: #1E40AF;
        --accent-blue: #3B82F6;
        --accent-bright: #60A5FA;
        --success-green: #10B981;
        --success-light: #34D399;
        --danger-red: #EF4444;
        --danger-light: #F87171;
        --warning-yellow: #F59E0B;
        --warning-light: #FBBF24;
        
        /* Text Colors */
        --text-primary: #F8FAFC;
        --text-secondary: #CBD5E1;
        --text-muted: #64748B;
        --text-accent: #3B82F6;
        --text-success: #10B981;
        --text-warning: #F59E0B;
        --text-danger: #EF4444;
        
        /* Surface Colors */
        --border-color: #334155;
        --border-light: #475569;
        --card-bg: #1E293B;
        --card-bg-elevated: #334155;
        --sidebar-bg: #0F172A;
        --input-bg: #334155;
        --input-bg-focus: #475569;
        --hover-bg: #475569;
        --hover-bg-light: #64748B;
        
        /* Enhanced Shadows */
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.2);
        --shadow-xl: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        --shadow-2xl: 0 40px 80px -12px rgba(0, 0, 0, 0.7);
        --shadow-glow: 0 0 20px rgba(59, 130, 246, 0.15);
        
        /* Professional Gradients */
        --gradient-primary: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%);
        --gradient-primary-glow: linear-gradient(135deg, #1E40AF 0%, #60A5FA 100%);
        --gradient-success: linear-gradient(135deg, #059669 0%, #10B981 100%);
        --gradient-success-glow: linear-gradient(135deg, #059669 0%, #34D399 100%);
        --gradient-danger: linear-gradient(135deg, #DC2626 0%, #EF4444 100%);
        --gradient-warning: linear-gradient(135deg, #D97706 0%, #F59E0B 100%);
        --gradient-card: linear-gradient(145deg, #1E293B 0%, #334155 100%);
        --gradient-card-hover: linear-gradient(145deg, #334155 0%, #475569 100%);
        --gradient-surface: linear-gradient(145deg, #0F172A 0%, #1E293B 50%, #334155 100%);
        
        /* Financial Chart Colors */
        --bull-green: #10B981;
        --bear-red: #EF4444;
        --neutral-gray: #64748B;
        --volume-blue: #3B82F6;
        --volatility-orange: #F97316;
        
        /* Animation Variables */
        --transition-fast: 0.15s ease;
        --transition-normal: 0.3s ease;
        --transition-slow: 0.6s ease;
        --transition-elastic: cubic-bezier(0.68, -0.55, 0.265, 1.55);
        
        /* Spacing */
        --space-xs: 0.25rem;
        --space-sm: 0.5rem;
        --space-md: 1rem;
        --space-lg: 1.5rem;
        --space-xl: 2rem;
        --space-2xl: 3rem;
        
        /* Border Radius */
        --radius-sm: 6px;
        --radius-md: 8px;
        --radius-lg: 12px;
        --radius-xl: 16px;
        --radius-2xl: 20px;
    }
    
    /* Global styles */
    .stApp {
        background: linear-gradient(135deg, #0D1421 0%, #1E293B 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--text-primary);
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    
    /* Enhanced Professional Header */
    .main-header {
        font-size: clamp(2rem, 4vw, 3.5rem);
        font-weight: 800;
        background: var(--gradient-primary-glow);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: var(--space-2xl);
        padding: var(--space-xl) 0;
        position: relative;
        font-family: 'IBM Plex Sans', 'Inter', sans-serif;
        letter-spacing: -0.025em;
        animation: fadeInUp 0.8s ease-out;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 200px;
        height: 4px;
        background: var(--gradient-primary);
        border-radius: 2px;
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.4);
    }
    
    /* Enhanced Professional Card System */
    .financial-card {
        background: var(--gradient-card);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-xl);
        padding: var(--space-xl);
        margin: var(--space-lg) 0;
        box-shadow: var(--shadow-lg);
        backdrop-filter: blur(20px);
        transition: all var(--transition-normal);
        position: relative;
        overflow: hidden;
        transform: translateZ(0);
        will-change: transform, box-shadow;
    }
    
    .financial-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: var(--gradient-primary);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .financial-card:hover {
        transform: translateY(-4px) scale(1.002);
        box-shadow: var(--shadow-2xl), var(--shadow-glow);
        border-color: var(--accent-bright);
        background: var(--gradient-card-hover);
    }
    
    .financial-card:hover::before {
        opacity: 1;
    }
    
    /* Professional Metric Containers */
    .metric-container {
        background: var(--gradient-card);
        padding: var(--space-lg);
        border-radius: var(--radius-lg);
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-lg);
        transition: all var(--transition-normal);
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(15px);
    }
    
    .metric-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: var(--gradient-success-glow);
        transition: width var(--transition-normal);
        opacity: 0.8;
    }
    
    .metric-container:hover::before {
        width: 8px;
    }
    
    /* Professional entity sections */
    .entity-section {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: var(--shadow-lg);
        position: relative;
    }
    
    .entity-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: var(--gradient-primary);
    }
    
    /* Status indicators */
    .success-box {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.05) 100%);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: var(--success-green);
        padding: 1rem 1.5rem;
        border-radius: 8px;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .success-box::before {
        content: '✓';
        font-weight: 700;
        font-size: 1.1rem;
    }
    
    .error-section {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.05) 100%);
        border: 1px solid rgba(239, 68, 68, 0.3);
        color: var(--danger-red);
        padding: 1rem 1.5rem;
        border-radius: 8px;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .error-section::before {
        content: '⚠';
        font-weight: 700;
        font-size: 1.1rem;
    }
    
    .warning-section {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.05) 100%);
        border: 1px solid rgba(245, 158, 11, 0.3);
        color: var(--warning-yellow);
        padding: 1rem 1.5rem;
        border-radius: 8px;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .warning-section::before {
        content: '⚠';
        font-weight: 700;
        font-size: 1.1rem;
    }
    
    .info-section {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(30, 58, 138, 0.05) 100%);
        border: 1px solid rgba(59, 130, 246, 0.3);
        color: var(--accent-blue);
        padding: 1rem 1.5rem;
        border-radius: 8px;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .info-section::before {
        content: 'ⓘ';
        font-weight: 700;
        font-size: 1.1rem;
    }
    
    /* Phase indicators */
    .phase-indicator {
        background: var(--gradient-primary);
        color: white;
        text-align: center;
        font-weight: 600;
        padding: 1.5rem 2rem;
        margin: 2rem 0;
        border-radius: 12px;
        box-shadow: var(--shadow-lg);
        font-size: 1.1rem;
        letter-spacing: 0.025em;
        position: relative;
    }
    
    .phase-indicator::before {
        content: '';
        position: absolute;
        inset: 0;
        padding: 2px;
        background: var(--gradient-primary);
        border-radius: 12px;
        mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        mask-composite: xor;
        -webkit-mask-composite: xor;
    }
    
    /* Calculation section */
    .calculation-section {
        background: var(--card-bg);
        border: 2px solid var(--accent-blue);
        padding: 2rem;
        border-radius: 16px;
        margin: 2rem 0;
        box-shadow: var(--shadow-xl);
        position: relative;
    }
    
    .calculation-section::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: var(--gradient-primary);
        border-radius: 16px;
        z-index: -1;
        opacity: 0.5;
    }
    
    /* Enhanced Professional Buttons */
    .stButton > button {
        background: var(--gradient-primary) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        padding: 0.875rem 2rem !important;
        font-weight: 600 !important;
        font-size: 0.925rem !important;
        transition: all var(--transition-normal) !important;
        box-shadow: var(--shadow-lg) !important;
        font-family: 'Inter', sans-serif !important;
        position: relative !important;
        overflow: hidden !important;
        cursor: pointer !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: var(--shadow-xl), var(--shadow-glow) !important;
        background: var(--gradient-primary-glow) !important;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) scale(0.98) !important;
        transition: all 0.1s ease !important;
    }
    
    .stButton > button:focus {
        outline: 2px solid var(--accent-blue) !important;
        outline-offset: 2px !important;
    }
    
    /* Professional sidebar */
    .css-1d391kg {
        background: var(--sidebar-bg) !important;
        border-right: 1px solid var(--border-color) !important;
    }
    
    /* Professional inputs */
    .stNumberInput > div > div > input {
        background: var(--input-bg) !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-primary) !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    .stSelectbox > div > div > div {
        background: var(--input-bg) !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-primary) !important;
        border-radius: 8px !important;
    }
    
    /* Professional tables */
    .dataframe {
        background: var(--card-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }
    
    .dataframe th {
        background: var(--primary-blue) !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 1rem !important;
    }
    
    .dataframe td {
        background: var(--card-bg) !important;
        color: var(--text-primary) !important;
        padding: 0.75rem 1rem !important;
        border-bottom: 1px solid var(--border-color) !important;
    }
    
    /* Professional metrics */
    [data-testid="metric-container"] {
        background: var(--gradient-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        box-shadow: var(--shadow-lg) !important;
    }
    
    [data-testid="metric-container"] > div > div:first-child {
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
    }
    
    [data-testid="metric-container"] > div > div:nth-child(2) {
        color: var(--success-green) !important;
        font-weight: 700 !important;
        font-size: 1.5rem !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    /* Loading states */
    .stSpinner {
        border: 3px solid var(--border-color) !important;
        border-top: 3px solid var(--accent-blue) !important;
    }
    
    /* Professional forms */
    .stForm {
        background: var(--card-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 16px !important;
        padding: 2rem !important;
        box-shadow: var(--shadow-lg) !important;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--primary-dark);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--hover-bg);
    }
    
    /* Professional animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }
    
    .fade-in-up {
        animation: fadeInUp 0.6s ease-out;
    }
    
    .pulse-animation {
        animation: pulse 2s infinite;
    }
    
    /* Advanced Professional Components */
    .dashboard-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: var(--space-lg);
        margin: var(--space-xl) 0;
    }
    
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: var(--space-sm);
        padding: var(--space-sm) var(--space-md);
        border-radius: var(--radius-md);
        font-weight: 500;
        font-size: 0.875rem;
        transition: all var(--transition-normal);
    }
    
    .status-indicator.success {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.1) 100%);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: var(--success-green);
    }
    
    .status-indicator.warning {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(217, 119, 6, 0.1) 100%);
        border: 1px solid rgba(245, 158, 11, 0.3);
        color: var(--warning-yellow);
    }
    
    .status-indicator.error {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(220, 38, 38, 0.1) 100%);
        border: 1px solid rgba(239, 68, 68, 0.3);
        color: var(--danger-red);
    }
    
    .progress-indicator {
        position: relative;
        height: 6px;
        background: var(--input-bg);
        border-radius: var(--radius-sm);
        overflow: hidden;
        margin: var(--space-md) 0;
    }
    
    .progress-bar-enhanced {
        height: 100%;
        background: var(--gradient-primary);
        border-radius: var(--radius-sm);
        transition: width 0.8s ease;
        position: relative;
        overflow: hidden;
    }
    
    .progress-bar-enhanced::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    .summary-card {
        background: var(--gradient-card);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-xl);
        padding: var(--space-xl);
        box-shadow: var(--shadow-lg);
        transition: all var(--transition-normal);
        position: relative;
        overflow: hidden;
    }
    
    .summary-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--gradient-primary);
        opacity: 0;
        transition: opacity var(--transition-normal);
    }
    
    .summary-card:hover::before {
        opacity: 1;
    }
    
    .summary-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-xl);
        border-color: var(--accent-blue);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        color: var(--text-primary);
        margin: var(--space-sm) 0;
        line-height: 1.2;
    }
    
    .metric-label {
        font-size: 0.875rem;
        font-weight: 500;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: var(--space-xs);
    }
    
    .metric-change {
        display: flex;
        align-items: center;
        gap: var(--space-xs);
        font-size: 0.875rem;
        font-weight: 500;
        margin-top: var(--space-xs);
    }
    
    .metric-change.positive {
        color: var(--success-green);
    }
    
    .metric-change.negative {
        color: var(--danger-red);
    }
    
    .loading-skeleton {
        background: linear-gradient(90deg, var(--card-bg) 25%, var(--hover-bg) 50%, var(--card-bg) 75%);
        background-size: 200% 100%;
        animation: loading-shimmer 1.5s infinite;
        border-radius: var(--radius-md);
    }
    
    @keyframes loading-shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    
    .data-table-container {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-xl);
        overflow: hidden;
        box-shadow: var(--shadow-lg);
        margin: var(--space-lg) 0;
    }
    
    .table-header {
        background: var(--gradient-primary);
        padding: var(--space-lg);
        border-bottom: 1px solid var(--border-color);
    }
    
    .table-title {
        color: white;
        font-weight: 600;
        font-size: 1.125rem;
        margin: 0;
        display: flex;
        align-items: center;
        gap: var(--space-sm);
    }
    
    /* Enhanced Form Styling */
    .professional-form {
        background: var(--gradient-card);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-xl);
        padding: var(--space-2xl);
        box-shadow: var(--shadow-lg);
        position: relative;
        overflow: hidden;
    }
    
    .professional-form::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: var(--gradient-primary);
    }
    
    .form-section {
        margin: var(--space-xl) 0;
    }
    
    .form-section-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: var(--space-lg);
        display: flex;
        align-items: center;
        gap: var(--space-sm);
    }
    
    .input-group {
        margin-bottom: var(--space-lg);
    }
    
    .input-label {
        display: block;
        font-weight: 500;
        color: var(--text-secondary);
        margin-bottom: var(--space-sm);
        font-size: 0.875rem;
    }
    
    .validation-feedback {
        margin-top: var(--space-sm);
        padding: var(--space-sm) var(--space-md);
        border-radius: var(--radius-sm);
        font-size: 0.875rem;
        display: flex;
        align-items: center;
        gap: var(--space-sm);
    }
    
    .validation-feedback.success {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.05) 100%);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: var(--success-green);
    }
    
    .validation-feedback.error {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.05) 100%);
        border: 1px solid rgba(239, 68, 68, 0.3);
        color: var(--danger-red);
    }
    
    /* Advanced Animation System */
    .slide-in-up {
        animation: slideInUp 0.6s ease-out;
    }
    
    .slide-in-left {
        animation: slideInLeft 0.5s ease-out;
    }
    
    .slide-in-right {
        animation: slideInRight 0.5s ease-out;
    }
    
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
            padding: 1rem 0;
        }
        
        .financial-card, .entity-section {
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        .metric-container {
            padding: 1rem;
        }
    }
</style>
"""

# Professional phase-specific styles
PHASE_STYLES = {
    'entity_setup': """
    .entity-form {
        background: var(--gradient-card);
        padding: 2.5rem;
        border-radius: 16px;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-lg);
        position: relative;
        overflow: hidden;
    }
    
    .entity-form::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #10B981, #059669);
    }
    
    .entity-form h3 {
        color: var(--success-green);
        font-weight: 600;
        margin-bottom: 1.5rem;
        font-size: 1.25rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .entity-form h3::before {
        content: '🏢';
        font-size: 1.1rem;
    }
    """,
    
    'tranche_setup': """
    .tranche-form {
        background: var(--gradient-card);
        padding: 2.5rem;
        border-radius: 16px;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-lg);
        position: relative;
        overflow: hidden;
    }
    
    .tranche-form::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--gradient-primary);
    }
    
    .tranche-form h3 {
        color: var(--accent-blue);
        font-weight: 600;
        margin-bottom: 1.5rem;
        font-size: 1.25rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .tranche-form h3::before {
        content: '📊';
        font-size: 1.1rem;
    }
    """,
    
    'quoting_depths': """
    .depth-form {
        background: var(--gradient-card);
        padding: 2.5rem;
        border-radius: 16px;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-lg);
        position: relative;
        overflow: hidden;
    }
    
    .depth-form::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #F59E0B, #D97706);
    }
    
    .depth-form h3 {
        color: var(--warning-yellow);
        font-weight: 600;
        margin-bottom: 1.5rem;
        font-size: 1.25rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .depth-form h3::before {
        content: '💰';
        font-size: 1.1rem;
    }
    """
}

# Professional chart configuration
CHART_STYLE_CONFIG = {
    'figure_size': (14, 10),
    'title_fontsize': 16,
    'title_fontweight': '600',
    'label_fontsize': 13,
    'label_fontweight': '500',
    'tick_fontsize': 11,
    'legend_fontsize': 10,
    'grid_alpha': 0.15,
    'bar_alpha': 0.85,
    'line_width': 2.5,
    'background_color': '#1E293B',
    'text_color': '#F8FAFC',
    'grid_color': '#334155',
    'spine_color': '#475569',
    'font_family': 'Inter'
}

# Matplotlib style configurations
MATPLOTLIB_STYLES = {
    'bar_chart': {
        'alpha': 0.85,
        'edgecolor': '#475569',
        'linewidth': 1.0,
        'color': ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']
    },
    'line_chart': {
        'linewidth': 2.5,
        'marker': 'o',
        'markersize': 8,
        'markerfacecolor': '#3B82F6',
        'markeredgecolor': '#1E3A8A',
        'markeredgewidth': 1.5,
        'color': '#3B82F6'
    },
    'scatter_plot': {
        'alpha': 0.7,
        'edgecolors': '#334155',
        'linewidth': 1.0,
        's': 60,
        'c': '#10B981'
    },
    'stacked_bar': {
        'alpha': 0.85,
        'edgecolor': '#334155',
        'linewidth': 1.2,
    },
    'financial_candlestick': {
        'up_color': '#10B981',
        'down_color': '#EF4444',
        'wick_color': '#64748B',
        'alpha': 0.9
    }
}

# Professional footer HTML
FOOTER_HTML = """
<div style='
    text-align: center; 
    color: var(--text-secondary); 
    padding: 2rem; 
    border-top: 1px solid var(--border-color);
    background: var(--card-bg);
    margin-top: 3rem;
'>
    <div style='display: flex; justify-content: center; align-items: center; gap: 2rem; margin-bottom: 1rem;'>
        <div style='display: flex; align-items: center; gap: 0.5rem;'>
            <span style='color: var(--success-green); font-size: 1.2rem;'>📈</span>
            <strong style='color: var(--text-primary); font-weight: 600;'>Professional Options Pricing Suite</strong>
        </div>
    </div>
    <div style='display: flex; justify-content: center; gap: 2rem; font-size: 0.875rem; margin-bottom: 1rem;'>
        <span>🔬 <strong>Black-Scholes Model</strong></span>
        <span>🏦 <strong>Depth Analysis</strong></span>
        <span>⚡ <strong>Real-time Valuation</strong></span>
        <span>📊 <strong>Risk Analytics</strong></span>
    </div>
    <p style='margin: 0; font-size: 0.8rem; opacity: 0.7;'>
        <em>Institutional-grade derivatives pricing and portfolio analysis platform</em>
    </p>
</div>
"""

# Professional component styles
COMPONENT_STYLES = {
    'progress_bar': """
    .progress-container {
        background: var(--input-bg);
        border-radius: 10px;
        overflow: hidden;
        height: 8px;
        margin: 1rem 0;
    }
    
    .progress-bar {
        height: 100%;
        background: var(--gradient-primary);
        transition: width 0.3s ease;
        border-radius: 10px;
    }
    """,
    
    'tooltip': """
    .custom-tooltip {
        background: var(--primary-dark);
        color: var(--text-primary);
        padding: 0.75rem 1rem;
        border-radius: 8px;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-xl);
        font-size: 0.875rem;
        max-width: 300px;
        z-index: 1000;
    }
    """,
    
    'loading_spinner': """
    .professional-spinner {
        border: 3px solid var(--border-color);
        border-top: 3px solid var(--accent-blue);
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 2rem auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    """,
    
    'data_table': """
    .professional-table {
        width: 100%;
        border-collapse: collapse;
        background: var(--card-bg);
        border-radius: 12px;
        overflow: hidden;
        box-shadow: var(--shadow-lg);
        margin: 1rem 0;
    }
    
    .professional-table th {
        background: var(--primary-blue);
        color: white;
        padding: 1rem;
        text-align: left;
        font-weight: 600;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }
    
    .professional-table td {
        padding: 0.75rem 1rem;
        border-bottom: 1px solid var(--border-color);
        color: var(--text-primary);
        font-family: 'JetBrains Mono', monospace;
    }
    
    .professional-table tbody tr:hover {
        background: var(--hover-bg);
        cursor: pointer;
    }
    """
}

# Professional icon mappings
ICONS = {
    'entity': '🏢',
    'tranche': '📊',
    'depth': '💰',
    'calculation': '⚡',
    'success': '✅',
    'warning': '⚠️',
    'error': '❌',
    'info': 'ℹ️',
    'loading': '⏳',
    'export': '📥',
    'settings': '⚙️',
    'analytics': '📈',
    'portfolio': '💼',
    'risk': '🎯',
    'performance': '🚀'
}

# Financial color palette for charts and indicators
FINANCIAL_COLORS = {
    'bull': '#10B981',      # Success green for gains
    'bear': '#EF4444',      # Danger red for losses  
    'neutral': '#64748B',   # Muted gray for neutral
    'primary': '#3B82F6',   # Primary blue
    'secondary': '#1E40AF', # Dark blue
    'accent': '#60A5FA',    # Light blue
    'warning': '#F59E0B',   # Warning yellow
    'info': '#0EA5E9',      # Info cyan
    'purple': '#8B5CF6',    # Purple accent
    'orange': '#F97316',    # Orange accent
    'pink': '#EC4899',      # Pink accent
    'indigo': '#6366F1'     # Indigo accent
}

# Chart color schemes for different visualizations
CHART_COLORS = {
    'portfolio': ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#F97316'],
    'risk': ['#10B981', '#F59E0B', '#EF4444'],
    'performance': ['#3B82F6', '#1E40AF', '#60A5FA', '#0EA5E9'],
    'greeks': ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6'],
    'depth': ['#1E40AF', '#3B82F6', '#60A5FA', '#0EA5E9', '#06B6D4'],
    'heatmap': ['#EF4444', '#F59E0B', '#10B981']
}

# Professional theme configurations
THEMES = {
    'dark': {
        'primary': '#1E3A8A',
        'secondary': '#3B82F6',
        'success': '#10B981',
        'danger': '#EF4444',
        'warning': '#F59E0B',
        'background': '#0D1421',
        'surface': '#1E293B',
        'text_primary': '#F8FAFC',
        'text_secondary': '#CBD5E1',
        'border': '#334155'
    },
    'light': {
        'primary': '#3B82F6',
        'secondary': '#1E3A8A',
        'success': '#059669',
        'danger': '#DC2626',
        'warning': '#D97706',
        'background': '#F8FAFC',
        'surface': '#FFFFFF',
        'text_primary': '#0F172A',
        'text_secondary': '#475569',
        'border': '#E2E8F0'
    }
}

# Responsive breakpoints
BREAKPOINTS = {
    'mobile': '768px',
    'tablet': '1024px',
    'desktop': '1280px',
    'wide': '1536px'
}

# Animation configurations
ANIMATIONS = {
    'duration_fast': '0.2s',
    'duration_normal': '0.3s',
    'duration_slow': '0.6s',
    'easing_ease': 'ease',
    'easing_ease_in_out': 'ease-in-out',
    'easing_ease_out': 'ease-out'
}
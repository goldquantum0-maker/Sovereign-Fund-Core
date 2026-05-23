import streamlit as st
import pandas as pd
from sovereign_board import sovereign_board # Import the compiled LangGraph board

# --- 1. THE SOVEREIGN AESTHETIC (Custom CSS) ---
st.set_page_config(page_title="Sovereign Fund Capital LLC", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #0A0A0A;
        color: #D4AF37;
    }
    h1, h2, h3 {
        font-family: 'Cormorant Garamond', serif !important;
        color: #D4AF37 !important;
    }
    .stButton>button {
        background-color: #D4AF37 !important;
        color: black !important;
        font-weight: bold !important;
        border-radius: 0px !important;
        border: 1px solid #D4AF37 !important;
    }
    .report-box {
        background-color: #1A1A1A;
        border: 1px solid #D4AF37;
        padding: 20px;
        border-radius: 5px;
        font-family: 'Courier Prime', monospace;
        color: #E0E0E0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR NAVIGATION ---
st.sidebar.title("SFC COMMAND")
page = st.sidebar.radio("Navigation", ["Overview", "Assets", "Board Room", "Reports", "Intelligence"])

# --- 3. PAGE LOGIC ---

if page == "Overview":
    st.title("Sovereign Fund Capital LLC")
    st.subheader("Executive Command Center")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Account Balance", "$4,800", "Leveraged")
    col2.metric("Sovereign Edge", "80%", "Target Win Rate")
    col3.metric("Risk Status", "Sentry Active", "Vostok-Sovereign")

    st.markdown("---")
    st.write("Welcome, Chairman Osinachi Chukwu. The board is standing by for instructions.")

elif page == "Board Room":
    st.title("AI Board of Directors")
    
    if st.button("CONVENE THE BOARD"):
        with st.spinner("Board is debating... Please wait..."):
            # This triggers the LangGraph orchestrator we built in Sprint 3
            initial_state = {
                "regime": "", "leads": [], "active_ticker": None, 
                "blueprint": None, "risk_approved": False, "risk_notes": "", "final_briefing": ""
            }
            result = sovereign_board.invoke(initial_state)
            
            st.markdown(f'<div class="report-box">{result["final_briefing"]}</div>', unsafe_allow_html=True)
            
            if result['risk_approved']:
                st.success(f"Sovereign Directive: EXECUTE {result['active_ticker']}")
            else:
                st.error("Sovereign Directive: TRADE REJECTED BY VOSTOK")

elif page == "Assets":
    st.title("Asset Command Panel")
    # Mock-up for your Live Visibility
    df = pd.DataFrame({
        'Asset': ['XAU/USD', 'NVDA', 'GLD', 'AAPL', 'BTC', 'EUR/USD'],
        'Allocation': ['20%', '15%', '10%', '10%', '15%', '30%'],
        'P&L': ['+$120', '+$450', '-$20', '+$110', '+$300', '+$10'],
        'Status': ['Holding', 'Holding', 'Stop-Loss', 'Holding', 'Hedge', 'Holding']
    })
    st.table(df)

elif page == "Intelligence":
    st.title("Sovereign Intel Feed")
    st.info("Scanning Dark Pools and Institutional 13F Filings...")
    # Here we would stream the output of the Amazon-Sovereign agent
    st.write("💎 [INSTITUTIONAL] Accumulation detected in XAU/USD - High Conviction")
    st.write("💣 [SURE-LEVERAGE] Volatility spike in Tech sector - Caution Advised")


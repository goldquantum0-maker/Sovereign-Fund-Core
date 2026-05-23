import os
import requests
import pandas as pd
import numpy as np
import yfinance as yf
from typing import TypedDict, List, Optional
from dotenv import load_dotenv

# Cloud & AI Imports
from huggingface_hub import InferenceClient
from serpapi import GoogleSearch
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
import streamlit as st

load_dotenv()

# =============================================================================
# SECTION 1: THE SOVEREIGN AGENTS (Internal Classes)
# =============================================================================

class RhineMacro:
    """The Architect: Sets the Global Market Regime via FRED."""
    def __init__(self):
        self.api_key = os.getenv("FRED_API_KEY")
        self.base_url = "https://api.stlouisfed.org/fred/"

    def fetch_fred_series(self, series_id):
        params = {"series_id": series_id, "api_key": self.api_key, "filetype": "json", "limit": 1}
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return float(response.json()['observations'][0]['value'])
        except: return None

    def determine_regime(self):
        yield_10y = self.fetch_fred_series("DGS10")
        cpi = self.fetch_fred_series("CPIAUCSL")
        if yield_10y is None or cpi is None: return "🟡 REGIME: UNKNOWN"
        if yield_10y > 4.2: return "🔴 RISK-OFF"
        elif yield_10y < 3.5: return "🟢 RISK-ON"
        else: return "🟡 NEUTRAL"

class AmazonIntel:
    """The Spy: Finds institutional flow and sentiment."""
    def __init__(self):
        self.serp_key = os.getenv("SERPAPI_KEY")
        self.hf_client = InferenceClient(token=os.getenv("HUGGINGFACE_TOKEN"))
        self.finbert_model = "ProsusAI/finbert"

    def get_sentiment(self, text):
        try:
            result = self.hf_client.text_classification(text, model=self.finbert_model)
            return result[0]['label'], result[0]['score']
        except: return "neutral", 0.0

    def scout_trades(self, regime):
        if "🔴 RISK-OFF" in regime: query = "institutional accumulation gold treasury defensive stocks 13F"
        elif "🟢 RISK-ON" in regime: query = "institutional accumulation AI tech growth stocks dark pool 13F"
        else: query = "top institutional buys blue chip value stocks 13F"
        try:
            search = GoogleSearch("Sovereign-Intel", "apiKey", self.serp_key)
            results = search.get_dict()
            snippets = [res['snippet'] for res in results.get('organic_results', [])[:3]]
            leads = []
            for text in snippets:
                sentiment, score = self.get_sentiment(text)
                if sentiment == "positive" and score > 0.75:
                    leads.append({"evidence": text, "score": score})
            return leads if leads else None
        except: return None

class KyotoQuant:
    """The Mathematician: Generates the surgical trade blueprint."""
    def __init__(self):
        self.min_risk_reward = 3.0 
        self.max_account_risk = 0.015 

    def calculate_volatility(self, ticker):
        try:
            df = yf.download(ticker, period="1mo", interval="1d", progress=False)
            high_low = df['High'] - df['Low']
            high_close = np.abs(df['High'] - df['Close'].shift())
            low_close = np.abs(df['Low'] - df['Close'].shift())
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            return np.max(ranges, axis=1).rolling(14).mean().iloc[-1]
        except: return 2.0

    def create_blueprint(self, ticker, account_balance=4800):
        try:
            data = yf.Ticker(ticker).history(period="1d")
            current_price = data['Close'].iloc[-1]
            atr = self.calculate_volatility(ticker)
            stop_loss = current_price - (atr * 2)
            risk_per_share = current_price - stop_loss
            take_profit = current_price + (risk_per_share * self.min_risk_reward)
            max_dollar_risk = account_balance * self.max_account_risk
            shares_to_buy = int(max_dollar_risk / risk_per_share)
            return {"ticker": ticker, "entry": round(current_price, 2), "stop": round(stop_loss, 2), 
                    "tp": round(take_profit, 2), "size": shares_to_buy, "risk_usd": round(max_dollar_risk, 2)}
        except: return None

class VostokRisk:
    """The Sentinel: The final gatekeeper."""
    def validate(self, blueprint, current_balance=4800):
        if not blueprint: return False, "No blueprint provided."
        if blueprint['risk_usd'] > (current_balance * 0.015): return False, "Risk exceeds 1.5% threshold."
        risk = blueprint['entry'] - blueprint['stop']
        reward = blueprint['tp'] - blueprint['entry']
        if reward / risk < 3.0: return False, "Risk/Reward ratio insufficient."
        return True, "All risk parameters validated."

# =============================================================================
# SECTION 2: THE LANGGRAPH ORCHESTRATOR
# =============================================================================

class FundState(TypedDict):
    regime: str
    leads: List[dict]
    active_ticker: Optional[str]
    blueprint: Optional[dict]
    risk_approved: bool
    risk_notes: str
    final_briefing: str

def rhine_node(state: FundState):
    return {"regime": RhineMacro().determine_regime()}

def amazon_node(state: FundState):
    leads = AmazonIntel().scout_trades(state['regime'])
    active_ticker = "NVDA" if leads else None # Simulation
    return {"leads": leads if leads else [], "active_ticker": active_ticker}

def kyoto_node(state: FundState):
    if not state['active_ticker']: return {"blueprint": None}
    return {"blueprint": KyotoQuant().create_blueprint(state['active_ticker'])}

def vostok_node(state: FundState):
    if not state['blueprint']: return {"risk_approved": False, "risk_notes": "No blueprint."}
    approved, notes = VostokRisk().validate(state['blueprint'])
    return {"risk_approved": approved, "risk_notes": notes}

def secretary_node(state: FundState):
    try:
        llm = ChatOpenAI(
            model="mistralai/mistral-7b-instruct",
            openai_api_key=os.getenv("OPENROUTER_API_KEY"),
            openai_api_base="https://openrouter.ai/api/v1",
        )
        prompt = f"Regime: {state['regime']}\nIntel: {state['leads']}\nBlueprint: {state['blueprint']}\nRisk: {state['risk_notes']}\nApproved: {state['risk_approved']}. Write professional briefing for Chairman Osinachi Chukwu."
        return {"final_briefing": llm.invoke(prompt).content}
    except:
        return {"final_briefing": "The Secretary is unable to reach the LLM. Please check API keys."}

# Build Graph
workflow = StateGraph(FundState)
workflow.add_node("rhine", rhine_node)
workflow.add_node("amazon", amazon_node)
workflow.add_node("kyoto", kyoto_node)
workflow.add_node("vostok", vostok_node)
workflow.add_node("alps", secretary_node)
workflow.set_entry_point("rhine")
workflow.add_edge("rhine", "amazon")
workflow.add_edge("amazon", "kyoto")
workflow.add_edge("kyoto", "vostok")
workflow.add_edge("vostok", "alps")
workflow.add_edge("alps", END)
sovereign_board = workflow.compile()

# =============================================================================
# SECTION 3: THE STREAMLIT UI (Sovereign Dashboard)
# =============================================================================

st.set_page_config(page_title="Sovereign Fund Capital LLC", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0A0A0A; color: #D4AF37; }
    h1, h2, h3 { font-family: 'Cormorant Garamond', serif !important; color: #D4AF37 !important; }
    .report-box { background-color: #1A1A1A; border: 1px solid #D4AF37; padding: 20px; border-radius: 5px; font-family: 'Courier Prime', monospace; color: #E0E0E0; }
    </style>
    """, unsafe_allow_html=True)

st.sidebar.title("SFC COMMAND")
page = st.sidebar.radio("Navigation", ["Overview", "Assets", "Board Room", "Intelligence"])

if page == "Overview":
    st.title("Sovereign Fund Capital LLC")
    st.subheader("Executive Command Center")
    col1, col2, col3 = st.columns(3)
    col1.metric("Account Balance", "$4,800", "Leveraged")
    col2.metric("Sovereign Edge", "80%", "Target Win Rate")
    col3.metric("Risk Status", "Sentry Active", "Vostok-Sovereign")

elif page == "Board Room":
    st.title("AI Board of Directors")
    if st.button("CONVENE THE BOARD"):
        with st.spinner("Board is debating..."):
            initial_state = {"regime": "", "leads": [], "active_ticker": None, "blueprint": None, "risk_approved": False, "risk_notes": "", "final_briefing": ""}
            result = sovereign_board.invoke(initial_state)
            st.markdown(f'<div class="report-box">{result["final_briefing"]}</div>', unsafe_allow_html=True)
            if result['risk_approved']: st.success(f"Sovereign Directive: EXECUTE {result['active_ticker']}")
            else: st.error("Sovereign Directive: TRADE REJECTED BY VOSTOK")

elif page == "Assets":
    st.title("Asset Command Panel")
    df = pd.DataFrame({'Asset': ['XAU/USD', 'NVDA', 'GLD'], 'Allocation': ['20%', '15%', '10%'], 'P&L': ['+$120', '+$450', '-$20']})
    st.table(df)

elif page == "Intelligence":
    st.title("Sovereign Intel Feed")
    st.info("Scanning Dark Pools...")
    st.write("💎 [INSTITUTIONAL] Accumulation detected in XAU/USD")

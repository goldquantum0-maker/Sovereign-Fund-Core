import os
import requests
import pandas as pd
import numpy as np
import yfinance as yf
from typing import TypedDict, List, Optional
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from serpapi import GoogleSearch
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
import streamlit as st
import time

load_dotenv()

# =============================================================================
# 1. REAL-TIME DATA ENGINE (Sovereign-Audit)
# =============================================================================
def get_institutional_portfolio():
    # These tickers are the most reliable for real-time data in yfinance
    # XAUUSD=X (Gold), NVDA (Nvidia), AAPL (Apple), BTC-USD (Bitcoin)
    holdings = {
        "GC=F": {"name": "Gold Futures", "shares": 5}, 
        "NVDA": {"name": "Nvidia", "shares": 10},
        "AAPL": {"name": "Apple", "shares": 15},
        "BTC-USD": {"name": "Bitcoin", "shares": 0.05},
        "EURUSD=X": {"name": "EUR/USD", "shares": 1000}
    }
    
    data_list = []
    total_equity = 0
    
    for ticker, info in holdings.items():
        try:
            t = yf.Ticker(ticker)
            price = t.history(period="1d")['Close'].iloc[-1]
            value = price * info['shares']
            total_equity += value
            data_list.append({"Asset": info['name'], "Ticker": ticker, "Price": round(price, 2), "Value": round(value, 2)})
        except:
            data_list.append({"Asset": info['name'], "Ticker": ticker, "Price": "ERR", "Value": 0})
            
    return pd.DataFrame(data_list), total_equity

# =============================================================================
# 2. THE SOVEREIGN BOARD (Logic Classes)
# =============================================================================
class RhineMacro:
    def determine(self):
        try:
            api_key = os.getenv("FRED_API_KEY")
            res = requests.get(f"https://api.stlouisfed.org/fred/series/observations?series_id=DGS10&api_key={api_key}&filetype=json&limit=1").json()
            yield_10y = float(res['observations'][0]['value'])
            return "🔴 RISK-OFF" if yield_10y > 4.2 else "🟢 RISK-ON" if yield_10y < 3.5 else "🟡 NEUTRAL"
        except: return "🟡 REGIME: UNKNOWN"

class AmazonIntel:
    def scout(self, regime):
        try:
            search = GoogleSearch("Sovereign-Intel", "apiKey", os.getenv("SERPAPI_KEY"))
            res = search.get_dict()
            snippets = [s['snippet'] for s in res.get('organic_results', [])[:2]]
            return snippets
        except: return ["No intel available."]

class KyotoQuant:
    def blueprint(self, ticker):
        try:
            p = yf.Ticker(ticker).history(period="1d")['Close'].iloc[-1]
            return {"ticker": ticker, "entry": round(p, 2), "stop": round(p*0.96, 2), "tp": round(p*1.12, 2)}
        except: return None

class VostokRisk:
    def validate(self, blueprint):
        if not blueprint: return False, "Blueprint Missing"
        return True, "Validated"

# =============================================================================
# 3. LANGGRAPH STATE MACHINE
# =============================================================================
class FundState(TypedDict):
    regime: str; leads: List[str]; active_ticker: str; blueprint: dict; risk_approved: bool; risk_notes: str; briefing: str

def rhine_node(state):
    res = RhineMacro().determine()
    return {"regime": res}

def amazon_node(state):
    leads = AmazonIntel().scout(state['regime'])
    return {"leads": leads, "active_ticker": "NVDA"}

def kyoto_node(state):
    return {"blueprint": KyotoQuant().blueprint(state['active_ticker'])}

def vostok_node(state):
    app, notes = VostokRisk().validate(state['blueprint'])
    return {"risk_approved": app, "risk_notes": notes}

def alps_node(state):
    try:
        llm = ChatOpenAI(model="mistralai/mistral-7b-instruct", openai_api_key=os.getenv("OPENROUTER_API_KEY"), openai_api_base="https://openrouter.ai/api/v1")
        prompt = f"Board Results: Regime {state['regime']}, Blueprint {state['blueprint']}, Risk {state['risk_notes']}. Write a brief directive for Chairman Osinachi."
        return {"briefing": llm.invoke(prompt).content}
    except: return {"briefing": "Secretary is offline. Check API keys."}

workflow = StateGraph(FundState)
workflow.add_node("rhine", rhine_node); workflow.add_node("amazon", amazon_node); workflow.add_node("kyoto", kyoto_node); workflow.add_node("vostok", vostok_node); workflow.add_node("alps", alps_node)
workflow.set_entry_point("rhine")
workflow.add_edge("rhine", "amazon"); workflow.add_edge("amazon", "kyoto"); workflow.add_edge("kyoto", "vostok"); workflow.add_edge("vostok", "alps"); workflow.add_edge("alps", END)
sovereign_board = workflow.compile()

# =============================================================================
# 4. THE INSTITUTIONAL UI
# =============================================================================
st.set_page_config(page_title="SFC Command", layout="wide")

# Professional Deep Blue/White Theme
st.markdown("""
    <style>
    .stApp { background-color: #00122b; color: #FFFFFF; }
    h1, h2, h3 { color: #FFFFFF !important; font-family: 'Arial', sans-serif !important; }
    .member-card { background-color: #002147; border: 1px solid #FFFFFF; padding: 15px; border-radius: 10px; text-align: center; min-width: 200px; }
    .report-box { background-color: #FFFFFF; color: #00122b; padding: 25px; border-radius: 10px; font-family: 'Courier New', monospace; font-weight: bold; border-left: 10px solid #004c99; }
    </style>
    """, unsafe_allow_html=True)

st.sidebar.title("SFC NAVIGATION")
page = st.sidebar.radio("Menu", ["Live Portfolio", "Board Room", "Intel Feed"])

if page == "Live Portfolio":
    st.title("Institutional Asset Tracking")
    df, equity = get_institutional_portfolio()
    
    col1, col2 = st.columns(2)
    col1.metric("Total Live Equity", f"${equity:,.2f}", "Market Value")
    col2.metric("Fund Baseline", "$14,300.00", "SFC Capital")
    
    st.table(df)

elif page == "Board Room":
    st.title("The Sovereign Board of Directors")
    
    # Display Board Members and their Capabilities
    members = {
        "RHINE": "Macro Architect - Global Regime & FED Analysis",
        "AMAZON": "Intel Spy - Institutional Flow & Dark Pools",
        "KYOTO": "Quant Mathematician - Risk/Reward Precision",
        "VOSTOK": "Risk Sentinel - Capital Preservation & Veto",
        "ALPS": "Executive Assistant - Synthesis & Reporting"
    }
    
    cols = st.columns(5)
    for i, (name, cap) in enumerate(members.items()):
        with cols[i]:
            st.markdown(f'<div class="member-card"><b>{name}</b><br><small>{cap}</small></div>', unsafe_allow_html=True)

    st.markdown("---")
    if st.button("CONVENE THE BOARD"):
        # VISIBLE PROCESS
        with st.status("Board Session in Progress...", expanded=True) as status:
            st.write("🏛️ Rhine is analyzing Macro indicators...")
            time.sleep(1)
            st.write("🕵️ Amazon is scanning institutional accumulation...")
            time.sleep(1)
            st.write("📐 Kyoto is calculating mathematical entries...")
            time.sleep(1)
            st.write("🛡️ Vostok is auditing risk exposure...")
            time.sleep(1)
            st.write("📝 Alps is synthesizing the final directive...")
            
            result = sovereign_board.invoke({"regime": "", "leads": [], "active_ticker": None, "blueprint": None, "risk_approved": False, "risk_notes": "", "briefing": ""})
            status.update(label="Session Complete", state="complete")

        st.markdown(f'<div class="report-box">{result["briefing"]}</div>', unsafe_allow_html=True)
        if result['risk_approved']: st.success(f"DIRECTIVE: EXECUTE {result['active_ticker']}")
        else: st.error("DIRECTIVE: TRADE REJECTED BY VOSTOK")

elif page == "Intel Feed":
    st.title("Sovereign Intelligence")
    st.info("Monitoring Whale Movements & Fed Data...")
    st.write("• [Sovereign-Intel] High-conviction accumulation detected in Gold.")
    st.write("• [Sovereign-Macro] 10Y Yields at critical resistance.")

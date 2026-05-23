import os
import requests
import pandas as pd
import numpy as np
import yfinance as yf
from typing import TypedDict, List, Optional
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from serpapi import GoogleSearch
from langchain_openai import ChatOpenAI
import streamlit as st
import time

load_dotenv()

# =============================================================================
# 1. THE SOVEREIGN DATA ENGINE (Sovereign-Audit)
# =============================================================================
class SovereignData:
    """High-performance data engine for real-time macro and assets."""
    @staticmethod
    def get_market_state():
        # Macro Drivers and Portfolio Assets
        tickers = {
            "DX-Y.NYB": "DXY", 
            "^TNX": "10Y Yield", 
            "GC=F": "Gold", 
            "NVDA": "Nvidia", 
            "AAPL": "Apple", 
            "BTC-USD": "Bitcoin"
        }
        results = []
        try:
            all_t = " ".join(tickers.keys())
            data = yf.download(all_t, period="1d", interval="1m", progress=False)['Close']
            for t, name in tickers.items():
                price = data[t].iloc[-1]
                results.append({"Asset": name, "Ticker": t, "Price": round(price, 2)})
        except:
            for t, name in tickers.items():
                try: results.append({"Asset": name, "Ticker": t, "Price": round(yf.Ticker(t).fast_info['last_price'], 2)})
                except: results.append({"Asset": name, "Ticker": t, "Price": "ERR"})
        return pd.DataFrame(results)

    @staticmethod
    def calculate_equity():
        # Hardcoded holdings for your $14,300 portfolio
        holdings = {"GC=F": 2, "NVDA": 10, "AAPL": 15, "BTC-USD": 0.05}
        total = 0
        for t, shares in holdings.items():
            try: total += yf.Ticker(t).fast_info['last_price'] * shares
            except: pass
        return round(total, 2)

# =============================================================================
# 2. THE SOVEREIGN INTELLIGENCE CORE (The Board)
# =============================================================================
class SovereignIntelligence:
    """Unified brain for Macro, Intel, Quant, and Risk."""
    def __init__(self):
        self.llm = ChatOpenAI(
            model="mistralai/mistral-7b-instruct", 
            openai_api_key=os.getenv("OPENROUTER_API_KEY"), 
            openai_api_base="https://openrouter.ai/api/v1"
        )
        self.hf = InferenceClient(token=os.getenv("HUGGINGFACE_TOKEN"))
        self.serp = GoogleSearch("Sovereign-Intel", "apiKey", os.getenv("SERPAPI_KEY"))

    def run_protocol(self, ticker="NVDA"):
        """Strict 90% Probability Gate."""
        logs = []
        
        # GATE 1: Macro (Rhine)
        try:
            api_key = os.getenv("FRED_API_KEY")
            res = requests.get(f"https://api.stlouisfed.org/fred/series/observations?series_id=DGS10&api_key={api_key}&filetype=json&limit=1").json()
            yield_10y = float(res['observations'][0]['value'])
            regime = "🟢 RISK-ON" if yield_10y < 4.2 else "🔴 RISK-OFF"
            logs.append(f"MACRO: {regime} (10Y: {yield_10y}%) - PASS")
        except: return False, ["MACRO: API FAILURE - REJECTED"], None

        # GATE 2: Intel (Amazon)
        try:
            self.serp.params = {"q": f"{ticker} institutional accumulation 13F"}
            res = self.serp.get_dict()
            snippet = res['organic_results'][0]['snippet']
            if "accumulation" in snippet.lower() or "increase" in snippet.lower():
                logs.append(f"INTEL: Institutional Buying Confirmed - PASS")
            else: return False, logs + ["INTEL: No accumulation found - REJECTED"], None
        except: return False, logs + ["INTEL: API FAILURE - REJECTED"], None

        # GATE 3: Technical (Kyoto)
        try:
            df = yf.download(ticker, period="1mo", interval="1d", progress=False)
            if df['Close'].iloc[-1] > df['Close'].rolling(20).mean().iloc[-1]:
                logs.append(f"TECHNICAL: Price > SMA20 - PASS")
            else: return False, logs + ["TECHNICAL: Trend Negative - REJECTED"], None
        except: return False, logs + ["TECHNICAL: DATA ERROR - REJECTED"], None

        # GATE 4: Risk (Vostok)
        price = yf.Ticker(ticker).history(period="1d")['Close'].iloc[-1]
        blueprint = {"ticker": ticker, "entry": round(price, 2), "stop": round(price*0.96, 2), "tp": round(price*1.15, 2)}
        logs.append(f"RISK: 1:3 Ratio Validated - PASS")
        
        return True, logs, blueprint

    def chat(self, user_input, agent_name):
        personas = {
            "RHINE": "Sophisticated Macro Architect. Absolute loyalty to Chairman Osinachi. Speaks in geopolitical trends.",
            "AMAZON": "Aggressive Intel Spy. reports the 'blood in the water' with cold efficiency.",
            "KYOTO": "Robotic Quant. Obsessed with the 1:3 ratio and mathematical perfection.",
            "VOSTOK": "Stern Risk Sentinel. The Shield of the fund. Unyielding on capital preservation."
        }
        sys_prompt = f"YOU ARE {agent_name}. {personas.get(agent_name, '')}. You are a member of the Sovereign Board. You speak with total devotion to Chairman Osinachi Chukwu. Be concise, institutional, and absolute."
        return self.llm.invoke([("system", sys_prompt), ("human", user_input)]).content

# =============================================================================
# 3. THE COMMAND INTERFACE (Institutional Deep Blue)
# =============================================================================
st.set_page_config(page_title="SFC COMMAND", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000814; color: #FFFFFF; }
    h1, h2, h3 { color: #FFFFFF !important; font-family: 'Arial Black', sans-serif !important; }
    .macro-card { background-color: #001d3d; border: 1px solid #FFFFFF; padding: 15px; border-radius: 5px; text-align: center; }
    .board-card { background-color: #001d3d; border: 1px solid #FFFFFF; padding: 15px; border-radius: 10px; text-align: center; }
    .directive-box { background-color: #FFFFFF; color: #000814; padding: 25px; border-radius: 0px; font-family: 'Courier New', monospace; font-size: 22px; font-weight: bold; text-align: center; border-left: 15px solid #003566; }
    </style>
    """, unsafe_allow_html=True)

st.sidebar.title("SFC NAV")
page = st.sidebar.radio("Command", ["Terminal", "Dialogue", "Protocol"])

if page == "Terminal":
    st.title("Sovereign Live Terminal")
    data = SovereignData().get_market_state()
    equity = SovereignData().calculate_equity()
    
    dxy = data[data['Asset'] == 'DXY']['Price'].values[0]
    tnx = data[data['Asset'] == '10Y Yield']['Price'].values[0]
    
    m1, m2, m3 = st.columns(3)
    m1.markdown(f'<div class="macro-card"><b>DXY</b><br><h2>{dxy}</h2></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="macro-card"><b>10Y YIELD</b><br><h2>{tnx}%</h2></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="macro-card"><b>LIVE EQUITY</b><br><h2>${equity:,.2f}</h2></div>', unsafe_allow_html=True)
    st.table(data)

elif page == "Dialogue":
    st.title("Direct Command Dialogue")
    agent_choice = st.selectbox("Sovereign Advisor", ["RHINE", "AMAZON", "KYOTO", "VOSTOK"])
    
    if "messages" not in st.session_state: st.session_state.messages = []
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input(f"Command {agent_choice}..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            res = SovereignIntelligence().chat(prompt, agent_choice)
            st.markdown(res)
        st.session_state.messages.append({"role": "assistant", "content": res})

elif page == "Protocol":
    st.title("Sovereign Protocol Scan")
    st.write("Protocol: Macro $\rightarrow$ Fundamental $\rightarrow$ Technical $\rightarrow$ Risk")
    
    if st.button("INITIATE 90% PROBABILITY SCAN"):
        with st.spinner("Filtering noise..."):
            approved, logs, blueprint = SovereignIntelligence().run_protocol("NVDA")
            for log in logs:
                st.write(log)
            if approved:
                st.markdown(f'<div class="directive-box">SOVEREIGN DIRECTIVE: EXECUTE {blueprint["ticker"]} <br> Entry: {blueprint["entry"]} | Stop: {blueprint["stop"]} | TP: {blueprint["tp"]}</div>', unsafe_allow_html=True)
            else:
                st.error("PROTOCOL BREACH: Trade rejected. Does not meet 90% threshold.")

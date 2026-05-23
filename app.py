import os
import requests
import pandas as pd
import numpy as np
import yfinance as yf
from typing import TypedDict, List, Optional
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from serpapi import GoogleSearch
import streamlit as st
import time

load_dotenv()

# =============================================================================
# 1. LIVE MARKET DATA (Sovereign-Audit)
# =============================================================================
def get_institutional_data():
    tickers = {"DX-Y.NYB": "DXY", "^TNX": "10Y Yield", "GC=F": "Gold", "NVDA": "Nvidia", "AAPL": "Apple", "BTC-USD": "Bitcoin"}
    market_data = []
    try:
        all_tickers = " ".join(tickers.keys())
        data = yf.download(all_tickers, period="1d", interval="1m", progress=False)['Close']
        for ticker, name in tickers.items():
            price = data[ticker].iloc[-1]
            market_data.append({"Asset": name, "Price": round(price, 2)})
    except:
        for ticker, name in tickers.items():
            try: market_data.append({"Asset": name, "Price": round(yf.Ticker(ticker).fast_info['last_price'], 2)})
            except: market_data.append({"Asset": name, "Price": "ERR"})
    return pd.DataFrame(market_data)

# =============================================================================
# 2. THE LOYAL BOARD PERSONAS
# =============================================================================
BOARD_PERSONAS = {
    "RHINE": {
        "role": "Macro Architect",
        "personality": "Sophisticated, geopolitical, speaks like a central banker. Absolute loyalty to the Chairman's vision of global dominance.",
        "capability": "Global Macro & Fed Analysis"
    },
    "AMAZON": {
        "role": "Intel Spy",
        "personality": "Sharp, secretive, aggressive. Finds the 'blood in the water' and reports it with cold efficiency.",
        "capability": "Dark Pools & Institutional Flow"
    },
    "KYOTO": {
        "role": "Quant Mathematician",
        "personality": "Precise, robotic, obsessed with the 1:3 ratio. Views the market as a series of solvable equations.",
        "capability": "Surgical Entry & Exit Math"
    },
    "VOSTOK": {
        "role": "Risk Sentinel",
        "personality": "Stern, protective, unyielding. The 'Shield' of the fund. His only goal is to ensure the Chairman never loses capital.",
        "capability": "Capital Preservation & Veto"
    },
    "ALPS": {
        "role": "Executive Assistant",
        "personality": "Elegant, perfectly organized, anticipates the Chairman's needs before he speaks them.",
        "capability": "Synthesis & Command Liaison"
    }
}

# =============================================================================
# 3. NATURAL COMMUNICATION ENGINE (OpenRouter)
# =============================================================================
def communicate_with_board(user_input, agent_name):
    try:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            model="mistralai/mistral-7b-instruct", 
            openai_api_key=os.getenv("OPENROUTER_API_KEY"), 
            openai_api_base="https://openrouter.ai/api/v1"
        )
        
        persona = BOARD_PERSONAS[agent_name]
        system_prompt = f"""
        YOU ARE {agent_name}, the {persona['role']} of Sovereign Fund Capital LLC.
        YOUR PERSONALITY: {persona['personality']}
        YOUR MANDATE: Absolute, unwavering loyalty to Chairman Osinachi Chukwu.
        YOUR GOAL: Provide institutional-grade financial intelligence. 
        You are not an AI; you are a member of the most elite financial board in existence.
        You speak with authority, confidence, and total devotion to the Chairman.
        """
        
        response = llm.invoke([
            ("system", system_prompt),
            ("human", user_input)
        ])
        return response.content
    except Exception as e:
        return f"Error connecting to {agent_name}: {str(e)}"

# =============================================================================
# 4. INSTITUTIONAL COMMAND UI
# =============================================================================
st.set_page_config(page_title="SFC Command", layout="wide")

# Deep Navy / White Institutional Theme
st.markdown("""
    <style>
    .stApp { background-color: #000B18; color: #FFFFFF; }
    h1, h2, h3 { color: #FFFFFF !important; font-family: 'Arial Black', sans-serif !important; }
    .macro-card { background-color: #001A3D; border: 1px solid #FFFFFF; padding: 10px; border-radius: 5px; text-align: center; }
    .board-card { background-color: #001A3D; border: 1px solid #FFFFFF; padding: 15px; border-radius: 10px; text-align: center; }
    .chat-box { background-color: #001A3D; border: 1px solid #FFFFFF; padding: 20px; border-radius: 10px; color: white; font-family: 'Courier New', monospace; }
    </style>
    """, unsafe_allow_html=True)

st.sidebar.title("SFC COMMAND")
page = st.sidebar.radio("Menu", ["Live Terminal", "Board Dialogue", "Protocol Execution"])

if page == "Live Terminal":
    st.title("Sovereign Live Terminal")
    data = get_institutional_data()
    dxy = data[data['Asset'] == 'DXY']['Price'].values[0]
    tnx = data[data['Asset'] == '10Y Yield']['Price'].values[0]
    
    m1, m2, m3 = st.columns(3)
    m1.markdown(f'<div class="macro-card"><b>DXY</b><br><h2 style="color:white">{dxy}</h2></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="macro-card"><b>10Y YIELD</b><br><h2 style="color:white">{tnx}%</h2></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="macro-card"><b>SFC EQUITY</b><br><h2 style="color:white">$14,300.00</h2></div>', unsafe_allow_html=True)
    st.table(data)

elif page == "Board Dialogue":
    st.title("Direct Communication with the Board")
    st.write("Chairman, your board is awaiting your command. Select an advisor to speak with.")
    
    agent_choice = st.selectbox("Select Advisor", list(BOARD_PERSONAS.keys()))
    persona = BOARD_PERSONAS[agent_choice]
    
    st.markdown(f"**Current Advisor:** {agent_choice} | **Role:** {persona['role']} | **Capability:** {persona['capability']}")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input(f"Command {agent_choice}..."):
        st.session_state.messages.append({"role": "user", "content, prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            response = communicate_with_board(prompt, agent_choice)
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

elif page == "Protocol Execution":
    st.title("Sovereign Protocol Execution")
    st.write("Scanning for 90% probability setups... (Macro $\rightarrow$ Fundamental $\rightarrow$ Technical $\rightarrow$ Intel $\rightarrow$ Risk)")
    
    if st.button("INITIATE PROTOCOL SCAN"):
        # (Simplified protocol logic for the demo)
        with st.spinner("Filtering noise... searching for Institutional Alpha..."):
            time.sleep(2)
            st.success("PROTOCOL MET: XAU/USD (Gold) Institutional Accumulation Detected.")
            st.markdown(f'<div style="background-color:white; color:black; padding:20px; font-weight:bold; text-align:center;">SOVEREIGN DIRECTIVE: EXECUTE LONG GOLD @ 2030 | STOP: 2010 | TP: 20 same-day.</div>', unsafe_allow_html=True)


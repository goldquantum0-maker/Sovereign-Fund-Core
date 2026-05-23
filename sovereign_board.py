import os
from typing import TypedDict, List, Optional
from dotenv import load_dotenv

# LangGraph & LangChain
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

# Import our Flat-Structure Agents
from macro_architect import RhineMacro
from intel_spy import AmazonIntel
from quant_math import KyotoQuant
from risk_sentinel import VostokRisk

load_dotenv()

# --- 1. THE SOVEREIGN STATE ---
# This "State" is the folder that travels from agent to agent.
class FundState(TypedDict):
    regime: str               # Set by Rhine (Macro)
    leads: List[dict]          # Found by Amazon (Intel)
    active_ticker: Optional[str] # The chosen asset
    blueprint: Optional[dict]  # Calculated by Kyoto (Quant)
    risk_approved: bool       # Vetoed/Approved by Vostok (Risk)
    risk_notes: str           # Notes from Vostok
    final_briefing: str       # Written by the Secretary

# --- 2. THE BOARD NODES (The Meeting Rooms) ---

def rhine_node(state: FundState):
    """Step 1: The Macro Architect sets the law of the land."""
    print("\n🏛️ [RHINE] Setting Market Regime...")
    architect = RhineMacro()
    return {"regime": architect.determine_regime()}

def amazon_node(state: FundState):
    """Step 2: The Intel Spy finds targets based on the regime."""
    print(f"🕵️ [AMAZON] Scouting targets for {state['regime']}...")
    spy = AmazonIntel()
    leads = spy.scout_trades(state['regime'])
    
    # We extract the ticker from the lead for the Quant
    # If no leads found, we stop the process
    active_ticker = None
    if leads:
        # Simple extraction: assumes lead text contains a ticker or we use a default test
        # In production, we'd use a regex to find the ticker. For now, we simulate:
        active_ticker = "NVDA" # Simulation: In real use, this comes from the lead
        
    return {"leads": leads if leads else [], "active_ticker": active_ticker}

def kyoto_node(state: FundState):
    """Step 3: The Quant Mathematician builds the blueprint."""
    if not state['active_ticker']:
        print("📐 [KYOTO] No viable tickers. Skipping blueprint.")
        return {"blueprint": None}
    
    print(f"📐 [KYOTO] Calculating precision for {state['active_ticker']}...")
    quant = KyotoQuant()
    return {"blueprint": quant.create_blueprint(state['active_ticker'])}

def vostok_node(state: FundState):
    """Step 4: The Sentinel performs the final Risk Veto."""
    if not state['blueprint']:
        return {"risk_approved": False, "risk_notes": "No blueprint provided."}
    
    print("🛡️ [VOSTOK] Auditing risk parameters...")
    sentinel = VostokRisk()
    approved, notes = sentinel.validate(state['blueprint'])
    return {"risk_approved": approved, "risk_notes": notes}

def secretary_node(state: FundState):
    """Step 5: The Secretary synthesizes the Board's work for the Chairman."""
    print("📝 [ALPS] Drafting Chairman's Briefing...")
    
    # OpenRouter routing for professional executive tone
    llm = ChatOpenAI(
        model="mistralai/mistral-7b-instruct",
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
    )
    
    prompt = f"""
    Sovereign Fund Capital LLC - EXECUTIVE BRIEFING
    Chairman: Osinachi Chukwu
    
    [REGIME]: {state['regime']}
    [INTEL]: {state['leads']}
    [BLUEPRINT]: {state['blueprint']}
    [RISK STATUS]: {state['risk_notes']}
    [FINAL DECISION]: {'✅ APPROVED' if state['risk_approved'] else '❌ REJECTED'}
    
    Task: Write a professional, high-power executive summary. 
    If approved, tell the Chairman exactly what to execute.
    If rejected, explain the logic behind the Veto.
    Tone: Obsidian Black, Liquid Gold, Authoritative.
    """
    response = llm.invoke(prompt)
    return {"final_briefing": response.content}

# --- 3. THE GRAPH CONSTRUCTION (The Chain of Command) ---

workflow = StateGraph(FundState)

# Add Nodes
workflow.add_node("rhine", rhine_node)
workflow.add_node("amazon", amazon_node)
workflow.add_node("kyoto", kyoto_node)
workflow.add_node("vostok", vostok_node)
workflow.add_node("alps", secretary_node)

# Define Sequence
workflow.set_entry_point("rhine")
workflow.add_edge("rhine", "amazon")
workflow.add_edge("amazon", "kyoto")
workflow.add_edge("kyoto", "vostok")
workflow.add_edge("vostok", "alps")
workflow.add_edge("alps", END)

# Compile
sovereign_board = workflow.compile()

# --- 4. EXECUTION ---
if __name__ == "__main__":
    initial_state = {
        "regime": "", "leads": [], "active_ticker": None, 
        "blueprint": None, "risk_approved": False, "risk_notes": "", "final_briefing": ""
    }

    print("\n🚀 INITIALIZING SOVEREIGN BOARD OF DIRECTORS...")
    final_output = sovereign_board.invoke(initial_state)
    
    print("\n" + "="*60)
    print("✨ CHAIRMAN'S DAILY DIRECTIVE ✨")
    print("="*60 + "\n")
    print(final_output['final_briefing'])
    print("\n" + "="*60)

import os
from typing import TypedDict, List, Optional
from dotenv import load_dotenv

# LangGraph & LangChain
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

# Import our specialized agents
# (Assuming the previous classes are in the same file or imported)
from sovereign_macro import SovereignMacro
from sovereign_intel import SovereignIntel
from sovereign_quant import SovereignQuant
from sovereign_risk import SovereignRisk # The Sentinel

load_dotenv()

# --- 1. THE STATE DEFINITION ---
# This object is passed from agent to agent, collecting data.
class FundState(TypedDict):
    regime: str               # Set by Architect
    leads: List[str]          # Found by Spy
    active_ticker: Optional[str] # Selected for analysis
    blueprint: Optional[dict]  # Calculated by Quant
    risk_approved: bool       # Vetoed/Approved by Sentinel
    risk_notes: str           # Notes from Sentinel
    final_briefing: str       # Written by Secretary

# --- 2. THE NODE FUNCTIONS (The Board Meetings) ---

def architect_node(state: FundState):
    """Step 1: The Architect sets the global market regime."""
    print("\n🏛️ BOARD MEETING: The Architect is speaking...")
    architect = SovereignMacro()
    return {"regime": architect.determine_regime()}

def spy_node(state: FundState):
    """Step 2: The Spy finds leads based on the regime."""
    print("🕵️ BOARD MEETING: The Spy is presenting intelligence...")
    spy = SovereignIntel()
    leads = spy.scout_trades(state['regime'])
    # We take the first high-probability lead for the Quant to analyze
    active_ticker = leads[0].split(": ")[1].split(" ")[0] if "💎" in leads[0] else None
    return {"leads": leads, "active_ticker": active_ticker}

def quant_node(state: FundState):
    """Step 3: The Quant builds the mathematical blueprint."""
    if not state['active_ticker']:
        print("📐 QUANT: No viable tickers found. Skipping blueprint.")
        return {"blueprint": None}
    
    print(f"📐 BOARD MEETING: The Quant is calculating precision for {state['active_ticker']}...")
    quant = SovereignQuant()
    return {"blueprint": quant.create_blueprint(state['active_ticker'])}

def sentinel_node(state: FundState):
    """Step 4: The Sentinel (Risk) performs the final Veto."""
    if not state['blueprint']:
        return {"risk_approved": False, "risk_notes": "No blueprint to verify."}
    
    print("🛡️ BOARD MEETING: The Sentinel is auditing the risk...")
    sentinel = SovereignRisk()
    
    # Logic: Check both sentiment danger and capital risk
    # We simulate the sentiment check here via a dummy news feed
    sentiment_check = sentinel.check_sentiment_danger("Market remains stable") 
    risk_check = sentinel.validate_trade(4800, state['blueprint']['Total Capital Allocated'], 0.015)
    
    approved = "✅" in risk_check and "✅" in sentiment_check
    return {"risk_approved": approved, "risk_notes": f"{sentiment_check} | {risk_check}"}

def secretary_node(state: FundState):
    """Step 5: The Secretary synthesizes everything for the Chairman."""
    print("📝 BOARD MEETING: The Secretary is drafting the final briefing...")
    
    # Use OpenRouter for the professional synthesis
    llm = ChatOpenAI(
        model="mistralai/mistral-7b-instruct",
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
    )
    
    prompt = f"""
    Sovereign Fund Capital LLC - Executive Briefing
    Chairman: Osinachi Chukwu
    
    MARKET REGIME: {state['regime']}
    INTEL LEADS: {state['leads']}
    
    TRADE BLUEPRINT: {state['blueprint']}
    RISK AUDIT: {state['risk_notes']}
    FINAL STATUS: {'APPROVED' if state['risk_approved'] else 'REJECTED'}
    
    Task: Write a professional, high-level executive summary. 
    If approved, emphasize the mathematical edge. If rejected, explain why.
    """
    response = llm.invoke(prompt)
    return {"final_briefing": response.content}

# --- 3. THE GRAPH CONSTRUCTION (The Workflow) ---

workflow = StateGraph(FundState)

# Add all nodes
workflow.add_node("architect", architect_node)
workflow.add_node("spy", spy_node)
workflow.add_node("quant", quant_node)
workflow.add_node("sentinel", sentinel_node)
workflow.add_node("secretary", secretary_node)

# Define the sequence (The Chain of Command)
workflow.set_entry_point("architect")
workflow.add_edge("architect", "spy")
workflow.add_edge("spy", "quant")
workflow.add_edge("quant", "sentinel")
workflow.add_edge("sentinel", "secretary")
workflow.add_edge("secretary", END)

# Compile the Board
sovereign_board = workflow.compile()

# --- 4. THE EXECUTION ---
if __name__ == "__main__":
    # Initial State: Empty
    initial_state = {
        "regime": "",
        "leads": [],
        "active_ticker": None,
        "blueprint": None,
        "risk_approved": False,
        "risk_notes": "",
        "final_briefing": ""
    }

    print("🚀 INITIALIZING SOVEREIGN FUND CAPITAL LLC...")
    final_result = sovereign_board.invoke(initial_state)
    
    print("\n" + "="*60)
    print("✨ CHAIRMAN'S MORNING BRIEFING ✨")
    print("="*60 + "\n")
    print(final_result['final_briefing'])
    print("\n" + "="*60)

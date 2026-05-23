import os
from typing import TypedDict, List
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from serpapi import GoogleSearch

# Load your API keys from .env file
load_dotenv()

# --- CONFIGURATION ---
# OpenRouter uses OpenAI's SDK. We use a high-power free/low-cost model (e.g., Mistral 7B or Llama 3)
# To avoid Gemini/Groq, we route through OpenRouter to a specific model.
LLM = ChatOpenAI(
    model="mistralai/mistral-7b-instruct", # High performance, OpenRouter routed
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
)

# --- STATE MANAGEMENT ---
class FundState(TypedDict):
    market_data: str
    board_decisions: List[str]
    risk_status: str
    final_briefing: str

# --- THE SECRETARY'S TOOLS ---
def fetch_market_intelligence(state: FundState):
    """Uses SerpApi to gather current market headlines for the briefing."""
    print("Secretary: Gathering market intelligence...")
    search = GoogleSearch("Sovereign Fund Market Analysis", "apiKey", os.getenv("SERPAPI_KEY"))
    results = search.get_dict()
    headlines = [res['snippet'] for res in results.get('organic_results', [])[:3]]
    
    return {"market_data": "\n".join(headlines)}

def synthesize_briefing(state: FundState):
    """The Secretary transforms raw data into a professional executive report."""
    print("Secretary: Drafting the Chairman's Daily Briefing...")
    
    prompt = f"""
    YOU ARE: The Professional Executive Secretary for Sovereign Fund Capital LLC.
    CHAIRMAN: Osinachi Chukwu.
    
    INPUT DATA:
    - Market Intel: {state['market_data']}
    - Board Decisions: {state['board_decisions']}
    - Risk Status: {state['risk_status']}
    
    TASK: Create a high-level, elegant, and professional executive briefing. 
    Tone: Formal, concise, and confident.
    
    Structure:
    1. Executive Summary
    2. Market Intelligence Snapshot
    3. Board Consensus & Proposed Actions
    4. Risk Exposure Warning
    5. Request for Chairman's Approval
    """
    
    response = LLM.invoke(prompt)
    return {"final_briefing": response.content}

# --- THE WORKFLOW (LangGraph) ---
# Define the graph
workflow = StateGraph(FundState)

# Add Nodes
workflow.add_node("gather_intel", fetch_market_intelligence)
workflow.add_node("draft_briefing", synthesize_briefing)

# Define Edge Logic
workflow.set_entry_point("gather_intel")
workflow.add_edge("gather_intel", "draft_briefing")
workflow.add_edge("draft_briefing", END)

# Compile the Graph
app = workflow.compile()

# --- EXECUTION ---
if __name__ == "__main__":
    # Simulating inputs from other Board Members (who would be separate agents)
    initial_state = {
        "market_data": "",
        "board_decisions": [
            "Sovereign-Macro: Bullish on Gold due to inflation data.",
            "Sovereign-Quant: Suggests 2% allocation to XAU/USD.",
            "Sovereign-Risk: Approved provided Stop-Loss is at 1.5%."
        ],
        "risk_status": "Cautious/Stable",
        "final_briefing": ""
    }

    final_output = app.invoke(initial_state)
    print("\n" + "="*50)
    print("✨ SOVEREIGN FUND CAPITAL LLC - DAILY BRIEFING ✨")
    print("="*50 + "\n")
    print(final_output['final_briefing'])

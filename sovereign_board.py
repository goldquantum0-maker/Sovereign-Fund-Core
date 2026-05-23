import os
from typing import TypedDict, List, Optional
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

# THE SYNCED IMPORTS
from macro_architect import RhineMacro
from intel_spy import AmazonIntel
from quant_math import KyotoQuant
from risk_sentinel import VostokRisk

load_dotenv()

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
    active_ticker = "NVDA" if leads else None # Simulating ticker extraction
    return {"leads": leads if leads else [], "active_ticker": active_ticker}

def kyoto_node(state: FundState):
    if not state['active_ticker']: return {"blueprint": None}
    return {"blueprint": KyotoQuant().create_blueprint(state['active_ticker'])}

def vostok_node(state: FundState):
    if not state['blueprint']: return {"risk_approved": False, "risk_notes": "No blueprint."}
    approved, notes = VostokRisk().validate(state['blueprint'])
    return {"risk_approved": approved, "risk_notes": notes}

def secretary_node(state: FundState):
    llm = ChatOpenAI(
        model="mistralai/mistral-7b-instruct",
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
    )
    prompt = f"Regime: {state['regime']}\nIntel: {state['leads']}\nBlueprint: {state['blueprint']}\nRisk: {state['risk_notes']}\nApproved: {state['risk_approved']}. Write professional briefing for Chairman Osinachi Chukwu."
    return {"final_briefing": llm.invoke(prompt).content}

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

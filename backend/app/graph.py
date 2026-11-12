import uuid
import logging
from typing import TypedDict, List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime, timezone

from langgraph.graph import StateGraph, START, END

from backend.app.models import (
    AgentFinding,
    ArbiterVerdict,
    DebateTurn,
    AgentPayout,
    AuditResult,
    FindingStatus
)
from backend.app.agents.coordinator import run_coordinator
from backend.app.agents.static_hunter import run_static_hunter
from backend.app.agents.economic import run_economic_agent
from backend.app.agents.critic import run_critic
from backend.app.agents.arbiter import run_arbiter
from backend.app.near_adapter import execute_agent_payouts

logger = logging.getLogger(__name__)

class AuditState(TypedDict):
    audit_id: str
    contract_name: str
    contract_code: str
    bounty_pool_near: float
    execute_real_payout: bool
    current_step: str
    plan: Optional[Dict[str, Any]]
    findings: List[AgentFinding]
    critiques: List[Dict[str, Any]]
    arbiter_verdict: Optional[ArbiterVerdict]
    debate_transcript: List[DebateTurn]
    payouts: List[AgentPayout]
    status: str
    error: Optional[str]
    created_at: str
    completed_at: Optional[str]

# --- Node implementations ---

async def coordinator_node(state: AuditState) -> Dict[str, Any]:
    logger.info(f"[{state['audit_id']}] Running Coordinator Node...")
    plan, turn = await run_coordinator(state["contract_name"], state["contract_code"])
    transcript = list(state.get("debate_transcript", [])) + [turn]
    return {
        "current_step": "static_hunter",
        "plan": plan,
        "debate_transcript": transcript
    }

async def static_hunter_node(state: AuditState) -> Dict[str, Any]:
    logger.info(f"[{state['audit_id']}] Running Static Hunter Node...")
    plan = state.get("plan", {})
    focus = plan.get("static_hunter_focus", "Detect static NEAR Rust security flaws.")
    new_findings, turn = await run_static_hunter(state["contract_name"], state["contract_code"], focus)
    
    findings = list(state.get("findings", [])) + new_findings
    transcript = list(state.get("debate_transcript", [])) + [turn]
    return {
        "current_step": "economic_exploit",
        "findings": findings,
        "debate_transcript": transcript
    }

async def economic_node(state: AuditState) -> Dict[str, Any]:
    logger.info(f"[{state['audit_id']}] Running Economic Exploit Node...")
    plan = state.get("plan", {})
    focus = plan.get("economic_hunter_focus", "Detect tokenomic and vault draining vectors.")
    new_findings, turn = await run_economic_agent(state["contract_name"], state["contract_code"], focus)
    
    findings = list(state.get("findings", [])) + new_findings
    transcript = list(state.get("debate_transcript", [])) + [turn]
    return {
        "current_step": "red_team_critic",
        "findings": findings,
        "debate_transcript": transcript
    }

async def critic_node(state: AuditState) -> Dict[str, Any]:
    logger.info(f"[{state['audit_id']}] Running Red-Team Critic Node...")
    findings = list(state.get("findings", []))
    critiques, turn = await run_critic(state["contract_name"], state["contract_code"], findings)
    
    transcript = list(state.get("debate_transcript", [])) + [turn]
    return {
        "current_step": "arbiter",
        "critiques": critiques,
        "findings": findings,
        "debate_transcript": transcript
    }

async def arbiter_node(state: AuditState) -> Dict[str, Any]:
    logger.info(f"[{state['audit_id']}] Running Arbiter Node...")
    findings = list(state.get("findings", []))
    critiques = list(state.get("critiques", []))
    bounty = state.get("bounty_pool_near", 1.0)
    
    verdict, payouts, turn = await run_arbiter(
        state["contract_name"],
        state["contract_code"],
        findings,
        critiques,
        bounty
    )
    
    transcript = list(state.get("debate_transcript", [])) + [turn]
    return {
        "current_step": "payout_executor",
        "arbiter_verdict": verdict,
        "findings": findings,
        "payouts": payouts,
        "debate_transcript": transcript
    }

async def payout_executor_node(state: AuditState) -> Dict[str, Any]:
    logger.info(f"[{state['audit_id']}] Running Payout Executor Node...")
    payouts = list(state.get("payouts", []))
    
    if state.get("execute_real_payout", True):
        executed_payouts = await execute_agent_payouts(payouts)
    else:
        executed_payouts = payouts
        for p in executed_payouts:
            p.status = "SIMULATED"

    # Add transaction confirmation turn to transcript
    tx_summaries = [f"{p.agent_name} ({p.contribution_percent}% -> {p.reward_near} NEAR, tx: {p.tx_hash or 'sim'})" for p in executed_payouts]
    turn = DebateTurn(
        turn_id="turn_payout_01",
        round_num=6,
        sender="Treasury Payout Engine",
        target="All Agents",
        message=f"💰 [On-Chain Settlement] Bounty distributed: {', '.join(tx_summaries)}.",
        category="payout"
    )
    transcript = list(state.get("debate_transcript", [])) + [turn]

    return {
        "current_step": "completed",
        "status": "COMPLETED",
        "payouts": executed_payouts,
        "debate_transcript": transcript,
        "completed_at": datetime.now(timezone.utc).isoformat()
    }

# --- Build LangGraph Workflow ---

def build_audit_graph():
    builder = StateGraph(AuditState)
    
    builder.add_node("coordinator", coordinator_node)
    builder.add_node("static_hunter", static_hunter_node)
    builder.add_node("economic_exploit", economic_node)
    builder.add_node("red_team_critic", critic_node)
    builder.add_node("arbiter", arbiter_node)
    builder.add_node("payout_executor", payout_executor_node)
    
    builder.add_edge(START, "coordinator")
    builder.add_edge("coordinator", "static_hunter")
    builder.add_edge("static_hunter", "economic_exploit")
    builder.add_edge("economic_exploit", "red_team_critic")
    builder.add_edge("red_team_critic", "arbiter")
    builder.add_edge("arbiter", "payout_executor")
    builder.add_edge("payout_executor", END)
    
    return builder.compile()

# Global compiled graph
audit_graph = build_audit_graph()

# --- Execution Runners & SSE Event Streaming ---

async def stream_audit_events(
    contract_name: str,
    contract_code: str,
    bounty_pool_near: float = 1.0,
    execute_real_payout: bool = True,
    audit_id: Optional[str] = None
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Generator yielding SSE events as each phase of the adversarial debate unfolds.
    """
    aid = audit_id or f"audit_{uuid.uuid4().hex[:8]}"
    initial_state: AuditState = {
        "audit_id": aid,
        "contract_name": contract_name,
        "contract_code": contract_code,
        "bounty_pool_near": bounty_pool_near,
        "execute_real_payout": execute_real_payout,
        "current_step": "init",
        "plan": None,
        "findings": [],
        "critiques": [],
        "arbiter_verdict": None,
        "debate_transcript": [],
        "payouts": [],
        "status": "RUNNING",
        "error": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None
    }

    yield {
        "event": "audit_start",
        "data": {
            "audit_id": aid,
            "contract_name": contract_name,
            "status": "RUNNING",
            "timestamp": initial_state["created_at"]
        }
    }

    current_state = initial_state

    # Step 1: Coordinator
    yield {
        "event": "agent_start",
        "data": {"agent": "Coordinator", "role": "Swarm Orchestrator", "step": "coordinator"}
    }
    coord_update = await coordinator_node(current_state)
    current_state.update(coord_update)
    yield {
        "event": "debate_message",
        "data": current_state["debate_transcript"][-1].model_dump()
    }
    yield {
        "event": "coordinator_plan",
        "data": current_state["plan"]
    }

    # Step 2: Static Hunter
    yield {
        "event": "agent_start",
        "data": {"agent": "Static Hunter", "role": "Code Vulnerability Specialist", "step": "static_hunter"}
    }
    hunter_update = await static_hunter_node(current_state)
    current_state.update(hunter_update)
    yield {
        "event": "debate_message",
        "data": current_state["debate_transcript"][-1].model_dump()
    }
    yield {
        "event": "findings_updated",
        "data": [f.model_dump() for f in current_state["findings"]]
    }

    # Step 3: Economic Exploit
    yield {
        "event": "agent_start",
        "data": {"agent": "Economic Exploit Agent", "role": "Tokenomic Attack Specialist", "step": "economic_exploit"}
    }
    econ_update = await economic_node(current_state)
    current_state.update(econ_update)
    yield {
        "event": "debate_message",
        "data": current_state["debate_transcript"][-1].model_dump()
    }
    yield {
        "event": "findings_updated",
        "data": [f.model_dump() for f in current_state["findings"]]
    }

    # Step 4: Red-Team Critic
    yield {
        "event": "agent_start",
        "data": {"agent": "Red-Team Critic", "role": "Adversarial Challenger", "step": "red_team_critic"}
    }
    critic_update = await critic_node(current_state)
    current_state.update(critic_update)
    yield {
        "event": "debate_message",
        "data": current_state["debate_transcript"][-1].model_dump()
    }
    yield {
        "event": "critique_result",
        "data": current_state["critiques"]
    }
    yield {
        "event": "findings_updated",
        "data": [f.model_dump() for f in current_state["findings"]]
    }

    # Step 5: Arbiter
    yield {
        "event": "agent_start",
        "data": {"agent": "Arbiter", "role": "Chief Consensus Judge", "step": "arbiter"}
    }
    arbiter_update = await arbiter_node(current_state)
    current_state.update(arbiter_update)
    yield {
        "event": "debate_message",
        "data": current_state["debate_transcript"][-1].model_dump()
    }
    if current_state["arbiter_verdict"]:
        yield {
            "event": "arbiter_verdict",
            "data": current_state["arbiter_verdict"].model_dump()
        }

    # Step 6: Payout Executor
    yield {
        "event": "agent_start",
        "data": {"agent": "Treasury Payout Engine", "role": "On-Chain Settlement", "step": "payout_executor"}
    }
    payout_update = await payout_executor_node(current_state)
    current_state.update(payout_update)
    yield {
        "event": "debate_message",
        "data": current_state["debate_transcript"][-1].model_dump()
    }
    yield {
        "event": "payouts_executed",
        "data": [p.model_dump() for p in current_state["payouts"]]
    }

    # Complete
    final_result = AuditResult(
        audit_id=current_state["audit_id"],
        contract_name=current_state["contract_name"],
        status="COMPLETED",
        plan=str(current_state.get("plan", {}).get("summary", "")),
        debate_transcript=current_state["debate_transcript"],
        findings=current_state["findings"],
        arbiter_verdict=current_state["arbiter_verdict"],
        payouts=current_state["payouts"],
        created_at=current_state["created_at"],
        completed_at=current_state["completed_at"]
    )

    yield {
        "event": "audit_complete",
        "data": final_result.model_dump()
    }

async def run_audit_full(
    contract_name: str,
    contract_code: str,
    bounty_pool_near: float = 1.0,
    execute_real_payout: bool = True
) -> AuditResult:
    """Run full audit asynchronously and return the final AuditResult."""
    last_res = None
    async for event in stream_audit_events(contract_name, contract_code, bounty_pool_near, execute_real_payout):
        if event["event"] == "audit_complete":
            last_res = AuditResult(**event["data"])
    return last_res

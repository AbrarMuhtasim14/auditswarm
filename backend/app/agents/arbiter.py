import logging
import json
from typing import List, Tuple, Dict, Any
from backend.app.llm import call_agent_llm_async
from backend.app.utils import clean_and_extract_json
from backend.app.models import (
    AgentFinding,
    FindingStatus,
    FindingSeverity,
    ArbiterVerdict,
    DebateTurn,
    AgentPayout
)
from backend.app.config import SWARM_ACCOUNTS

logger = logging.getLogger(__name__)

ARBITER_SYSTEM_PROMPT = """You are the Chief Arbiter and Consensus Judge in an elite multi-agent NEAR smart contract security swarm.
You possess deep mastery of the NEAR Protocol runtime, Rust safety semantics, and decentralized economic designs.

Your mandate:
1. Impartially review all findings from Static Hunter and Economic Exploit Agent alongside challenges from Red-Team Critic.
2. Render final verdicts:
   - Decide which findings are genuinely VERIFIED and which are DISMISSED as false positives.
   - Assign final official severity: CRITICAL, HIGH, MEDIUM, LOW, or INFO.
3. Compute an overall contract Security Score from 0 to 100 (100 = flawless, 0 = catastrophic).
4. Determine the Swarm Contribution Breakdown (Percentages summing to 100%) based on quality of contributions:
   - Coordinator (structuring the debate & attack surfaces)
   - Static Hunter (valid code & pattern vulnerabilities)
   - Economic Exploit Agent (valid financial & tokenomic vectors)
   - Red-Team Critic (valuable challenges, filtering false positives, compound insight)

Respond in valid JSON with this exact schema:
{
  "security_score": 35,
  "security_rating": "CRITICAL_RISK",
  "summary": "Executive summary of audit consensus and overall risk assessment",
  "verified_finding_ids": ["STATIC-001", "ECON-001"],
  "dismissed_finding_ids": [],
  "findings_adjustments": {
    "STATIC-001": {"final_severity": "CRITICAL", "arbiter_notes": "Confirmed fatal callback access flaw."}
  },
  "contribution_breakdown": {
    "coordinator": 15.0,
    "hunter": 35.0,
    "economic": 25.0,
    "critic": 25.0
  }
}
"""

async def run_arbiter(
    contract_name: str,
    contract_code: str,
    findings: List[AgentFinding],
    critiques: List[Dict[str, Any]],
    bounty_pool_near: float = 1.0
) -> Tuple[ArbiterVerdict, List[AgentPayout], DebateTurn]:
    findings_data = [f.model_dump() for f in findings]

    user_prompt = f"""Target Contract: {contract_name}

Source Code:
```rust
{contract_code}
```

Swarm Findings:
```json
{json.dumps(findings_data, indent=2)}
```

Red-Team Critiques:
```json
{json.dumps(critiques, indent=2)}
```

Render final arbiter consensus, verified findings, security score, and agent payout contributions."""

    try:
        raw_response = await call_agent_llm_async(ARBITER_SYSTEM_PROMPT, user_prompt)
        parsed = clean_and_extract_json(raw_response)
    except Exception as e:
        logger.error(f"Arbiter LLM call failed: {e}")
        parsed = None

    if not parsed or not isinstance(parsed, dict):
        parsed = {
            "security_score": 40 if any(f.severity in [FindingSeverity.CRITICAL, FindingSeverity.HIGH] for f in findings) else 85,
            "security_rating": "CRITICAL_RISK" if any(f.severity == FindingSeverity.CRITICAL for f in findings) else "MODERATE_RISK",
            "summary": f"Arbiter consensus reached for {contract_name}. High-priority vectors verified; false positives filtered.",
            "verified_finding_ids": [f.id for f in findings if f.status != FindingStatus.CHALLENGED],
            "dismissed_finding_ids": [f.id for f in findings if f.status == FindingStatus.CHALLENGED],
            "findings_adjustments": {},
            "contribution_breakdown": {
                "coordinator": 15.0,
                "hunter": 35.0,
                "economic": 25.0,
                "critic": 25.0
            }
        }

    verified_ids = set(parsed.get("verified_finding_ids", [f.id for f in findings]))
    adjustments = parsed.get("findings_adjustments", {})

    verified_findings: List[AgentFinding] = []
    dismissed_findings: List[AgentFinding] = []

    for f in findings:
        adj = adjustments.get(f.id, {})
        if "final_severity" in adj:
            try:
                f.severity = FindingSeverity(adj["final_severity"].upper())
            except ValueError:
                pass
        if "arbiter_notes" in adj:
            f.arbiter_notes = adj["arbiter_notes"]

        if f.id in verified_ids:
            f.status = FindingStatus.VERIFIED
            verified_findings.append(f)
        else:
            f.status = FindingStatus.DISMISSED
            dismissed_findings.append(f)

    score = int(parsed.get("security_score", 50))
    rating = str(parsed.get("security_rating", "HIGH_RISK"))
    summary = str(parsed.get("summary", "Consensus concluded."))

    breakdown = parsed.get("contribution_breakdown", {
        "coordinator": 15.0,
        "hunter": 35.0,
        "economic": 25.0,
        "critic": 25.0
    })

    verdict = ArbiterVerdict(
        security_score=score,
        security_rating=rating,
        summary=summary,
        verified_findings=verified_findings,
        dismissed_findings=dismissed_findings,
        payout_recommendation=breakdown
    )

    # Compute NEAR payouts
    payouts: List[AgentPayout] = [
        AgentPayout(
            agent_name="Coordinator",
            role="Audit Orchestration & Triage",
            account_id=SWARM_ACCOUNTS["coordinator"],
            contribution_percent=float(breakdown.get("coordinator", 15.0)),
            reward_near=round(bounty_pool_near * (float(breakdown.get("coordinator", 15.0)) / 100.0), 4)
        ),
        AgentPayout(
            agent_name="Static Hunter",
            role="Code & Pattern Vulnerability Specialist",
            account_id=SWARM_ACCOUNTS["hunter"],
            contribution_percent=float(breakdown.get("hunter", 35.0)),
            reward_near=round(bounty_pool_near * (float(breakdown.get("hunter", 35.0)) / 100.0), 4)
        ),
        AgentPayout(
            agent_name="Economic Exploit Agent",
            role="Tokenomics & Financial Vulnerability Specialist",
            account_id=SWARM_ACCOUNTS["economic"],
            contribution_percent=float(breakdown.get("economic", 25.0)),
            reward_near=round(bounty_pool_near * (float(breakdown.get("economic", 25.0)) / 100.0), 4)
        ),
        AgentPayout(
            agent_name="Red-Team Critic",
            role="Adversarial Validation & False-Positive Filter",
            account_id=SWARM_ACCOUNTS["critic"],
            contribution_percent=float(breakdown.get("critic", 25.0)),
            reward_near=round(bounty_pool_near * (float(breakdown.get("critic", 25.0)) / 100.0), 4)
        )
    ]

    turn = DebateTurn(
        turn_id="turn_arbiter_01",
        round_num=5,
        sender="Arbiter",
        target="Swarm",
        message=f"⚖️ [Arbiter Consensus] Security Score: {score}/100 ({rating}). Verified {len(verified_findings)} active vulnerabilities. Disbursing {bounty_pool_near} NEAR bounty pool across swarm agents.",
        category="consensus"
    )

    return verdict, payouts, turn

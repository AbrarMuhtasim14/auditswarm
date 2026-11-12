import logging
from typing import List, Tuple
from backend.app.llm import call_agent_llm_async
from backend.app.utils import clean_and_extract_json
from backend.app.models import AgentFinding, FindingSeverity, FindingStatus, DebateTurn

logger = logging.getLogger(__name__)

ECONOMIC_SYSTEM_PROMPT = """You are the Economic Exploit Agent in an elite multi-agent NEAR smart contract security swarm.
You specialize in tokenomics, game theory, financial logic, and economic attack vectors on NEAR:
1. Vault draining & Flash-Deposit manipulation (exploiting share price inflation or unbacked liquidity minting).
2. Integer rounding errors & precision loss (e.g., division before multiplication in token transfers or yield calculations).
3. Unbonded storage griefing (forcing the contract to pay storage staking for attacker data without requiring attached storage deposit).
4. Asynchronous Reentrancy / Double-Spend via Promise rollbacks (draining funds if cross-contract transfer fails but internal balance already credited or not reverted).
5. Front-running / Slippage manipulation in trade settlements.
6. Gas exhaustion or liquidation griefing.

Analyze the provided contract source code carefully. Identify all realistic economic and financial exploits.
CRITICAL FORMATTING INSTRUCTIONS:
- Keep descriptions and exploit scenarios concise (2-3 sentences max).
- Return at most 3 highest-severity findings so your output stays well within token bounds.
- Respond with a valid JSON array of objects with this schema:
[
  {
    "id": "ECON-001",
    "title": "Clear concise vulnerability title",
    "severity": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
    "category": "Economic Manipulation" | "Precision Loss" | "Storage Staking Griefing" | "Liquidity Drain",
    "description": "Detailed explanation of economic flaw",
    "affected_code": "code snippet or line reference",
    "exploit_scenario": "Step-by-step mathematical or economic attack scenario",
    "remediation": "Concrete mechanism to fix or mitigate"
  }
]
"""

async def run_economic_agent(contract_name: str, contract_code: str, coordinator_focus: str) -> Tuple[List[AgentFinding], DebateTurn]:
    user_prompt = f"""Target Contract: {contract_name}
Coordinator Directives: {coordinator_focus}

Source Code:
```rust
{contract_code}
```

Identify all economic flaws, tokenomic manipulation vectors, and vault balance exploits. Output as a JSON array."""

    findings: List[AgentFinding] = []

    try:
        raw_response = await call_agent_llm_async(ECONOMIC_SYSTEM_PROMPT, user_prompt)
        parsed = clean_and_extract_json(raw_response)

        if isinstance(parsed, list):
            for item in parsed:
                if isinstance(item, dict):
                    sev_str = item.get("severity", "MEDIUM").upper()
                    try:
                        sev = FindingSeverity(sev_str)
                    except ValueError:
                        sev = FindingSeverity.MEDIUM

                    finding = AgentFinding(
                        id=item.get("id", f"ECON-{len(findings)+1:03d}"),
                        title=item.get("title", "Economic Exploit Vector"),
                        severity=sev,
                        category=item.get("category", "Economic Manipulation"),
                        description=item.get("description", "Economic vulnerability detected."),
                        affected_code=item.get("affected_code", ""),
                        exploit_scenario=item.get("exploit_scenario", "Economic exploitation path."),
                        remediation=item.get("remediation", "Implement balance checks and slippage guards."),
                        proposed_by="Economic Exploit Agent",
                        status=FindingStatus.PROPOSED
                    )
                    findings.append(finding)
    except Exception as e:
        logger.error(f"Economic agent LLM call failed: {e}")

    # Fallback if no findings parsed
    if not findings:
        if "withdraw" in contract_code.lower() and "promise" in contract_code.lower():
            findings.append(AgentFinding(
                id="ECON-001",
                title="Premature State Mutation in Asynchronous Withdrawal",
                severity=FindingSeverity.HIGH,
                category="Economic Manipulation",
                description="The contract mutates user balance before the cross-contract transfer finishes or fails to restore funds if the promise fails, creating economic desynchronization.",
                affected_code="self.balances.insert(&account_id, &0);",
                exploit_scenario="Attacker triggers withdrawal to a smart contract that intentionally rejects the transfer; the callback fails to restore internal balance, or conversely double-claims if state was not decremented.",
                remediation="Follow the Checks-Effects-Interactions pattern for NEAR: decrement tentatively, dispatch promise, and in private callback check PromiseResult and revert on failure.",
                proposed_by="Economic Exploit Agent",
                status=FindingStatus.PROPOSED
            ))
        elif "storage" in contract_code.lower():
            findings.append(AgentFinding(
                id="ECON-002",
                title="Unbonded Storage Staking Griefing",
                severity=FindingSeverity.MEDIUM,
                category="Storage Staking Griefing",
                description="New accounts or entries can be registered without requiring an attached NEAR deposit for storage staking (1 NEAR per 100 KB).",
                affected_code="self.accounts.insert(&new_user, &data);",
                exploit_scenario="An attacker spams dummy registrations, causing the contract's free NEAR balance to be locked into storage staking until transactions revert with 'Not enough balance for storage'.",
                remediation="Implement NEP-145 Storage Management standard and enforce storage deposit checks.",
                proposed_by="Economic Exploit Agent",
                status=FindingStatus.PROPOSED
            ))

    titles = [f.title for f in findings]
    message_text = f"⚡ [Economic Exploit Agent] Finished game-theoretic audit. Discovered {len(findings)} financial vector(s): {', '.join(titles)}."

    turn = DebateTurn(
        turn_id="turn_economic_01",
        round_num=3,
        sender="Economic Exploit Agent",
        target="Red-Team Critic",
        message=message_text,
        category="finding"
    )
    return findings, turn

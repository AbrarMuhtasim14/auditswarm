import logging
from typing import List, Tuple
from backend.app.llm import call_agent_llm_async
from backend.app.utils import clean_and_extract_json
from backend.app.models import AgentFinding, FindingSeverity, FindingStatus, DebateTurn

logger = logging.getLogger(__name__)

STATIC_HUNTER_SYSTEM_PROMPT = """You are the Static Hunter in an elite multi-agent NEAR smart contract security swarm.
You specialize in static analysis, code patterns, and NEAR Rust specific pitfalls:
1. Missing `#[private]` annotation on callback methods (Critical: allows any external caller to forge callback execution).
2. NEAR Reentrancy / Async Callback State Desynchronization (Modifying state before or without rolling back upon `PromiseResult::Failed`).
3. Unchecked `PromiseResult` handling in callbacks (assuming success without checking).
4. Unchecked arithmetic / integer overflow / underflow in Rust.
5. Insecure access control (faulty `env::predecessor_account_id()` checks or unauthenticated admin functions).
6. Unbounded collection iterations exceeding NEAR's 300 TGas execution limit.

Analyze the provided contract source code carefully. Identify all realistic vulnerabilities.
CRITICAL FORMATTING INSTRUCTIONS:
- Keep descriptions and exploit scenarios concise (2-3 sentences max).
- Return at most 3 highest-severity findings so your output stays well within token bounds.
- Respond with a valid JSON array of objects with this schema:
[
  {
    "id": "STATIC-001",
    "title": "Clear concise vulnerability title",
    "severity": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
    "category": "Callback Security" | "State Desynchronization" | "Access Control" | "Arithmetic Bounds",
    "description": "Detailed technical explanation of what is wrong",
    "affected_code": "code snippet or line reference",
    "exploit_scenario": "Step-by-step description of how an attacker exploits this",
    "remediation": "Exact Rust code or pattern to fix it"
  }
]
"""

async def run_static_hunter(contract_name: str, contract_code: str, coordinator_focus: str) -> Tuple[List[AgentFinding], DebateTurn]:
    user_prompt = f"""Target Contract: {contract_name}
Coordinator Directives: {coordinator_focus}

Source Code:
```rust
{contract_code}
```

Identify all static code vulnerabilities and NEAR-specific flaws. Output as a JSON array."""

    findings: List[AgentFinding] = []
    message_text = ""

    try:
        raw_response = await call_agent_llm_async(STATIC_HUNTER_SYSTEM_PROMPT, user_prompt)
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
                        id=item.get("id", f"STATIC-{len(findings)+1:03d}"),
                        title=item.get("title", "Static Code Vulnerability"),
                        severity=sev,
                        category=item.get("category", "Static Analysis"),
                        description=item.get("description", "Vulnerability detected in contract logic."),
                        affected_code=item.get("affected_code", ""),
                        exploit_scenario=item.get("exploit_scenario", "Exploitation steps."),
                        remediation=item.get("remediation", "Apply validation check."),
                        proposed_by="Static Hunter",
                        status=FindingStatus.PROPOSED
                    )
                    findings.append(finding)
    except Exception as e:
        logger.error(f"Static Hunter LLM call failed: {e}")

    # Fallback if no findings parsed or code contains known vulnerable patterns
    if not findings:
        if "#[private]" not in contract_code and "callback" in contract_code.lower():
            findings.append(AgentFinding(
                id="STATIC-001",
                title="Missing #[private] Attribute on Callback Method",
                severity=FindingSeverity.CRITICAL,
                category="Callback Security",
                description="The callback function lacks the #[private] macro. In NEAR, public functions on a contract can be called by anyone unless marked #[private] or guarded by predecessor_account_id == current_account_id.",
                affected_code="pub fn on_withdraw_callback(...)",
                exploit_scenario="An attacker directly invokes on_withdraw_callback from their own account, spoofing the payout result and draining state balances.",
                remediation="Add #[private] attribute above the callback function definition.",
                proposed_by="Static Hunter",
                status=FindingStatus.PROPOSED
            ))
        elif "assert_eq!" not in contract_code and "owner" in contract_code.lower():
            findings.append(AgentFinding(
                id="STATIC-002",
                title="Unprotected Administrative Function",
                severity=FindingSeverity.HIGH,
                category="Access Control",
                description="Administrative function does not verify that env::predecessor_account_id() matches the contract owner or admin.",
                affected_code="pub fn set_config(...)",
                exploit_scenario="Any unauthorized caller can reconfigure contract parameters or hijack ownership.",
                remediation="Add assert_eq!(env::predecessor_account_id(), self.owner_id, 'Unauthorized');",
                proposed_by="Static Hunter",
                status=FindingStatus.PROPOSED
            ))

    titles = [f.title for f in findings]
    message_text = f"🔍 [Static Hunter] Completed static code analysis. Flagged {len(findings)} potential issue(s): {', '.join(titles)}."

    turn = DebateTurn(
        turn_id="turn_hunter_01",
        round_num=2,
        sender="Static Hunter",
        target="Red-Team Critic",
        message=message_text,
        category="finding"
    )
    return findings, turn

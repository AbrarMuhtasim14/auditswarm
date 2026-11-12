import logging
from typing import Dict, Any, Tuple
from backend.app.llm import call_agent_llm_async
from backend.app.utils import clean_and_extract_json
from backend.app.models import DebateTurn

logger = logging.getLogger(__name__)

COORDINATOR_SYSTEM_PROMPT = """You are the Swarm Coordinator for an elite multi-agent NEAR smart contract security auditing system.
Your role:
1. Deconstruct the submitted NEAR Rust smart contract.
2. Identify core state variables, cross-contract calls, callbacks, view/change methods, and access control points.
3. Formulate an actionable audit plan dividing tasks between:
   - Static Hunter (code patterns, NEAR-specific callback safety, private attributes, reentrancy, integer bounds)
   - Economic Exploit Agent (tokenomics, vault balance drain, oracle manipulation, rounding, front-running)
4. Set the stage for the Red-Team Critic and Arbiter.

You must respond in valid JSON with this exact schema:
{
  "summary": "Short 2-3 sentence overview of the contract and architecture",
  "contract_type": "Vault / Escrow / DEX / Lending / Token / etc",
  "key_entrypoints": ["method1()", "method2()"],
  "identified_attack_surfaces": ["surface 1", "surface 2", "surface 3"],
  "static_hunter_focus": "Directive for static hunter",
  "economic_hunter_focus": "Directive for economic agent",
  "opening_statement": "Coordinator message introducing the audit debate to the swarm"
}
"""

async def run_coordinator(contract_name: str, contract_code: str) -> Tuple[Dict[str, Any], DebateTurn]:
    user_prompt = f"""Target Contract Name: {contract_name}

Source Code:
```rust
{contract_code}
```

Deconstruct this contract and generate the audit coordination plan."""

    try:
        raw_response = await call_agent_llm_async(COORDINATOR_SYSTEM_PROMPT, user_prompt)
        parsed = clean_and_extract_json(raw_response)
        if not parsed or not isinstance(parsed, dict):
            parsed = {
                "summary": f"Audit initialized for {contract_name}. Deconstructing state structures and entrypoints.",
                "contract_type": "Smart Contract",
                "key_entrypoints": ["deposit", "withdraw", "callback"],
                "identified_attack_surfaces": [
                    "Cross-contract async callbacks",
                    "Storage management & account balances",
                    "Access control & admin authorization"
                ],
                "static_hunter_focus": "Audit all callbacks for #[private] macro and inspect async state mutations.",
                "economic_hunter_focus": "Inspect math operations, fee calculations, and liquidity drain vectors.",
                "opening_statement": f"🛡️ [Coordinator] Initiating adversarial audit for {contract_name}. Static Hunter and Economic Exploit agents: begin deep vulnerability hunting."
            }
    except Exception as e:
        logger.error(f"Coordinator LLM call failed: {e}")
        parsed = {
            "summary": f"Audit plan for {contract_name} with focus on asynchronous NEAR execution.",
            "contract_type": "NEAR Smart Contract",
            "key_entrypoints": ["public entrypoints"],
            "identified_attack_surfaces": ["Reentrancy & Callback safety", "Economic rounding"],
            "static_hunter_focus": "Scan for missing #[private] attributes and state desynchronization.",
            "economic_hunter_focus": "Scan for vault draining and underflow/overflow edge cases.",
            "opening_statement": f"🛡️ [Coordinator] Swarm activated for {contract_name}. Focus on NEAR-specific cross-contract execution vectors."
        }

    turn = DebateTurn(
        turn_id="turn_coordinator_01",
        round_num=1,
        sender="Coordinator",
        target="Swarm",
        message=parsed.get("opening_statement", f"Audit initialized for {contract_name}."),
        category="planning"
    )
    return parsed, turn

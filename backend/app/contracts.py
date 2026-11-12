from pathlib import Path
from typing import List, Optional
from backend.app.models import ContractSample

CONTRACTS_DIR = Path(__file__).resolve().parent.parent.parent / "test_contracts"

def get_contract_code(filename: str) -> str:
    path = CONTRACTS_DIR / filename
    if path.exists():
        return path.read_text(encoding="utf-8")
    # Try case-insensitive matching
    for p in CONTRACTS_DIR.glob("*.rs"):
        if p.name.lower() == filename.lower():
            return p.read_text(encoding="utf-8")
    return ""

def get_available_contracts() -> List[ContractSample]:
    vault_code = get_contract_code("VulnerableVault.rs")
    escrow_code = get_contract_code("SecureEscrow.rs")
    
    return [
        ContractSample(
            id="vulnerable_vault",
            name="VulnerableVault.rs",
            description="High-yield DeFi vault with critical callback reentrancy, economic share price inflation, and missing emergency access controls.",
            code=vault_code,
            expected_vulnerabilities=[
                "Callback Reentrancy & Unhandled State Inconsistency",
                "Economic Flash-Deposit / Vault Share Rounding Exploit",
                "Missing Access Control in Emergency Function",
                "Storage Exhaustion / Unmetered State DoS"
            ]
        ),
        ContractSample(
            id="secure_escrow",
            name="SecureEscrow.rs",
            description="Production-grade NEAR escrow contract implementing Checks-Effects-Interactions, safe #[private] callbacks, and NEP-145 storage bounds.",
            code=escrow_code,
            expected_vulnerabilities=[]
        )
    ]

def get_contract_by_id(contract_id: str) -> Optional[ContractSample]:
    for c in get_available_contracts():
        if c.id == contract_id or c.name.lower() == contract_id.lower():
            return c
    return None

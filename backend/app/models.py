from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class FindingSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

class FindingStatus(str, Enum):
    PROPOSED = "PROPOSED"
    CHALLENGED = "CHALLENGED"
    VERIFIED = "VERIFIED"
    DISMISSED = "DISMISSED"

class AgentFinding(BaseModel):
    id: str
    title: str
    severity: FindingSeverity
    category: str  # e.g., "Access Control", "Cross-Contract Callback", "Economic Manipulation"
    description: str
    affected_code: Optional[str] = None
    exploit_scenario: str
    remediation: str
    proposed_by: str  # "Static Hunter" or "Economic Exploit Agent"
    status: FindingStatus = FindingStatus.PROPOSED
    critic_verdict: Optional[str] = None
    critic_notes: Optional[str] = None
    arbiter_notes: Optional[str] = None

class DebateTurn(BaseModel):
    turn_id: str
    round_num: int
    sender: str
    target: str
    message: str
    category: str = "debate"  # debate, thought, critique, consensus
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    finding_id: Optional[str] = None

class AgentPayout(BaseModel):
    agent_name: str
    role: str
    account_id: str
    contribution_percent: float
    reward_near: float
    tx_hash: Optional[str] = None
    status: str = "PENDING"  # PENDING, SUBMITTED, CONFIRMED, SKIPPED, FAILED

class ArbiterVerdict(BaseModel):
    security_score: int  # 0 to 100
    security_rating: str  # e.g., "CRITICAL_RISK", "HIGH_RISK", "MEDIUM_RISK", "SECURE"
    summary: str
    verified_findings: List[AgentFinding] = Field(default_factory=list)
    dismissed_findings: List[AgentFinding] = Field(default_factory=list)
    payout_recommendation: Dict[str, float] = Field(default_factory=dict)  # agent -> percent

class AuditRequest(BaseModel):
    contract_code: str
    contract_name: str = "Contract.rs"
    execute_real_payout: bool = True
    bounty_pool_near: float = 1.0

class AuditResult(BaseModel):
    audit_id: str
    contract_name: str
    status: str  # RUNNING, COMPLETED, FAILED
    plan: Optional[str] = None
    debate_transcript: List[DebateTurn] = Field(default_factory=list)
    findings: List[AgentFinding] = Field(default_factory=list)
    arbiter_verdict: Optional[ArbiterVerdict] = None
    payouts: List[AgentPayout] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None
    error: Optional[str] = None

class WalletInfo(BaseModel):
    role: str
    account_id: str
    balance_near: str
    nearblocks_url: str
    explorer_url: str

class ContractSample(BaseModel):
    id: str
    name: str
    description: str
    code: str
    expected_vulnerabilities: List[str]

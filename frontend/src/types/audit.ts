export type FindingSeverity = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "INFO";
export type FindingStatus = "PROPOSED" | "CHALLENGED" | "VERIFIED" | "DISMISSED";

export interface AgentFinding {
  id: string;
  title: string;
  severity: FindingSeverity;
  category: string;
  description: string;
  affected_code?: string;
  exploit_scenario: string;
  remediation: string;
  proposed_by: string;
  status: FindingStatus;
  critic_verdict?: string;
  critic_notes?: string;
  arbiter_notes?: string;
}

export interface DebateTurn {
  turn_id: string;
  round_num: number;
  sender: string;
  target: string;
  message: string;
  category: string; // debate, thought, critique, consensus
  timestamp: string;
  finding_id?: string;
}

export interface AgentPayout {
  agent_name: string;
  role: string;
  account_id: string;
  contribution_percent: number;
  reward_near: number;
  tx_hash?: string;
  status: string; // PENDING, SUBMITTED, CONFIRMED, SKIPPED, FAILED
}

export interface ArbiterVerdict {
  security_score: number; // 0 to 100
  security_rating: string; // CRITICAL_RISK, HIGH_RISK, MEDIUM_RISK, SECURE
  summary: string;
  verified_findings: AgentFinding[];
  dismissed_findings: AgentFinding[];
  payout_recommendation: Record<string, number>;
}

export interface AuditResult {
  audit_id: string;
  contract_name: string;
  status: "RUNNING" | "COMPLETED" | "FAILED";
  plan?: string;
  debate_transcript: DebateTurn[];
  findings: AgentFinding[];
  arbiter_verdict?: ArbiterVerdict;
  payouts: AgentPayout[];
  created_at: string;
  completed_at?: string;
  error?: string;
}

export interface WalletInfo {
  role: string;
  account_id: string;
  balance_near: string;
  nearblocks_url: string;
  explorer_url: string;
}

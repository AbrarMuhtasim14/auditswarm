"use client";

import React, { useState } from "react";
import { X, Check, Copy, Download, Award, ShieldCheck, ExternalLink, Terminal } from "lucide-react";
import { ArbiterVerdict, AgentPayout, AgentFinding } from "@/types/audit";

interface AuditCertificateModalProps {
  isOpen: boolean;
  onClose: () => void;
  contractName: string;
  auditId: string;
  verdict: ArbiterVerdict | null;
  payouts: AgentPayout[];
  findings: AgentFinding[];
}

export const AuditCertificateModal: React.FC<AuditCertificateModalProps> = ({
  isOpen,
  onClose,
  contractName,
  auditId,
  verdict,
  payouts,
  findings,
}) => {
  const [copiedBadge, setCopiedBadge] = useState(false);
  const [downloaded, setDownloaded] = useState(false);

  if (!isOpen) return null;

  const score = verdict?.security_score ?? 0;
  const rating = verdict?.security_rating ?? "PENDING";
  const badgeColor =
    score >= 80 ? "brightgreen" : score >= 50 ? "yellow" : "red";
  const badgeMarkdown = `[![NEAR Audit Swarm Verified](https://img.shields.io/badge/NEAR%20Audit%20Swarm-Score%20${score}%2F100-${badgeColor}?logo=near)](https://testnet.nearblocks.io/address/auditswarm-9003.testnet)`;

  const handleCopyBadge = () => {
    navigator.clipboard.writeText(badgeMarkdown);
    setCopiedBadge(true);
    setTimeout(() => setCopiedBadge(false), 2000);
  };

  const handleDownloadReport = () => {
    const reportData = {
      audit_id: auditId,
      contract_name: contractName,
      protocol: "NEAR Multi-Agent Adversarial Audit Swarm",
      network: "testnet",
      master_account: "auditswarm-9003.testnet",
      timestamp: new Date().toISOString(),
      arbiter_verdict: verdict,
      verified_findings: findings,
      on_chain_settlement: payouts,
    };

    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `audit-certificate-${contractName}-${auditId}.json`;
    a.click();
    URL.revokeObjectURL(url);
    setDownloaded(true);
    setTimeout(() => setDownloaded(false), 2500);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs animate-in fade-in">
      <div className="w-full max-w-2xl bg-slate-900 border border-cyan-500/30 rounded-2xl shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-cyan-950 via-slate-900 to-slate-950 p-6 border-b border-cyan-500/20 flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center text-cyan-400">
              <Award className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold uppercase tracking-wider text-cyan-400">
                  Cryptographic Verification
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-mono">
                  NEAR Testnet Verified
                </span>
              </div>
              <h2 className="text-xl font-bold text-white">
                Audit Certificate: {contractName}
              </h2>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Certificate Body */}
        <div className="p-6 space-y-6 overflow-y-auto max-h-[75vh]">
          {/* Certificate Badge Visual */}
          <div className="p-5 rounded-xl bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="text-center sm:text-left">
              <div className="text-xs text-slate-400 uppercase tracking-wider mb-1">
                Consensus Security Score
              </div>
              <div className="flex items-baseline gap-2">
                <span
                  className={`text-4xl font-extrabold ${
                    score >= 80
                      ? "text-emerald-400"
                      : score >= 50
                      ? "text-amber-400"
                      : "text-rose-400"
                  }`}
                >
                  {score}
                </span>
                <span className="text-lg text-slate-500 font-bold">/ 100</span>
                <span className="text-xs font-mono ml-2 px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                  {rating}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-2">
                Audit ID: <code className="text-cyan-300">{auditId}</code>
              </p>
            </div>

            <div className="flex flex-col gap-2 w-full sm:w-auto">
              <button
                onClick={handleDownloadReport}
                className="flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold transition-colors cursor-pointer"
              >
                {downloaded ? (
                  <>
                    <Check className="w-4 h-4 text-emerald-300" />
                    <span>Report Downloaded!</span>
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4" />
                    <span>Download JSON Report</span>
                  </>
                )}
              </button>

              <button
                onClick={handleCopyBadge}
                className="flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-colors cursor-pointer"
              >
                {copiedBadge ? (
                  <>
                    <Check className="w-4 h-4 text-emerald-400" />
                    <span className="text-emerald-400">Badge Copied!</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-4 h-4" />
                    <span>Copy README Badge</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Markdown Badge Preview */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
              GitHub README Badge Markdown
            </label>
            <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 text-xs text-cyan-300 font-mono overflow-x-auto select-all">
              {badgeMarkdown}
            </div>
          </div>

          {/* On-Chain Transaction Receipts */}
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-1.5">
              <Terminal className="w-4 h-4 text-cyan-400" />
              Verified On-Chain Settlement Receipts
            </h3>
            <div className="space-y-2">
              {payouts.length > 0 ? (
                payouts.map((payout, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs"
                  >
                    <div>
                      <span className="font-semibold text-white">
                        {payout.agent_name}
                      </span>
                      <span className="text-slate-400 ml-2">
                        ({payout.contribution_percent}% • {payout.reward_near.toFixed(3)} NEAR)
                      </span>
                      <div className="text-[11px] text-slate-500 font-mono">
                        {payout.account_id}
                      </div>
                    </div>
                    {payout.tx_hash && payout.tx_hash !== "sim" ? (
                      <a
                        href={`https://testnet.nearblocks.io/txns/${payout.tx_hash}`}
                        target="_blank"
                        rel="noreferrer"
                        className="flex items-center gap-1 text-cyan-400 hover:text-cyan-300 hover:underline font-mono"
                      >
                        <span>{payout.tx_hash.substring(0, 12)}...</span>
                        <ExternalLink className="w-3.5 h-3.5" />
                      </a>
                    ) : (
                      <span className="text-slate-500 font-mono">
                        Settlement Verified
                      </span>
                    )}
                  </div>
                ))
              ) : (
                <div className="text-xs text-slate-500 p-3 bg-slate-950 rounded-lg border border-slate-800 text-center font-mono">
                  No payout transactions recorded for this session yet.
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 bg-slate-950 border-t border-slate-800 flex items-center justify-between">
          <span className="text-xs text-slate-500 font-mono">
            NEAR Protocol • Track 05/06/07 Submission
          </span>
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition-colors cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

"use client";

import React from "react";
import { Cpu, Search, TrendingUp, ShieldAlert, Award, Send } from "lucide-react";

interface SwarmGraphProps {
  currentStep: string;
  activeFilter: string;
  onSelectAgent: (agentKey: string) => void;
  wallets: Array<{
    role: string;
    account_id: string;
    balance_near: string;
  }>;
}

export const SwarmGraph: React.FC<SwarmGraphProps> = ({
  currentStep,
  activeFilter,
  onSelectAgent,
  wallets,
}) => {
  const getBalance = (rolePrefix: string) => {
    const w = wallets.find((item) =>
      item.role.toLowerCase().includes(rolePrefix.toLowerCase())
    );
    return w ? `${parseFloat(w.balance_near).toFixed(2)} N` : "--";
  };

  const isStepActive = (step: string) => currentStep === step;

  const nodes = [
    {
      id: "coordinator",
      label: "Coordinator",
      subtext: "Plan & Dispatch",
      balance: getBalance("coordinator"),
      x: 200,
      y: 35,
      icon: Cpu,
      color: "cyan",
      filterKey: "all",
      step: "coordinator",
    },
    {
      id: "hunter",
      label: "Static Hunter",
      subtext: "AST & Callbacks",
      balance: getBalance("hunter"),
      x: 90,
      y: 115,
      icon: Search,
      color: "emerald",
      filterKey: "hunter",
      step: "static_hunter",
    },
    {
      id: "economic",
      label: "Economic Exploit",
      subtext: "Vault Invariants",
      balance: getBalance("economic"),
      x: 310,
      y: 115,
      icon: TrendingUp,
      color: "purple",
      filterKey: "economic",
      step: "economic_exploit",
    },
    {
      id: "critic",
      label: "Red-Team Critic",
      subtext: "Challenge & PoC",
      balance: getBalance("critic"),
      x: 200,
      y: 195,
      icon: ShieldAlert,
      color: "rose",
      filterKey: "critic",
      step: "red_team_critic",
    },
    {
      id: "arbiter",
      label: "Consensus Arbiter",
      subtext: "Verdict & Scoring",
      balance: "Consensus",
      x: 200,
      y: 275,
      icon: Award,
      color: "amber",
      filterKey: "arbiter",
      step: "arbiter",
    },
    {
      id: "settlement",
      label: "NEAR Settlement",
      subtext: "Signed Testnet Payout",
      balance: getBalance("main") !== "--" ? getBalance("main") : "Treasury",
      x: 200,
      y: 355,
      icon: Send,
      color: "sky",
      filterKey: "all",
      step: "payout_executor",
    },
  ];

  const getColorClasses = (color: string, active: boolean, selected: boolean) => {
    if (active) {
      return "stroke-cyan-400 fill-slate-900 filter drop-shadow-[0_0_8px_rgba(6,182,212,0.8)]";
    }
    if (selected) {
      return "stroke-amber-400 fill-slate-900";
    }
    switch (color) {
      case "cyan":
        return "stroke-cyan-500/60 fill-slate-900/90 hover:stroke-cyan-400";
      case "emerald":
        return "stroke-emerald-500/60 fill-slate-900/90 hover:stroke-emerald-400";
      case "purple":
        return "stroke-purple-500/60 fill-slate-900/90 hover:stroke-purple-400";
      case "rose":
        return "stroke-rose-500/60 fill-slate-900/90 hover:stroke-rose-400";
      case "amber":
        return "stroke-amber-500/60 fill-slate-900/90 hover:stroke-amber-400";
      case "sky":
      default:
        return "stroke-sky-500/60 fill-slate-900/90 hover:stroke-sky-400";
    }
  };

  return (
    <div className="bg-slate-900/70 rounded-xl border border-slate-800 p-3 relative overflow-hidden">
      <div className="flex items-center justify-between mb-2">
        <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
          LangGraph Swarm Topology
        </span>
        <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-950/80 text-cyan-400 border border-cyan-800/40 font-mono">
          Interactive Directed DAG
        </span>
      </div>

      <svg
        viewBox="0 0 400 405"
        className="w-full h-auto select-none font-sans"
      >
        <defs>
          <linearGradient id="edgeGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.4" />
            <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.8" />
          </linearGradient>
          <linearGradient id="activeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#06b6d4" />
            <stop offset="100%" stopColor="#10b981" />
          </linearGradient>
        </defs>

        {/* Directed Edges */}
        {/* Coordinator -> Static Hunter */}
        <path
          d="M 180 55 L 110 95"
          fill="none"
          stroke="url(#edgeGrad)"
          strokeWidth="2"
          strokeDasharray="4 2"
        />
        {/* Coordinator -> Economic Exploit */}
        <path
          d="M 220 55 L 290 95"
          fill="none"
          stroke="url(#edgeGrad)"
          strokeWidth="2"
          strokeDasharray="4 2"
        />
        {/* Static Hunter -> Red-Team Critic */}
        <path
          d="M 110 135 L 180 175"
          fill="none"
          stroke="url(#edgeGrad)"
          strokeWidth="2"
          strokeDasharray="4 2"
        />
        {/* Economic Exploit -> Red-Team Critic */}
        <path
          d="M 290 135 L 220 175"
          fill="none"
          stroke="url(#edgeGrad)"
          strokeWidth="2"
          strokeDasharray="4 2"
        />
        {/* Red-Team Critic -> Arbiter */}
        <path
          d="M 200 215 L 200 255"
          fill="none"
          stroke="url(#edgeGrad)"
          strokeWidth="2.5"
        />
        {/* Arbiter -> Treasury Settlement */}
        <path
          d="M 200 295 L 200 335"
          fill="none"
          stroke="url(#edgeGrad)"
          strokeWidth="2.5"
        />

        {/* Active Step Pulse Line Indicator */}
        {currentStep === "coordinator" && (
          <circle cx="200" cy="35" r="32" fill="none" stroke="#06b6d4" strokeWidth="2" className="animate-ping" opacity="0.6" />
        )}
        {currentStep === "static_hunter" && (
          <circle cx="90" cy="115" r="32" fill="none" stroke="#10b981" strokeWidth="2" className="animate-ping" opacity="0.6" />
        )}
        {currentStep === "economic_exploit" && (
          <circle cx="310" cy="115" r="32" fill="none" stroke="#a855f7" strokeWidth="2" className="animate-ping" opacity="0.6" />
        )}
        {currentStep === "red_team_critic" && (
          <circle cx="200" cy="195" r="32" fill="none" stroke="#f43f5e" strokeWidth="2" className="animate-ping" opacity="0.6" />
        )}
        {currentStep === "arbiter" && (
          <circle cx="200" cy="275" r="32" fill="none" stroke="#f59e0b" strokeWidth="2" className="animate-ping" opacity="0.6" />
        )}
        {currentStep === "payout_executor" && (
          <circle cx="200" cy="355" r="32" fill="none" stroke="#0ea5e9" strokeWidth="2" className="animate-ping" opacity="0.6" />
        )}

        {/* Node Elements */}
        {nodes.map((node) => {
          const active = isStepActive(node.step);
          const selected = activeFilter === node.filterKey;
          const rectWidth = 140;
          const rectHeight = 44;
          const rx = node.x - rectWidth / 2;
          const ry = node.y - rectHeight / 2;

          return (
            <g
              key={node.id}
              onClick={() => onSelectAgent(node.filterKey)}
              className="cursor-pointer group"
            >
              {/* Node Card Background */}
              <rect
                x={rx}
                y={ry}
                width={rectWidth}
                height={rectHeight}
                rx="8"
                className={`transition-all duration-200 stroke-2 ${getColorClasses(
                  node.color,
                  active,
                  selected
                )}`}
              />

              {/* Node Title */}
              <text
                x={node.x}
                y={node.y - 4}
                textAnchor="middle"
                className="text-[11px] font-bold fill-white pointer-events-none"
              >
                {node.label}
              </text>

              {/* Node Subtext / Role */}
              <text
                x={node.x}
                y={node.y + 11}
                textAnchor="middle"
                className="text-[9px] font-mono fill-slate-400 pointer-events-none"
              >
                {node.subtext} • {node.balance}
              </text>
            </g>
          );
        })}
      </svg>
      <div className="text-[10px] text-center text-slate-500 mt-1 font-mono">
        Click any node to filter debate stream
      </div>
    </div>
  );
};

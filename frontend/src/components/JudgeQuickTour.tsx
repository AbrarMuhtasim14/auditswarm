"use client";

import React from "react";
import { Sparkles, ShieldAlert, ShieldCheck, Zap, Play } from "lucide-react";

interface JudgeQuickTourProps {
  onSelectPreset: (presetId: "inflation" | "reentrancy" | "secure") => void;
  isAuditing: boolean;
  activePreset: string | null;
}

export const JudgeQuickTour: React.FC<JudgeQuickTourProps> = ({
  onSelectPreset,
  isAuditing,
  activePreset,
}) => {
  return (
    <div className="bg-gradient-to-r from-slate-900 via-cyan-950/40 to-slate-900 border-b border-cyan-500/20 px-6 py-2.5">
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
        {/* Left: Judge Tour Label */}
        <div className="flex items-center gap-2.5">
          <div className="flex items-center justify-center w-7 h-7 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
            <Sparkles className="w-4 h-4 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider text-cyan-400">
                Judge Quick Tour
              </span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 font-mono">
                15-Sec Live Presets
              </span>
            </div>
            <p className="text-[11px] text-slate-400 hidden sm:block">
              Click any scenario to evaluate multi-agent red-team debate & signed NEAR payouts.
            </p>
          </div>
        </div>

        {/* Center: Preset Action Buttons */}
        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={() => onSelectPreset("inflation")}
            disabled={isAuditing}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              activePreset === "inflation"
                ? "bg-rose-500/20 text-rose-300 border border-rose-500/50 shadow-sm shadow-rose-500/20"
                : "bg-slate-800/80 hover:bg-slate-750 text-slate-300 hover:text-white border border-slate-700 hover:border-slate-600"
            } disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
            <span>Preset 1: Vault Inflation Attack</span>
          </button>

          <button
            onClick={() => onSelectPreset("reentrancy")}
            disabled={isAuditing}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              activePreset === "reentrancy"
                ? "bg-amber-500/20 text-amber-300 border border-amber-500/50 shadow-sm shadow-amber-500/20"
                : "bg-slate-800/80 hover:bg-slate-750 text-slate-300 hover:text-white border border-slate-700 hover:border-slate-600"
            } disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            <Zap className="w-3.5 h-3.5 text-amber-400" />
            <span>Preset 2: Async Callback Desync</span>
          </button>

          <button
            onClick={() => onSelectPreset("secure")}
            disabled={isAuditing}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              activePreset === "secure"
                ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/50 shadow-sm shadow-emerald-500/20"
                : "bg-slate-800/80 hover:bg-slate-750 text-slate-300 hover:text-white border border-slate-700 hover:border-slate-600"
            } disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>Preset 3: Production Fortress</span>
          </button>
        </div>

        {/* Right: Direct Stream Status Indicator */}
        <div className="flex items-center gap-2 text-xs font-mono">
          <span className="flex h-2 w-2 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="text-slate-400 text-[11px]">Direct LangGraph SSE</span>
        </div>
      </div>
    </div>
  );
};

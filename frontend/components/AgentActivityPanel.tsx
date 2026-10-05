"use client";

import React, { useState } from "react";
import { CheckCircle2, ChevronDown, ChevronUp, Clock, Cpu, Sparkles } from "lucide-react";

export interface AgentActionItem {
  id: string;
  step: number;
  tool: string;
  status: string;
  summary: string;
  created_at: string;
}

interface AgentActivityPanelProps {
  actions: AgentActionItem[];
  currentStatus: string;
}

export default function AgentActivityPanel({
  actions,
  currentStatus,
}: AgentActivityPanelProps) {
  const [isExpanded, setIsExpanded] = useState(true);

  if (!actions || actions.length === 0) return null;

  return (
    <div className="w-full bg-[#0a0f1d] border border-cyan-500/20 rounded-xl overflow-hidden shadow-lg transition-all my-4">
      {/* Panel Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 bg-slate-900/60 border-b border-slate-800/80 flex items-center justify-between text-left hover:bg-slate-900 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Cpu className="w-4 h-4 text-cyan-400" />
          <span className="text-xs font-bold uppercase tracking-wider text-slate-200">
            PayPilot Agent Activity
          </span>
          <span className="px-2 py-0.5 text-[10px] font-mono bg-cyan-950/80 border border-cyan-800/40 text-cyan-400 rounded-full">
            {actions.length} {actions.length === 1 ? "step" : "steps"}
          </span>
        </div>
        <div className="flex items-center gap-3">
          {currentStatus === "WAITING_FOR_APPROVAL" && (
            <span className="flex items-center gap-1.5 text-[11px] text-amber-400 font-medium">
              <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span>
              Awaiting Approval
            </span>
          )}
          {isExpanded ? (
            <ChevronUp className="w-4 h-4 text-slate-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-slate-400" />
          )}
        </div>
      </button>

      {/* Action Steps List */}
      {isExpanded && (
        <div className="p-4 space-y-2.5 max-h-64 overflow-y-auto font-mono text-xs">
          {actions.map((act) => {
            const isWaiting = act.status === "waiting";
            const isFailed = act.status === "failed";
            return (
              <div
                key={act.id}
                className="flex items-start gap-2.5 text-slate-300 leading-relaxed"
              >
                {isWaiting ? (
                  <span className="text-amber-400 font-bold mt-0.5">⏸</span>
                ) : isFailed ? (
                  <span className="text-rose-400 font-bold mt-0.5">✕</span>
                ) : (
                  <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400 mt-0.5 shrink-0" />
                )}
                <div className="flex-1">
                  <span className="text-slate-400 text-[11px] mr-1.5">[{act.tool}]</span>
                  <span className={isWaiting ? "text-amber-300 font-medium" : "text-slate-200"}>
                    {act.summary}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

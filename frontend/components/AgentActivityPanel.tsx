"use client";

import React, { useState } from "react";
import { CheckCircle2, ChevronDown, ChevronUp, Cpu, Loader2 } from "lucide-react";

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
    <div className="w-full bg-white dark:bg-[#0E1422] border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-subtle transition-all my-3">
      {/* Panel Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-2.5 bg-[#F5F8FC] dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between text-left hover:bg-slate-100/70 dark:hover:bg-slate-800/70 transition-colors cursor-pointer"
      >
        <div className="flex items-center gap-2">
          <Cpu className="w-4 h-4 text-[#0070E0] dark:text-[#38BDF8]" />
          <span className="text-xs font-bold uppercase tracking-wider text-[#14213D] dark:text-white">
            PayPilot Agent Activity
          </span>
          <span className="px-2 py-0.5 text-[10px] font-mono bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 rounded-full font-semibold">
            {actions.length} {actions.length === 1 ? "step" : "steps"}
          </span>
        </div>
        <div className="flex items-center gap-3">
          {currentStatus === "WAITING_FOR_APPROVAL" && (
            <span className="flex items-center gap-1.5 text-[11px] text-amber-600 dark:text-amber-400 font-semibold bg-amber-50 dark:bg-amber-950/60 px-2 py-0.5 rounded-full border border-amber-200 dark:border-amber-800">
              <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></span>
              Awaiting Approval
            </span>
          )}
          {isExpanded ? (
            <ChevronUp className="w-4 h-4 text-slate-500 dark:text-slate-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-slate-500 dark:text-slate-400" />
          )}
        </div>
      </button>

      {/* Action Steps List */}
      {isExpanded && (
        <div className="p-3.5 space-y-2 max-h-56 overflow-y-auto text-xs bg-white dark:bg-[#090D16]">
          {actions.map((act) => {
            const isWaiting = act.status === "waiting";
            const isFailed = act.status === "failed";
            const isRunning = act.status === "running";

            return (
              <div
                key={act.id}
                className="flex items-start gap-2.5 text-slate-700 dark:text-slate-300 leading-relaxed font-sans"
              >
                {isWaiting ? (
                  <span className="text-amber-500 font-bold mt-0.5 text-xs">⏸</span>
                ) : isFailed ? (
                  <span className="text-rose-500 font-bold mt-0.5 text-xs">✕</span>
                ) : isRunning ? (
                  <Loader2 className="w-3.5 h-3.5 text-[#0070E0] dark:text-[#38BDF8] animate-spin mt-0.5 shrink-0" />
                ) : (
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 dark:text-emerald-400 mt-0.5 shrink-0" />
                )}
                <div className="flex-1 font-mono text-[11px]">
                  <span className="text-[#0070E0] dark:text-[#38BDF8] font-semibold mr-1.5 bg-[#EAF3FF] dark:bg-[#0070E0]/20 px-1.5 py-0.2 rounded">
                    [{act.tool}]
                  </span>
                  <span
                    className={
                      isWaiting
                        ? "text-amber-700 dark:text-amber-400 font-medium font-sans"
                        : isFailed
                        ? "text-rose-700 dark:text-rose-400 font-sans"
                        : "text-slate-700 dark:text-slate-300 font-sans"
                    }
                  >
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

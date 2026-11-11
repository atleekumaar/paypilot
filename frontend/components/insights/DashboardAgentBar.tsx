"use client";

import React, { useState } from "react";
import { Sparkles, Send, Loader2, Lightbulb, Compass } from "lucide-react";
import { api } from "@/lib/api";

interface AgentQueryResult {
  intent: string;
  suggested_widget: string;
  title: string;
  summary: string;
  data: any;
  insights: string[];
}

interface DashboardAgentBarProps {
  onAgentResult: (result: AgentQueryResult) => void;
  onWidgetSelect?: (widget: string) => void;
}

export default function DashboardAgentBar({
  onAgentResult,
  onWidgetSelect,
}: DashboardAgentBarProps) {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [activeResult, setActiveResult] = useState<AgentQueryResult | null>(null);

  const presets = [
    "Compare laptop recommendations",
    "Show failed and pending payments",
    "Group spending by category",
    "Recent orders summary",
  ];

  const handleSearch = async (textToQuery?: string) => {
    const q = textToQuery || query;
    if (!q.trim() || loading) return;

    setLoading(true);
    try {
      const res = await api.post<AgentQueryResult>("/api/analytics/query", {
        query: q,
      });
      setActiveResult(res);
      onAgentResult(res);
      if (onWidgetSelect && res.suggested_widget) {
        onWidgetSelect(res.suggested_widget);
      }
    } catch (err) {
      console.error("AI Dashboard Agent error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 rounded-2xl bg-white dark:bg-gradient-to-r dark:from-slate-900/90 dark:via-cyan-950/30 dark:to-slate-900/90 border border-slate-200 dark:border-cyan-500/30 shadow-sm dark:shadow-2xl flex flex-col gap-4 transition-colors">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-cyan-50 dark:bg-cyan-500/20 border border-cyan-200 dark:border-cyan-500/40 text-cyan-600 dark:text-cyan-400">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-[#14213D] dark:text-white flex items-center gap-2">
              AG Studio AI Dashboard Agent
              <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full bg-cyan-50 dark:bg-cyan-950 border border-cyan-200 dark:border-cyan-800 text-cyan-700 dark:text-cyan-400">
                Constrained Analytics Engine
              </span>
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Ask natural-language questions across verified orders, payments, specs, and recommendation scores.
            </p>
          </div>
        </div>
      </div>

      {/* Query Bar */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSearch();
        }}
        className="flex gap-2"
      >
        <div className="relative flex-1">
          <Compass className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-cyan-600 dark:text-cyan-400" />
          <input
            type="text"
            placeholder="e.g. 'Compare top laptops', 'Show payment health exceptions', 'Group spending by category'..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-slate-50 dark:bg-slate-950/80 border border-slate-200 dark:border-slate-700/80 rounded-xl text-xs text-[#14213D] dark:text-white placeholder-slate-400 focus:outline-none focus:border-cyan-500 transition-colors"
          />
        </div>
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-medium text-xs flex items-center gap-1.5 shadow-lg shadow-cyan-600/20 disabled:opacity-50 transition-all shrink-0"
        >
          {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
          <span>Run Query</span>
        </button>
      </form>

      {/* Preset Pills */}
      <div className="flex flex-wrap items-center gap-2 text-xs">
        <span className="text-slate-400 dark:text-slate-500 text-[11px]">Quick Prompts:</span>
        {presets.map((p) => (
          <button
            key={p}
            type="button"
            onClick={() => {
              setQuery(p);
              handleSearch(p);
            }}
            className="px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-800/60 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 hover:text-[#14213D] dark:hover:text-white border border-slate-200 dark:border-slate-700/50 text-[11px] transition-colors"
          >
            {p}
          </button>
        ))}
      </div>

      {/* Active AI Insights Callout */}
      {activeResult && (
        <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-950/90 border border-cyan-200 dark:border-cyan-500/40 mt-2 space-y-2 animate-fadeIn">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Lightbulb className="w-4 h-4 text-amber-500 dark:text-amber-400" />
              <h4 className="text-xs font-bold text-[#14213D] dark:text-white">{activeResult.title}</h4>
            </div>
            <span className="text-[10px] uppercase font-bold text-cyan-700 dark:text-cyan-400 bg-cyan-50 dark:bg-cyan-950 px-2 py-0.5 rounded border border-cyan-200 dark:border-cyan-800">
              Widget: {activeResult.suggested_widget}
            </span>
          </div>
          <p className="text-xs text-slate-600 dark:text-slate-300">{activeResult.summary}</p>
          <div className="space-y-1 pt-1 border-t border-slate-200 dark:border-slate-800">
            {activeResult.insights.map((ins, i) => (
              <div key={i} className="text-[11px] text-slate-600 dark:text-slate-400 flex items-start gap-1.5">
                <span className="text-cyan-500 dark:text-cyan-400 font-bold">•</span>
                <span>{ins}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}


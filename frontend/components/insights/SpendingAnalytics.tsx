"use client";

import React from "react";
import { PieChart, TrendingUp, Filter, Sparkles, Layers } from "lucide-react";

interface SpendingData {
  spending_over_time: Array<{ date: string; amount: number; order_count: number }>;
  spending_by_category: Array<{ category: string; amount: number; percentage: number }>;
  payment_status_distribution: Array<{ status: string; count: number; amount: number }>;
}

interface SpendingAnalyticsProps {
  data: SpendingData | null;
  loading: boolean;
  selectedCategory: string | null;
  onSelectCategory: (cat: string | null) => void;
}

const CATEGORY_COLORS: Record<string, { gradient: string; bar: string; badge: string; text: string }> = {
  laptop: {
    gradient: "from-blue-600 via-cyan-500 to-cyan-400",
    bar: "bg-gradient-to-r from-blue-500 to-cyan-400",
    badge: "bg-cyan-950/70 text-cyan-300 border-cyan-800/60",
    text: "text-cyan-400",
  },
  phone: {
    gradient: "from-purple-600 via-fuchsia-500 to-pink-400",
    bar: "bg-gradient-to-r from-purple-500 to-pink-400",
    badge: "bg-purple-950/70 text-purple-300 border-purple-800/60",
    text: "text-purple-400",
  },
  monitor: {
    gradient: "from-emerald-600 via-teal-500 to-emerald-400",
    bar: "bg-gradient-to-r from-emerald-500 to-teal-400",
    badge: "bg-emerald-950/70 text-emerald-300 border-emerald-800/60",
    text: "text-emerald-400",
  },
  headphones: {
    gradient: "from-amber-600 via-amber-500 to-yellow-400",
    bar: "bg-gradient-to-r from-amber-500 to-yellow-400",
    badge: "bg-amber-950/70 text-amber-300 border-amber-800/60",
    text: "text-amber-400",
  },
  keyboard: {
    gradient: "from-indigo-600 via-indigo-500 to-violet-400",
    bar: "bg-gradient-to-r from-indigo-500 to-violet-400",
    badge: "bg-indigo-950/70 text-indigo-300 border-indigo-800/60",
    text: "text-indigo-400",
  },
};

const DEFAULT_CATEGORY_COLOR = {
  gradient: "from-slate-600 via-slate-500 to-slate-400",
  bar: "bg-gradient-to-r from-slate-500 to-slate-400",
  badge: "bg-slate-800 text-slate-300 border-slate-700",
  text: "text-slate-300",
};

export default function SpendingAnalytics({
  data,
  loading,
  selectedCategory,
  onSelectCategory,
}: SpendingAnalyticsProps) {
  if (loading || !data) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 p-6 rounded-2xl bg-slate-100 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 animate-pulse h-72" />
        <div className="p-6 rounded-2xl bg-slate-100 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 animate-pulse h-72" />
      </div>
    );
  }

  const maxSpend = Math.max(...data.spending_over_time.map((d) => d.amount), 1);
  const totalSpend = data.spending_over_time.reduce((acc, curr) => acc + curr.amount, 0);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* 1. Spending Over Time Bar Chart */}
      <div className="lg:col-span-2 p-6 rounded-2xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800/80 backdrop-blur-sm flex flex-col justify-between shadow-sm dark:shadow-xl transition-colors">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-cyan-50 dark:bg-cyan-500/10 border border-cyan-200 dark:border-cyan-500/20 text-cyan-600 dark:text-cyan-400">
              <TrendingUp className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-[#14213D] dark:text-white tracking-wide">Commerce Spending Timeline</h3>
              <p className="text-[11px] text-slate-500 dark:text-slate-400">Verified PayPal order settlements over time</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono font-bold text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800/50 px-2.5 py-0.5 rounded-full">
              Total ${totalSpend.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
          </div>
        </div>

        {/* Chart Canvas */}
        <div className="h-56 flex items-end gap-3 sm:gap-4 pt-8 pb-3 px-3 border-b border-slate-200 dark:border-slate-800/90 relative">
          {/* Background horizontal guide lines */}
          <div className="absolute inset-x-3 top-6 border-b border-slate-200 dark:border-slate-800/30 pointer-events-none" />
          <div className="absolute inset-x-3 top-24 border-b border-slate-200 dark:border-slate-800/30 pointer-events-none" />
          <div className="absolute inset-x-3 top-40 border-b border-slate-200 dark:border-slate-800/30 pointer-events-none" />

          {data.spending_over_time.map((item, idx) => {
            const heightPercent = Math.min(100, Math.max(20, Math.round((item.amount / maxSpend) * 100)));
            return (
              <div key={idx} className="flex-1 h-full flex flex-col justify-end items-center group relative z-10">
                {/* Value label directly above bar */}
                <span className="text-[10px] sm:text-xs font-mono font-bold text-cyan-600 dark:text-cyan-300 mb-1.5 transition-all duration-200 group-hover:scale-110 group-hover:text-[#14213D] dark:group-hover:text-white">
                  ${item.amount >= 1000 ? `${(item.amount / 1000).toFixed(1)}k` : Math.round(item.amount)}
                </span>

                {/* Vertical Bar */}
                <div
                  style={{ height: `${heightPercent}%` }}
                  className="w-full max-w-[44px] rounded-t-xl bg-gradient-to-t from-[#003087] via-[#0070E0] to-[#38BDF8] shadow-md shadow-[#0070E0]/20 transition-all duration-300 group-hover:brightness-125 group-hover:shadow-cyan-400/50 group-hover:scale-x-105"
                />

                {/* Date Label */}
                <span className="text-[10px] sm:text-[11px] font-mono text-slate-500 dark:text-slate-400 mt-2 truncate max-w-full font-medium">
                  {item.date.slice(5)}
                </span>

                {/* Floating Tooltip */}
                <div className="absolute -top-12 opacity-0 group-hover:opacity-100 transition-all duration-200 bg-slate-900 dark:bg-slate-950/95 text-[11px] text-white py-1.5 px-3 rounded-xl pointer-events-none whitespace-nowrap border border-slate-700 dark:border-cyan-500/40 shadow-2xl z-30">
                  <span className="font-bold text-cyan-300">${item.amount.toFixed(2)}</span>
                  <span className="text-slate-400 ml-1.5 font-sans">({item.order_count} order{item.order_count > 1 ? "s" : ""})</span>
                </div>
              </div>
            );
          })}
        </div>

        <div className="flex justify-between items-center text-xs text-slate-400 dark:text-slate-500 pt-3">
          <span className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-500 dark:bg-cyan-400"></span>
            Earliest Recorded Transaction
          </span>
          <span className="font-mono text-[11px] text-slate-500 dark:text-slate-400">Authoritative PayPal Rails</span>
        </div>
      </div>

      {/* 2. Spending by Category (Interactive Cross-Filtering) */}
      <div className="p-6 rounded-2xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800/80 backdrop-blur-sm flex flex-col justify-between shadow-sm dark:shadow-xl transition-colors">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-blue-50 dark:bg-blue-500/10 border border-blue-200 dark:border-blue-500/20 text-blue-600 dark:text-blue-400">
              <PieChart className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-[#14213D] dark:text-white tracking-wide">Category Distribution</h3>
              <p className="text-[11px] text-slate-500 dark:text-slate-400">Spending grouped by product vertical</p>
            </div>
          </div>
          {selectedCategory && (
            <button
              onClick={() => onSelectCategory(null)}
              className="text-[10px] font-semibold flex items-center gap-1 text-cyan-700 dark:text-cyan-300 hover:text-cyan-900 dark:hover:text-white bg-cyan-50 dark:bg-cyan-950/80 px-2.5 py-1 rounded-lg border border-cyan-200 dark:border-cyan-500/40 transition-colors cursor-pointer"
            >
              <Filter className="w-3 h-3" /> Clear Filter
            </button>
          )}
        </div>

        {/* Category List */}
        <div className="space-y-3 my-auto">
          {data.spending_by_category.map((cat) => {
            const isSelected = selectedCategory?.toLowerCase() === cat.category.toLowerCase();
            const colorCfg = CATEGORY_COLORS[cat.category.toLowerCase()] || DEFAULT_CATEGORY_COLOR;

            return (
              <div
                key={cat.category}
                onClick={() => onSelectCategory(isSelected ? null : cat.category)}
                className={`p-3 rounded-xl border transition-all duration-200 cursor-pointer ${
                  isSelected
                    ? "bg-cyan-50 dark:bg-cyan-500/15 border-cyan-400/70 shadow-md shadow-cyan-500/10 scale-[1.02]"
                    : "bg-slate-50 dark:bg-slate-800/40 border-slate-200 dark:border-slate-800/80 hover:border-slate-300 dark:hover:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800/70"
                }`}
              >
                <div className="flex justify-between items-center text-xs mb-2">
                  <div className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${colorCfg.text.replace('text-', 'bg-')}`}></span>
                    <span className={`font-bold capitalize ${isSelected ? "text-[#14213D] dark:text-white" : "text-slate-700 dark:text-slate-200"}`}>
                      {cat.category}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-bold text-[#14213D] dark:text-white">
                      ${cat.amount.toFixed(2)}
                    </span>
                    <span className={`text-[10px] font-mono px-1.5 py-0.2 rounded border font-bold ${colorCfg.badge}`}>
                      {cat.percentage}%
                    </span>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="w-full h-2 bg-slate-200 dark:bg-slate-800/90 rounded-full overflow-hidden p-0.5">
                  <div
                    style={{ width: `${Math.max(cat.percentage, 4)}%` }}
                    className={`h-full rounded-full transition-all duration-500 ${colorCfg.bar}`}
                  />
                </div>
              </div>
            );
          })}
        </div>

        <div className="text-[11px] text-slate-400 dark:text-slate-500 pt-3 flex items-center justify-between border-t border-slate-200 dark:border-slate-800/60 mt-3">
          <span className="flex items-center gap-1.5 text-cyan-600 dark:text-cyan-400 font-medium">
            <Sparkles className="w-3 h-3" />
            Click category to cross-filter
          </span>
          <span className="font-mono text-slate-500 dark:text-slate-400">{data.spending_by_category.length} categories</span>
        </div>
      </div>
    </div>
  );
}

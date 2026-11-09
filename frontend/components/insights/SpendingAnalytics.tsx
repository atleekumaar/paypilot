"use client";

import React from "react";
import { PieChart, TrendingUp, Filter } from "lucide-react";

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

export default function SpendingAnalytics({
  data,
  loading,
  selectedCategory,
  onSelectCategory,
}: SpendingAnalyticsProps) {
  if (loading || !data) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 p-6 rounded-2xl bg-slate-900/50 border border-slate-800 animate-pulse h-64" />
        <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800 animate-pulse h-64" />
      </div>
    );
  }

  const maxSpend = Math.max(...data.spending_over_time.map((d) => d.amount), 1);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Spending Over Time Bar Chart */}
      <div className="lg:col-span-2 p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-sm flex flex-col justify-between shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-semibold text-white">Commerce Spending Timeline</h3>
          </div>
          <span className="text-xs text-slate-400">Past Verified Orders</span>
        </div>

        <div className="h-44 flex items-end gap-3 pt-6 pb-2 px-2 border-b border-slate-800">
          {data.spending_over_time.map((item, idx) => {
            const heightPercent = Math.min(100, Math.max(12, Math.round((item.amount / maxSpend) * 100)));
            return (
              <div key={idx} className="flex-1 flex flex-col items-center gap-2 group relative">
                <div
                  style={{ height: `${heightPercent}%` }}
                  className="w-full rounded-t-md bg-gradient-to-t from-cyan-600/50 to-cyan-400 transition-all duration-300 group-hover:from-cyan-500 group-hover:to-cyan-300 group-hover:shadow-lg group-hover:shadow-cyan-500/20"
                />
                <span className="text-[10px] text-slate-500 truncate max-w-full">
                  {item.date.slice(5)}
                </span>
                {/* Tooltip on hover */}
                <div className="absolute -top-10 opacity-0 group-hover:opacity-100 transition-opacity bg-slate-800 text-[11px] text-white py-1 px-2 rounded pointer-events-none whitespace-nowrap border border-slate-700 shadow-lg z-20">
                  ${item.amount.toFixed(2)} ({item.order_count} ord)
                </div>
              </div>
            );
          })}
        </div>
        <div className="flex justify-between items-center text-xs text-slate-500 pt-3">
          <span>Earliest Recorded Transaction</span>
          <span>Authoritative Backend Settlement</span>
        </div>
      </div>

      {/* Spending by Category (Interactive Cross-Filtering) */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-sm flex flex-col justify-between shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <PieChart className="w-4 h-4 text-blue-400" />
            <h3 className="text-sm font-semibold text-white">Category Distribution</h3>
          </div>
          {selectedCategory && (
            <button
              onClick={() => onSelectCategory(null)}
              className="text-[10px] flex items-center gap-1 text-cyan-400 hover:text-cyan-300 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/50"
            >
              <Filter className="w-2.5 h-2.5" /> Clear Filter
            </button>
          )}
        </div>

        <div className="space-y-3.5 my-auto">
          {data.spending_by_category.map((cat) => {
            const isSelected = selectedCategory === cat.category;
            return (
              <div
                key={cat.category}
                onClick={() => onSelectCategory(isSelected ? null : cat.category)}
                className={`p-2.5 rounded-xl border transition-all cursor-pointer ${
                  isSelected
                    ? "bg-cyan-500/10 border-cyan-500/50 shadow-md shadow-cyan-500/10"
                    : "bg-slate-800/30 border-slate-800/70 hover:border-slate-700 hover:bg-slate-800/60"
                }`}
              >
                <div className="flex justify-between text-xs mb-1.5">
                  <span className={`font-medium ${isSelected ? "text-cyan-300" : "text-slate-200"}`}>
                    {cat.category}
                  </span>
                  <span className="text-slate-400">
                    ${cat.amount.toFixed(2)} ({cat.percentage}%)
                  </span>
                </div>
                <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    style={{ width: `${cat.percentage}%` }}
                    className={`h-full rounded-full transition-all ${
                      isSelected ? "bg-cyan-400" : "bg-blue-500"
                    }`}
                  />
                </div>
              </div>
            );
          })}
        </div>

        <div className="text-[11px] text-slate-500 pt-2 flex items-center justify-between">
          <span>Click to cross-filter intelligence grid</span>
          <span>{data.spending_by_category.length} categories</span>
        </div>
      </div>
    </div>
  );
}


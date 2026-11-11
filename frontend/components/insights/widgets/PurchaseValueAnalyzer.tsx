"use client";

import React from "react";
import { TrendingDown, CheckCircle, Percent, DollarSign } from "lucide-react";

interface PurchaseValueAnalyzerProps {
  avgOrderValue?: number;
  totalOrders?: number;
}

export default function PurchaseValueAnalyzer({
  avgOrderValue = 1049.0,
  totalOrders = 3,
}: PurchaseValueAnalyzerProps) {
  const estimatedSavings = 180.0;
  const savingsPct = 14.5;
  const costPerDay = (avgOrderValue / 1095).toFixed(2); // 3 year lifespan

  return (
    <div className="p-5 rounded-2xl bg-white dark:bg-gradient-to-br dark:from-slate-900/90 dark:via-slate-900/60 dark:to-slate-950/90 border border-slate-200 dark:border-emerald-500/30 shadow-sm dark:shadow-xl relative overflow-hidden transition-colors">
      <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/10 rounded-full blur-2xl pointer-events-none" />

      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-emerald-50 dark:bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-500/30">
            <Percent className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-[#14213D] dark:text-white">Purchase Value Analyzer</h3>
            <p className="text-[11px] text-slate-500 dark:text-slate-400">Total Cost of Ownership & Savings</p>
          </div>
        </div>
        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-50 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
          SAVING {savingsPct}%
        </span>
      </div>

      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-700/60">
          <div className="text-[10px] text-slate-500 dark:text-slate-400 uppercase font-semibold">Estimated Savings</div>
          <div className="text-lg font-bold text-emerald-600 dark:text-emerald-400 mt-1 flex items-center gap-1">
            <TrendingDown className="w-4 h-4" />
            ${estimatedSavings.toFixed(2)}
          </div>
          <div className="text-[10px] text-slate-400 dark:text-slate-500 mt-0.5">Vs. retail MSRP benchmark</div>
        </div>

        <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-700/60">
          <div className="text-[10px] text-slate-500 dark:text-slate-400 uppercase font-semibold">Daily Cost Index</div>
          <div className="text-lg font-bold text-cyan-600 dark:text-cyan-400 mt-1 flex items-center gap-1">
            <DollarSign className="w-4 h-4" />
            ${costPerDay} / day
          </div>
          <div className="text-[10px] text-slate-400 dark:text-slate-500 mt-0.5">Over 3-year useful lifespan</div>
        </div>
      </div>

      <div className="space-y-2 text-xs text-slate-600 dark:text-slate-300">
        <div className="flex items-center gap-2 p-2 rounded-lg bg-slate-50 dark:bg-slate-800/30 border border-slate-200 dark:border-slate-800">
          <CheckCircle className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
          <span>Optimal purchase price confirmed below category median.</span>
        </div>
        <div className="flex items-center gap-2 p-2 rounded-lg bg-slate-50 dark:bg-slate-800/30 border border-slate-200 dark:border-slate-800">
          <CheckCircle className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
          <span>Authorized vendor warranty with full buyer protection.</span>
        </div>
      </div>
    </div>
  );
}


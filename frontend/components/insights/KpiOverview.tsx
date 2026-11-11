"use client";

import React from "react";
import { DollarSign, ShoppingBag, CreditCard, AlertTriangle, Clock, TrendingUp } from "lucide-react";

interface KpiData {
  total_spending: number;
  total_orders: number;
  average_order_value: number;
  completed_payments: number;
  failed_payments: number;
  pending_orders: number;
  currency?: string;
}

interface KpiOverviewProps {
  data: KpiData | null;
  loading: boolean;
}

export default function KpiOverview({ data, loading }: KpiOverviewProps) {
  if (loading || !data) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="p-4 rounded-xl bg-slate-100 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 animate-pulse h-24" />
        ))}
      </div>
    );
  }

  const cards = [
    {
      title: "Total Spending",
      value: `$${data.total_spending.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      icon: DollarSign,
      color: "text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-500/10 border-emerald-200 dark:border-emerald-500/20",
    },
    {
      title: "Total Orders",
      value: data.total_orders,
      icon: ShoppingBag,
      color: "text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-500/10 border-blue-200 dark:border-blue-500/20",
    },
    {
      title: "Avg Order Value",
      value: `$${data.average_order_value.toFixed(2)}`,
      icon: TrendingUp,
      color: "text-cyan-600 dark:text-cyan-400 bg-cyan-50 dark:bg-cyan-500/10 border-cyan-200 dark:border-cyan-500/20",
    },
    {
      title: "Completed Payments",
      value: data.completed_payments,
      icon: CreditCard,
      color: "text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-500/10 border-indigo-200 dark:border-indigo-500/20",
    },
    {
      title: "Pending Orders",
      value: data.pending_orders,
      icon: Clock,
      color: "text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-500/10 border-amber-200 dark:border-amber-500/20",
    },
    {
      title: "Failed / Flagged",
      value: data.failed_payments,
      icon: AlertTriangle,
      color: data.failed_payments > 0 
        ? "text-rose-600 dark:text-rose-400 bg-rose-50 dark:bg-rose-500/10 border-rose-200 dark:border-rose-500/20" 
        : "text-slate-500 dark:text-slate-400 bg-slate-100 dark:bg-slate-800/40 border-slate-200 dark:border-slate-700/40",
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      {cards.map((c) => {
        const Icon = c.icon;
        return (
          <div
            key={c.title}
            className="p-4 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800/80 backdrop-blur-sm hover:border-slate-300 dark:hover:border-slate-700 transition-colors shadow-sm dark:shadow-lg dark:shadow-black/20"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-medium text-slate-500 dark:text-slate-400 tracking-wider uppercase">{c.title}</span>
              <div className={`p-1.5 rounded-lg border ${c.color}`}>
                <Icon className="w-3.5 h-3.5" />
              </div>
            </div>
            <div className="text-xl font-bold text-[#14213D] dark:text-white tracking-tight">{c.value}</div>
          </div>
        );
      })}
    </div>
  );
}


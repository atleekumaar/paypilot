"use client";

import React from "react";
import { ShieldAlert, Sparkles, CheckCircle2, XCircle, Loader2 } from "lucide-react";

interface PurchaseApprovalCardProps {
  productName: string;
  totalAmount: number;
  currency: string;
  reason?: string;
  onApprove: () => void;
  onDeny: () => void;
  isLoading?: boolean;
}

export default function PurchaseApprovalCard({
  productName,
  totalAmount,
  currency,
  reason,
  onApprove,
  onDeny,
  isLoading = false,
}: PurchaseApprovalCardProps) {
  return (
    <div className="w-full max-w-xl mx-auto bg-white dark:bg-[#0E1422] border-2 border-[#0070E0]/40 dark:border-[#0070E0]/60 rounded-2xl p-5 sm:p-6 shadow-card hover:shadow-cardHover transition-all my-5 text-left animate-in fade-in zoom-in-95">
      {/* Badge Header */}
      <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3 mb-4">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-full bg-amber-50 dark:bg-amber-950/50 flex items-center justify-center text-amber-600 dark:text-amber-400">
            <ShieldAlert className="w-4 h-4" />
          </div>
          <h4 className="text-xs font-bold uppercase tracking-wider text-[#14213D] dark:text-white">
            Human-in-the-Loop Approval Required
          </h4>
        </div>
        <div className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#EAF3FF] dark:bg-[#0070E0]/20 border border-[#0070E0]/20 dark:border-[#0070E0]/40 text-[#0070E0] dark:text-[#38BDF8] text-[11px] font-semibold">
          <span className="w-1.5 h-1.5 rounded-full bg-[#0070E0] dark:bg-[#38BDF8]"></span>
          <span>PayPal Sandbox</span>
        </div>
      </div>

      {/* Main Item & Price */}
      <div className="flex items-baseline justify-between mb-4">
        <div>
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            Selected Product
          </span>
          <h3 className="text-lg sm:text-xl font-bold text-[#14213D] dark:text-white mt-0.5">
            {productName}
          </h3>
        </div>
        <div className="text-right">
          <span className="text-[11px] font-medium text-slate-500 dark:text-slate-400">Total Price</span>
          <div className="text-2xl font-extrabold text-[#003087] dark:text-[#38BDF8] font-mono tracking-tight">
            ${totalAmount.toLocaleString("en-US", { minimumFractionDigits: 2 })}
            <span className="text-xs text-slate-500 dark:text-slate-400 font-sans font-medium ml-1">
              {currency}
            </span>
          </div>
        </div>
      </div>

      {/* Grounded Rationale */}
      <div className="p-3.5 rounded-xl bg-[#F5F8FC] dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 mb-5 text-xs text-slate-700 dark:text-slate-300">
        <div className="flex items-center gap-1.5 text-[#0070E0] dark:text-[#38BDF8] font-semibold mb-1">
          <Sparkles className="w-3.5 h-3.5" />
          PayPilot Selected This Because:
        </div>
        <p className="leading-relaxed">
          {reason || "Top-performing recommendation satisfying your budget, specifications, and safety policies."}
        </p>
      </div>

      {/* Approval Buttons */}
      <div className="flex gap-3">
        <button
          type="button"
          onClick={onDeny}
          disabled={isLoading}
          className="flex-1 py-3 px-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-bold uppercase tracking-wider transition-all disabled:opacity-50 cursor-pointer flex items-center justify-center gap-1.5"
        >
          <XCircle className="w-4 h-4 text-slate-400" />
          <span>Deny</span>
        </button>
        <button
          type="button"
          onClick={onApprove}
          disabled={isLoading}
          className="flex-1 py-3 px-4 rounded-xl bg-[#0070E0] hover:bg-[#005bb5] text-white text-xs font-bold uppercase tracking-wider shadow-sm hover:shadow transition-all disabled:opacity-50 cursor-pointer flex items-center justify-center gap-1.5"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin text-white" />
              <span>Processing...</span>
            </>
          ) : (
            <>
              <CheckCircle2 className="w-4 h-4 text-white" />
              <span>Approve Purchase</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}

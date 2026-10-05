"use client";

import React from "react";
import { CheckCircle, ShieldAlert, Sparkles, XCircle } from "lucide-react";

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
    <div className="w-full max-w-lg mx-auto bg-gradient-to-b from-[#121c33] to-[#0a0f1d] border-2 border-cyan-500/80 rounded-2xl p-6 shadow-2xl shadow-cyan-500/10 my-6 animate-in fade-in zoom-in-95 text-left">
      {/* Badge Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-amber-400" />
          <h4 className="text-sm font-extrabold uppercase tracking-wider text-white">
            Human-in-the-Loop Approval Required
          </h4>
        </div>
        <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-cyan-950/80 border border-cyan-500/30 text-cyan-400 text-[11px] font-semibold">
          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
          <span>PayPal Sandbox</span>
        </div>
      </div>

      {/* Main Item & Price */}
      <div className="flex items-baseline justify-between mb-4">
        <div>
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
            Selected Product
          </span>
          <h3 className="text-xl font-extrabold text-white mt-0.5">{productName}</h3>
        </div>
        <div className="text-right">
          <span className="text-[11px] text-slate-400">Total Price</span>
          <div className="text-2xl font-black text-cyan-400 font-mono">
            ${totalAmount.toLocaleString("en-US", { minimumFractionDigits: 2 })}
            <span className="text-xs text-slate-400 font-normal ml-1">{currency}</span>
          </div>
        </div>
      </div>

      {/* Grounded Rationale */}
      <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 mb-6 text-xs text-slate-300">
        <div className="flex items-center gap-1.5 text-cyan-400 font-semibold mb-1.5">
          <Sparkles className="w-3.5 h-3.5" />
          PayPilot selected this because:
        </div>
        <p className="leading-relaxed">
          {reason || "Top-performing recommendation satisfying your budget and technical requirements."}
        </p>
      </div>

      {/* Approval Buttons */}
      <div className="flex gap-3">
        <button
          type="button"
          onClick={onDeny}
          disabled={isLoading}
          className="flex-1 py-3 rounded-xl border border-slate-700 bg-slate-900/80 hover:bg-slate-800 text-slate-300 hover:text-white text-xs font-bold uppercase tracking-wider transition-all disabled:opacity-50"
        >
          Deny
        </button>
        <button
          type="button"
          onClick={onApprove}
          disabled={isLoading}
          className="flex-1 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-xs font-bold uppercase tracking-wider shadow-lg shadow-cyan-500/25 transition-all disabled:opacity-50"
        >
          {isLoading ? "Processing..." : "Approve Purchase"}
        </button>
      </div>
    </div>
  );
}

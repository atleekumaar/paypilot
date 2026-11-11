"use client";

import React, { useMemo, useRef, useState } from "react";
import { AgGridReact } from "ag-grid-react";
import { ColDef, ModuleRegistry, AllCommunityModule } from "ag-grid-community";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-quartz.css";
import { CreditCard, Search, ShieldCheck } from "lucide-react";

ModuleRegistry.registerModules([AllCommunityModule]);

export interface PaymentRecord {
  payment_id: string;
  purchase_plan_id: string;
  provider_order_id: string;
  amount: number;
  currency: string;
  provider: string;
  status: string;
  capture_id: string | null;
  refund_id?: string | null;
  refund_status?: string | null;
  total_refunded?: number;
  verification_status: string;
  payer_email?: string | null;
  created_at: string | null;
}

interface PaymentIntelligenceGridProps {
  payments: PaymentRecord[];
  loading: boolean;
}

export default function PaymentIntelligenceGrid({ payments, loading }: PaymentIntelligenceGridProps) {
  const [quickFilter, setQuickFilter] = useState("");
  const gridRef = useRef<AgGridReact>(null);

  const columnDefs = useMemo<ColDef<PaymentRecord>[]>(() => [
    {
      field: "payment_id",
      headerName: "Payment ID",
      width: 150,
      filter: true,
      cellRenderer: (params: any) => (
        <span className="font-mono text-cyan-400 font-semibold">{params.value}</span>
      ),
    },
    {
      field: "amount",
      headerName: "Amount",
      width: 120,
      filter: "agNumberColumnFilter",
      cellRenderer: (params: any) => (
        <span className="font-bold text-emerald-400">${Number(params.value).toFixed(2)}</span>
      ),
    },
    {
      field: "status",
      headerName: "Payment Status",
      width: 140,
      filter: true,
      cellRenderer: (params: any) => {
        const s = String(params.value).toUpperCase();
        let color = "text-emerald-400 bg-emerald-950/60 border-emerald-500/40";
        if (s.includes("REFUND")) color = "text-amber-400 bg-amber-950/60 border-amber-500/40";
        if (s.includes("FAIL") || s.includes("CANCEL")) color = "text-rose-400 bg-rose-950/60 border-rose-500/40";
        return (
          <span className={`px-2 py-0.5 rounded text-xs font-semibold border ${color}`}>
            {s}
          </span>
        );
      },
    },
    {
      field: "verification_status",
      headerName: "Provider Verification",
      width: 170,
      cellRenderer: (params: any) => (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-950/70 border border-emerald-500/40 text-emerald-300">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          PayPal Verified
        </span>
      ),
    },
    {
      field: "provider_order_id",
      headerName: "PayPal Order ID",
      flex: 1,
      minWidth: 160,
      filter: true,
      cellRenderer: (params: any) => (
        <span className="font-mono text-slate-400 text-xs truncate">{params.value}</span>
      ),
    },
    {
      field: "capture_id",
      headerName: "Capture ID",
      width: 160,
      cellRenderer: (params: any) => (
        <span className="font-mono text-slate-300 text-xs">
          {params.value || "Sync Pending"}
        </span>
      ),
    },
    {
      field: "total_refunded",
      headerName: "Refunded",
      width: 120,
      cellRenderer: (params: any) => (
        <span className="text-slate-400 text-xs">
          {params.value ? `$${Number(params.value).toFixed(2)}` : "$0.00"}
        </span>
      ),
    },
  ], []);

  const defaultColDef = useMemo<ColDef>(() => ({
    sortable: true,
    resizable: true,
  }), []);

  return (
    <div className="p-6 rounded-2xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800/80 backdrop-blur-sm shadow-sm dark:shadow-xl flex flex-col gap-4 transition-colors">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
        <div className="flex items-center gap-2">
          <CreditCard className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
          <div>
            <h3 className="text-base font-bold text-[#14213D] dark:text-white tracking-wide">Payment Intelligence</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">PayPal Orders API v2 capture tracking, verification audits, and refund ledger.</p>
          </div>
        </div>

        <div className="relative w-full sm:w-64">
          <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search payments, captures..."
            value={quickFilter}
            onChange={(e) => setQuickFilter(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/80 rounded-xl text-xs text-[#14213D] dark:text-white placeholder-slate-400 focus:outline-none focus:border-cyan-500 transition-colors"
          />
        </div>
      </div>

      <div className="ag-theme-quartz w-full h-[300px] rounded-xl overflow-hidden border border-slate-200 dark:border-slate-800 shadow-inner">
        <AgGridReact
          ref={gridRef}
          rowData={payments}
          columnDefs={columnDefs}
          defaultColDef={defaultColDef}
          quickFilterText={quickFilter}
          pagination={true}
          paginationPageSize={5}
          loading={loading}
        />
      </div>
    </div>
  );
}


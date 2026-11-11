"use client";

import React, { useMemo, useRef, useState } from "react";
import { AgGridReact } from "ag-grid-react";
import { ColDef, ModuleRegistry, AllCommunityModule } from "ag-grid-community";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-quartz.css";
import { Package, Search, Truck, CheckCircle2 } from "lucide-react";

ModuleRegistry.registerModules([AllCommunityModule]);

export interface OrderRecord {
  order_id: string;
  product_name: string;
  brand: string;
  quantity: number;
  amount: number;
  currency: string;
  order_status: string;
  order_date: string | null;
  paypal_order_id?: string;
  payment_id?: string;
  shipment_status?: string;
  carrier?: string;
  tracking_number?: string;
}

interface OrderIntelligenceGridProps {
  orders: OrderRecord[];
  loading: boolean;
}

export default function OrderIntelligenceGrid({ orders, loading }: OrderIntelligenceGridProps) {
  const [quickFilter, setQuickFilter] = useState("");
  const gridRef = useRef<AgGridReact>(null);

  const columnDefs = useMemo<ColDef<OrderRecord>[]>(() => [
    {
      field: "order_id",
      headerName: "Order ID",
      width: 140,
      filter: true,
      cellRenderer: (params: any) => (
        <span className="font-mono text-cyan-400 font-semibold">{params.value}</span>
      ),
    },
    {
      field: "product_name",
      headerName: "Product",
      flex: 2,
      minWidth: 200,
      filter: true,
      cellRenderer: (params: any) => (
        <div>
          <span className="font-medium text-[#14213D] dark:text-white">{params.value}</span>
          <span className="text-[11px] text-slate-500 dark:text-slate-400 block">{params.data.brand} (Qty: {params.data.quantity})</span>
        </div>
      ),
    },
    {
      field: "amount",
      headerName: "Amount",
      width: 130,
      filter: "agNumberColumnFilter",
      cellRenderer: (params: any) => (
        <span className="font-bold text-emerald-400">${Number(params.value).toFixed(2)}</span>
      ),
    },
    {
      field: "order_status",
      headerName: "Order Status",
      width: 140,
      filter: true,
      cellRenderer: (params: any) => {
        const s = String(params.value).toUpperCase();
        let color = "text-blue-400 bg-blue-950/60 border-blue-500/40";
        if (s === "DELIVERED") color = "text-emerald-400 bg-emerald-950/60 border-emerald-500/40";
        if (s === "IN_TRANSIT") color = "text-amber-400 bg-amber-950/60 border-amber-500/40";
        return (
          <span className={`px-2 py-0.5 rounded text-xs font-semibold border ${color}`}>
            {s}
          </span>
        );
      },
    },
    {
      field: "shipment_status",
      headerName: "Shipment Tracking",
      width: 180,
      cellRenderer: (params: any) => (
        <div className="flex items-center gap-1.5 text-xs text-slate-300">
          <Truck className="w-3.5 h-3.5 text-cyan-400" />
          <span>{params.data.carrier || "FedEx"}: {params.value || "In Transit"}</span>
        </div>
      ),
    },
    {
      field: "order_date",
      headerName: "Date",
      width: 140,
      filter: true,
      cellRenderer: (params: any) => (
        <span className="text-slate-400 text-xs">
          {params.value ? params.value.slice(0, 10) : "2026-10-12"}
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
          <Package className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          <div>
            <h3 className="text-base font-bold text-[#14213D] dark:text-white tracking-wide">Order Intelligence Grid</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">Post-purchase order lifecycle, logistics tracking, and verified settlements.</p>
          </div>
        </div>

        <div className="relative w-full sm:w-64">
          <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search orders, tracking..."
            value={quickFilter}
            onChange={(e) => setQuickFilter(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/80 rounded-xl text-xs text-[#14213D] dark:text-white placeholder-slate-400 focus:outline-none focus:border-cyan-500 transition-colors"
          />
        </div>
      </div>

      <div className="ag-theme-quartz w-full h-[320px] rounded-xl overflow-hidden border border-slate-200 dark:border-slate-800 shadow-inner">
        <AgGridReact
          ref={gridRef}
          rowData={orders}
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


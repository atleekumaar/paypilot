"use client";

import React, { useMemo, useState } from "react";
import Link from "next/link";
import { AgGridReact } from "ag-grid-react";
import {
  ColDef,
  ModuleRegistry,
  AllCommunityModule,
  ICellRendererParams,
  ValueFormatterParams,
} from "ag-grid-community";
import {
  Package,
  Truck,
  CheckCircle2,
  Clock,
  AlertTriangle,
  ChevronRight,
  ShieldCheck,
  Search,
  ExternalLink,
} from "lucide-react";

// Register all AG Grid Community features
ModuleRegistry.registerModules([AllCommunityModule]);

export interface TimelineEvent {
  title: string;
  description: string;
  timestamp: string;
  completed: boolean;
  current: boolean;
}

export interface Shipment {
  id: string;
  order_id: string;
  tracking_number: string;
  carrier: string;
  status: string;
  estimated_delivery: string;
  actual_delivery?: string | null;
  last_location: string;
  last_update: string;
  timeline: TimelineEvent[];
}

export interface OrderRow {
  id: string;
  user_id: string;
  purchase_plan_id: string;
  paypal_order_id?: string;
  payment_id?: string;
  product_id: string;
  product_name: string;
  brand?: string;
  quantity: number;
  amount: number;
  currency: string;
  status: string;
  created_at: string;
  updated_at: string;
  shipment?: Shipment;
}

interface OrdersGridProps {
  orders: OrderRow[];
  loading?: boolean;
  quickFilterText?: string;
}

export default function OrdersGrid({
  orders,
  loading = false,
  quickFilterText = "",
}: OrdersGridProps) {
  // Column Definitions
  const columnDefs = useMemo<ColDef<OrderRow>[]>(() => {
    return [
      {
        headerName: "Order ID",
        field: "id",
        width: 140,
        pinned: "left",
        sortable: true,
        filter: "agTextColumnFilter",
        cellRenderer: (params: ICellRendererParams<OrderRow>) => {
          if (!params.data) return null;
          return (
            <div className="flex items-center h-full">
              <Link
                href={`/orders/${params.data.id}`}
                className="inline-flex items-center gap-1 font-mono font-bold text-xs bg-[#F5F8FC] hover:bg-[#EAF3FF] border border-slate-200 hover:border-[#0070E0]/30 text-slate-700 hover:text-[#0070E0] px-2.5 py-1 rounded-md transition-colors"
                title={`View order ${params.data.id}`}
              >
                <span>{params.data.id}</span>
                <ExternalLink className="w-3 h-3 opacity-60" />
              </Link>
            </div>
          );
        },
      },
      {
        headerName: "Product Description",
        field: "product_name",
        flex: 2,
        minWidth: 240,
        sortable: true,
        filter: "agTextColumnFilter",
        cellRenderer: (params: ICellRendererParams<OrderRow>) => {
          if (!params.data) return null;
          return (
            <div className="flex items-center gap-3 h-full py-1">
              <div className="w-9 h-9 rounded-xl bg-[#EAF3FF] border border-[#0070E0]/20 flex items-center justify-center shrink-0 text-[#0070E0]">
                <Package className="w-4 h-4" />
              </div>
              <div className="min-w-0 flex-1">
                <Link
                  href={`/orders/${params.data.id}`}
                  className="font-bold text-xs sm:text-sm text-[#14213D] hover:text-[#0070E0] truncate block transition-colors"
                >
                  {params.data.product_name}
                </Link>
                <div className="text-[11px] text-slate-500 flex items-center gap-2 mt-0.5">
                  <span>
                    Brand:{" "}
                    <strong className="text-slate-700">
                      {params.data.brand || "Standard"}
                    </strong>
                  </span>
                  <span>&bull;</span>
                  <span>Qty: {params.data.quantity || 1}</span>
                </div>
              </div>
            </div>
          );
        },
      },
      {
        headerName: "Order Date",
        field: "created_at",
        width: 170,
        sortable: true,
        filter: "agDateColumnFilter",
        valueFormatter: (params: ValueFormatterParams<OrderRow>) => {
          if (!params.value) return "—";
          try {
            const date = new Date(params.value);
            return date.toLocaleDateString("en-US", {
              month: "short",
              day: "numeric",
              year: "numeric",
              hour: "2-digit",
              minute: "2-digit",
            });
          } catch {
            return String(params.value);
          }
        },
        cellRenderer: (params: ICellRendererParams<OrderRow>) => {
          return (
            <div className="flex items-center h-full text-xs text-slate-600 font-medium">
              {params.valueFormatted}
            </div>
          );
        },
      },
      {
        headerName: "Order Status",
        field: "status",
        width: 170,
        sortable: true,
        filter: "agTextColumnFilter",
        cellRenderer: (params: ICellRendererParams<OrderRow>) => {
          if (!params.data) return null;
          const status = params.data.status;
          const shipment = params.data.shipment;
          const isDelayed =
            shipment?.last_update &&
            shipment.last_update.toLowerCase().includes("delay");

          if (isDelayed) {
            return (
              <div className="flex items-center h-full">
                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
                  Delayed
                </span>
              </div>
            );
          }

          switch (status) {
            case "DELIVERED":
              return (
                <div className="flex items-center h-full">
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                    Delivered
                  </span>
                </div>
              );
            case "IN_TRANSIT":
              return (
                <div className="flex items-center h-full">
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-[#EAF3FF] text-[#0070E0] border border-[#0070E0]/20">
                    <Truck className="w-3.5 h-3.5 text-[#0070E0]" />
                    In Transit
                  </span>
                </div>
              );
            case "SHIPPED":
              return (
                <div className="flex items-center h-full">
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
                    <Package className="w-3.5 h-3.5 text-blue-600" />
                    Shipped
                  </span>
                </div>
              );
            case "PROCESSING":
              return (
                <div className="flex items-center h-full">
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-purple-50 text-purple-700 border border-purple-200">
                    <Clock className="w-3.5 h-3.5 text-purple-600" />
                    Processing
                  </span>
                </div>
              );
            default:
              return (
                <div className="flex items-center h-full">
                  <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200">
                    {status}
                  </span>
                </div>
              );
          }
        },
      },
      {
        headerName: "Total Amount",
        field: "amount",
        width: 140,
        sortable: true,
        filter: "agNumberColumnFilter",
        cellRenderer: (params: ICellRendererParams<OrderRow>) => {
          if (!params.data) return null;
          const currency = params.data.currency || "USD";
          const amount = Number(params.data.amount || 0).toFixed(2);
          return (
            <div className="flex items-center h-full font-mono font-bold text-xs text-[#003087]">
              ${amount} {currency}
            </div>
          );
        },
      },
      {
        headerName: "Payment Status",
        field: "paypal_order_id",
        width: 170,
        minWidth: 160,
        sortable: true,
        filter: "agTextColumnFilter",
        cellRenderer: (params: ICellRendererParams<OrderRow>) => {
          if (!params.data) return null;
          if (params.data.paypal_order_id) {
            return (
              <div className="flex items-center h-full">
                <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-semibold text-[#0070E0] bg-[#EAF3FF] border border-[#0070E0]/30" title={`PayPal Order: ${params.data.paypal_order_id}`}>
                  <ShieldCheck className="w-3.5 h-3.5 text-[#0070E0]" />
                  PayPal Verified
                </span>
              </div>
            );
          }
          return (
            <div className="flex items-center h-full text-xs text-slate-400">
              Direct Payment
            </div>
          );
        },
      },
      {
        headerName: "Action",
        width: 120,
        minWidth: 110,
        sortable: false,
        filter: false,
        cellRenderer: (params: ICellRendererParams<OrderRow>) => {
          if (!params.data) return null;
          return (
            <div className="flex items-center h-full">
              <Link
                href={`/orders/${params.data.id}`}
                className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-[#0070E0] hover:bg-[#005bb5] text-white text-xs font-bold transition-all shadow-xs cursor-pointer"
              >
                <span>Track</span>
                <ChevronRight className="w-3 h-3" />
              </Link>
            </div>
          );
        },
      },
    ];
  }, []);

  // Default Column Config
  const defaultColDef = useMemo<ColDef>(() => {
    return {
      resizable: true,
      sortable: true,
      filter: true,
    };
  }, []);

  return (
    <div className="w-full">
      <div
        className="ag-theme-quartz w-full shadow-subtle rounded-2xl overflow-hidden bg-white"
        style={{ height: "540px" }}
      >
        <AgGridReact<OrderRow>
          rowData={orders}
          columnDefs={columnDefs}
          defaultColDef={defaultColDef}
          quickFilterText={quickFilterText}
          pagination={true}
          paginationPageSize={10}
          paginationPageSizeSelector={[10, 25, 50]}
          rowHeight={64}
          headerHeight={44}
          animateRows={true}
          loading={loading}
          noRowsOverlayComponent={() => (
            <div className="flex flex-col items-center justify-center p-8 text-slate-500">
              <Package className="w-10 h-10 text-slate-300 mb-2" />
              <p className="text-sm font-bold text-slate-700">No matching orders found</p>
              <p className="text-xs text-slate-400 mt-0.5">
                Adjust your filters or query to display order history.
              </p>
            </div>
          )}
        />
      </div>
    </div>
  );
}

"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import Navbar from "@/components/Navbar";
import OrdersGrid, { OrderRow } from "@/components/OrdersGrid";
import {
  Package,
  Truck,
  CheckCircle2,
  Clock,
  AlertTriangle,
  ChevronRight,
  RefreshCw,
  MessageSquare,
  ShieldCheck,
  Search,
  LayoutGrid,
  Table as TableIcon,
  AlertCircle,
} from "lucide-react";
import { API_BASE_URL } from "@/lib/api";

export default function OrdersPage() {
  const [orders, setOrders] = useState<OrderRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [viewMode, setViewMode] = useState<"grid" | "cards">("grid");

  const fetchOrders = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/api/orders?user_id=guest_user`);
      if (!res.ok) {
        throw new Error(`Failed to fetch orders (HTTP ${res.status})`);
      }
      const data = await res.json();
      setOrders(data);
    } catch (err: any) {
      console.warn("Failed to fetch orders from backend:", err);
      setError(err.message || "Unable to connect to order service.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  const filteredOrders = orders.filter((o) => {
    const matchesFilter = filter === "ALL" || o.status === filter;
    if (!matchesFilter) return false;
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      o.id.toLowerCase().includes(q) ||
      o.product_name.toLowerCase().includes(q) ||
      (o.brand && o.brand.toLowerCase().includes(q)) ||
      (o.paypal_order_id && o.paypal_order_id.toLowerCase().includes(q))
    );
  });

  const getStatusBadge = (status: string, lastUpdate?: string) => {
    const isDelayed = lastUpdate && lastUpdate.toLowerCase().includes("delay");

    if (isDelayed) {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
          <AlertTriangle className="w-3 h-3 text-amber-500" />
          Delayed In Transit
        </span>
      );
    }

    switch (status) {
      case "DELIVERED":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
            <CheckCircle2 className="w-3 h-3 text-emerald-600" />
            Delivered
          </span>
        );
      case "IN_TRANSIT":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-[#EAF3FF] text-[#0070E0] border border-[#0070E0]/20">
            <Truck className="w-3 h-3 text-[#0070E0]" />
            In Transit
          </span>
        );
      case "SHIPPED":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
            <Package className="w-3 h-3 text-blue-600" />
            Shipped
          </span>
        );
      case "PROCESSING":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-purple-50 text-purple-700 border border-purple-200">
            <Clock className="w-3 h-3 text-purple-600" />
            Processing
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200">
            {status}
          </span>
        );
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-[#F5F8FC]/50 dark:bg-[#090D16] text-[#14213D] dark:text-slate-100 transition-colors duration-200">
      <Navbar />

      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 py-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-200 dark:border-slate-800 mb-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-[#0070E0]/20 bg-[#EAF3FF] dark:bg-[#0070E0]/20 text-[#0070E0] dark:text-[#38BDF8] text-xs font-bold mb-2">
              <Package className="w-3.5 h-3.5" />
              Verified PayPal Purchases &amp; Logistics
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-[#14213D] dark:text-white tracking-tight">
              My Orders &amp; Shipment Tracking
            </h1>
            <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 mt-1">
              Interactive AG Grid order ledger, authoritative PayPal records, and real-time shipment milestones.
            </p>
          </div>

          <div className="flex items-center gap-2 self-start sm:self-auto">
            {/* View Mode Toggle */}
            <div className="flex items-center bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-1 shadow-2xs">
              <button
                onClick={() => setViewMode("grid")}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                  viewMode === "grid"
                    ? "bg-[#0070E0] text-white shadow-xs"
                    : "text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white"
                }`}
                title="Table View (AG Grid)"
              >
                <TableIcon className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">AG Grid</span>
              </button>
              <button
                onClick={() => setViewMode("cards")}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                  viewMode === "cards"
                    ? "bg-[#0070E0] text-white shadow-xs"
                    : "text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white"
                }`}
                title="Card View"
              >
                <LayoutGrid className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Cards</span>
              </button>
            </div>

            <button
              onClick={fetchOrders}
              className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 text-xs font-bold text-slate-700 dark:text-slate-200 shadow-2xs transition-colors cursor-pointer"
            >
              <RefreshCw className={`w-3.5 h-3.5 text-slate-500 dark:text-slate-400 ${loading ? "animate-spin" : ""}`} />
              Refresh
            </button>
          </div>
        </div>

        {/* Filter & Search Bar */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 mb-5">
          {/* Status Filter Chips */}
          <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
            {["ALL", "IN_TRANSIT", "PROCESSING", "DELIVERED"].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-3.5 py-1.5 rounded-full font-bold transition-all whitespace-nowrap cursor-pointer ${
                  filter === f
                    ? "bg-[#0070E0] text-white shadow-xs"
                    : "bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-50 dark:hover:bg-slate-700"
                }`}
              >
                {f.replace("_", " ")}
              </button>
            ))}
          </div>

          {/* Quick Search */}
          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search orders, products, brands..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-slate-200 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0070E0]/20 focus:border-[#0070E0] transition-all"
            />
          </div>
        </div>

        {/* Error State */}
        {error && (
          <div className="mb-6 p-4 rounded-2xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 flex items-center justify-between gap-3 text-red-800 dark:text-red-300 text-xs">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-red-600 shrink-0" />
              <span>{error}</span>
            </div>
            <button
              onClick={fetchOrders}
              className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded-lg font-bold transition-colors shrink-0"
            >
              Retry
            </button>
          </div>
        )}

        {/* Orders Content */}
        {loading && orders.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-slate-500 dark:text-slate-400 bg-white dark:bg-[#0E1422] rounded-3xl border border-slate-200 dark:border-slate-800 shadow-subtle">
            <RefreshCw className="w-8 h-8 animate-spin text-[#0070E0] dark:text-[#38BDF8] mb-3" />
            <p className="text-sm font-bold text-slate-800 dark:text-slate-200">Loading order ledger...</p>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Connecting to authoritative order service</p>
          </div>
        ) : filteredOrders.length === 0 ? (
          <div className="text-center py-16 px-4 rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0E1422] shadow-subtle">
            <div className="w-14 h-14 rounded-2xl bg-[#EAF3FF] dark:bg-[#0070E0]/20 text-[#0070E0] dark:text-[#38BDF8] flex items-center justify-center mx-auto mb-3">
              <Package className="w-7 h-7" />
            </div>
            <h3 className="text-base font-bold text-[#14213D] dark:text-white mb-1">No Orders Found</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 max-w-sm mx-auto mb-5 leading-relaxed">
              You do not have any orders matching the selected filter. Try discovering products with the PayPilot Assistant!
            </p>
            <Link
              href="/"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-[#0070E0] text-white text-xs font-bold hover:bg-[#005bb5] transition-colors shadow-xs"
            >
              Start Shopping with PayPilot
            </Link>
          </div>
        ) : viewMode === "grid" ? (
          /* AG Grid View */
          <OrdersGrid
            orders={filteredOrders}
            loading={loading}
            quickFilterText={searchQuery}
          />
        ) : (
          /* Card View (Fallback / Responsive Mobile) */
          <div className="grid grid-cols-1 gap-4">
            {filteredOrders.map((order) => {
              const shipment = order.shipment;
              const isDelayed = shipment?.last_update?.toLowerCase().includes("delay");

              return (
                <div
                  key={order.id}
                  className="rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0E1422] shadow-subtle hover:shadow-card transition-all p-5 sm:p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-5 group"
                >
                  <div className="flex items-start gap-4 flex-1 min-w-0">
                    <div className="w-12 h-12 rounded-2xl bg-[#EAF3FF] dark:bg-[#0070E0]/20 border border-[#0070E0]/20 dark:border-[#0070E0]/40 flex items-center justify-center shrink-0 text-[#0070E0] dark:text-[#38BDF8]">
                      <Package className="w-6 h-6" />
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex flex-wrap items-center gap-2 mb-1.5">
                        <span className="text-xs font-mono font-bold text-slate-600 dark:text-slate-300 bg-[#F5F8FC] dark:bg-slate-800 border border-slate-200 dark:border-slate-700 px-2.5 py-0.5 rounded-md">
                          {order.id}
                        </span>
                        {getStatusBadge(order.status, shipment?.last_update)}
                        {order.paypal_order_id && (
                          <span className="text-[11px] font-mono font-semibold text-[#0070E0] dark:text-[#38BDF8] bg-[#EAF3FF] dark:bg-[#0070E0]/20 border border-[#0070E0]/30 px-2 py-0.5 rounded-md flex items-center gap-1">
                            <ShieldCheck className="w-3 h-3 text-[#0070E0] dark:text-[#38BDF8]" />
                            PayPal Verified
                          </span>
                        )}
                      </div>

                      <h3 className="text-base sm:text-lg font-bold text-[#14213D] dark:text-white group-hover:text-[#0070E0] dark:group-hover:text-[#38BDF8] transition-colors truncate">
                        {order.product_name}
                      </h3>

                      <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                        Brand: <span className="text-slate-800 dark:text-slate-200 font-semibold">{order.brand || "Standard"}</span> &bull; Total:{" "}
                        <span className="text-[#003087] dark:text-[#38BDF8] font-black font-mono">
                          ${Number(order.amount).toFixed(2)} {order.currency}
                        </span>
                      </p>

                      {/* Shipment Snippet */}
                      {shipment && (
                        <div className="mt-3.5 text-xs bg-[#F5F8FC] dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700/60 rounded-2xl p-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                          <div className="flex items-center gap-2 text-slate-700 dark:text-slate-300 truncate">
                            <Truck className="w-4 h-4 text-[#0070E0] dark:text-[#38BDF8] shrink-0" />
                            <span className="truncate">{shipment.last_update}</span>
                          </div>
                          <div className="text-[11px] text-slate-500 dark:text-slate-400 shrink-0 font-medium">
                            Est. Arrival:{" "}
                            <span className={`font-bold ${isDelayed ? "text-amber-500" : "text-slate-900 dark:text-white"}`}>
                              {shipment.estimated_delivery}
                            </span>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex sm:flex-col items-center sm:items-end justify-between w-full sm:w-auto gap-2.5 shrink-0 pt-3 sm:pt-0 border-t sm:border-t-0 border-slate-100 dark:border-slate-800">
                    <Link
                      href={`/orders/${order.id}`}
                      className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-[#0070E0] hover:bg-[#005bb5] text-white text-xs font-bold transition-all shadow-xs cursor-pointer"
                    >
                      <span>Track Order</span>
                      <ChevronRight className="w-3.5 h-3.5" />
                    </Link>

                    <Link
                      href={`/?prompt=${encodeURIComponent(`Where is my order ${order.id}?`)}`}
                      className="inline-flex items-center gap-1 text-[11px] text-slate-500 dark:text-slate-400 hover:text-[#0070E0] dark:hover:text-[#38BDF8] font-medium transition-colors"
                    >
                      <MessageSquare className="w-3 h-3" />
                      <span>Ask PayPilot</span>
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}

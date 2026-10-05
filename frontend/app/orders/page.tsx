"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import Navbar from "@/components/Navbar";
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
} from "lucide-react";

interface TimelineEvent {
  title: string;
  description: string;
  timestamp: string;
  completed: boolean;
  current: boolean;
}

interface Shipment {
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

interface Order {
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

export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>("ALL");

  const fetchOrders = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/orders?user_id=guest_user");
      if (res.ok) {
        const data = await res.json();
        setOrders(data);
      }
    } catch (err) {
      console.error("Failed to fetch orders:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  const filteredOrders = orders.filter((o) => {
    if (filter === "ALL") return true;
    return o.status === filter;
  });

  const getStatusBadge = (status: string, lastUpdate?: string) => {
    const isDelayed = lastUpdate && lastUpdate.toLowerCase().includes("delay");

    if (isDelayed) {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
          <AlertTriangle className="w-3 h-3 text-amber-400" />
          Delayed In Transit
        </span>
      );
    }

    switch (status) {
      case "DELIVERED":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="w-3 h-3 text-emerald-400" />
            Delivered
          </span>
        );
      case "IN_TRANSIT":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Truck className="w-3 h-3 text-cyan-400 animate-pulse" />
            In Transit
          </span>
        );
      case "SHIPPED":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
            <Package className="w-3 h-3 text-blue-400" />
            Shipped
          </span>
        );
      case "PROCESSING":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-purple-500/10 text-purple-400 border border-purple-500/20">
            <Clock className="w-3 h-3 text-purple-400" />
            Processing
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-800 text-slate-300">
            {status}
          </span>
        );
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-[#07090e] text-slate-100">
      <Navbar />

      <main className="flex-1 max-w-5xl w-full mx-auto px-4 sm:px-6 py-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800/80 mb-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-cyan-500/20 bg-cyan-500/5 text-cyan-400 text-xs font-medium mb-2">
              <Package className="w-3.5 h-3.5" />
              Verified PayPal Purchases & Logistics
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              My Orders & Shipment Tracking
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              Authoritative order state, real-time shipment scans, and grounded AI resolution.
            </p>
          </div>

          <button
            onClick={fetchOrders}
            className="self-start sm:self-auto flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900/60 hover:bg-slate-800 text-xs font-medium text-slate-300 transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </button>
        </div>

        {/* Filter Chips */}
        <div className="flex items-center gap-2 overflow-x-auto pb-4 mb-4 text-xs">
          {["ALL", "IN_TRANSIT", "PROCESSING", "DELIVERED"].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1.5 rounded-lg font-medium transition-all whitespace-nowrap ${
                filter === f
                  ? "bg-cyan-500 text-black font-semibold shadow-md shadow-cyan-500/20"
                  : "bg-slate-900 border border-slate-800 text-slate-400 hover:text-white"
              }`}
            >
              {f.replace("_", " ")}
            </button>
          ))}
        </div>

        {/* Orders List */}
        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 text-slate-500">
            <RefreshCw className="w-8 h-8 animate-spin text-cyan-400 mb-3" />
            <p className="text-sm">Loading order history...</p>
          </div>
        ) : filteredOrders.length === 0 ? (
          <div className="text-center py-16 px-4 rounded-2xl border border-slate-800/80 bg-slate-900/20">
            <Package className="w-12 h-12 mx-auto text-slate-600 mb-3" />
            <h3 className="text-base font-semibold text-white mb-1">No Orders Found</h3>
            <p className="text-xs text-slate-400 max-w-sm mx-auto mb-4">
              You do not have any orders matching the selected filter.
            </p>
            <Link
              href="/"
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-cyan-500 text-black text-xs font-semibold hover:bg-cyan-400 transition-colors"
            >
              Start Shopping with PayPilot
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {filteredOrders.map((order) => {
              const shipment = order.shipment;
              const isDelayed = shipment?.last_update.toLowerCase().includes("delay");

              return (
                <div
                  key={order.id}
                  className="rounded-2xl border border-slate-800/80 bg-slate-900/40 hover:border-slate-700/80 transition-all p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-5 group"
                >
                  <div className="flex items-start gap-4 flex-1">
                    <div className="w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center shrink-0 text-cyan-400">
                      <Package className="w-6 h-6" />
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex flex-wrap items-center gap-2 mb-1">
                        <span className="text-xs font-mono font-medium text-slate-400 bg-slate-800/80 px-2 py-0.5 rounded">
                          {order.id}
                        </span>
                        {getStatusBadge(order.status, shipment?.last_update)}
                        {order.paypal_order_id && (
                          <span className="text-[10px] font-mono text-cyan-400/80 bg-cyan-950/40 border border-cyan-900/40 px-1.5 py-0.5 rounded flex items-center gap-1">
                            <ShieldCheck className="w-2.5 h-2.5 text-cyan-400" />
                            PayPal Verified
                          </span>
                        )}
                      </div>

                      <h3 className="text-base font-bold text-white group-hover:text-cyan-400 transition-colors truncate">
                        {order.product_name}
                      </h3>

                      <p className="text-xs text-slate-400 mt-0.5">
                        Brand: <span className="text-slate-300 font-medium">{order.brand || "Standard"}</span> &bull; Total:{" "}
                        <span className="text-white font-semibold">
                          ${order.amount.toFixed(2)} {order.currency}
                        </span>
                      </p>

                      {/* Shipment Snippet */}
                      {shipment && (
                        <div className="mt-3 text-xs bg-slate-950/60 border border-slate-800/60 rounded-xl p-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                          <div className="flex items-center gap-2 text-slate-300 truncate">
                            <Truck className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                            <span className="truncate">{shipment.last_update}</span>
                          </div>
                          <div className="text-[11px] text-slate-400 shrink-0">
                            Est. Arrival:{" "}
                            <span className={`font-semibold ${isDelayed ? "text-amber-400" : "text-white"}`}>
                              {shipment.estimated_delivery}
                            </span>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex sm:flex-col items-center sm:items-end justify-between w-full sm:w-auto gap-2 shrink-0 pt-3 sm:pt-0 border-t sm:border-t-0 border-slate-800/60">
                    <Link
                      href={`/orders/${order.id}`}
                      className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 text-xs font-semibold transition-all group-hover:bg-cyan-500 group-hover:text-black"
                    >
                      Track Order
                      <ChevronRight className="w-3.5 h-3.5" />
                    </Link>

                    <Link
                      href={`/?prompt=${encodeURIComponent(`Where is my order ${order.id}?`)}`}
                      className="inline-flex items-center gap-1 text-[11px] text-slate-400 hover:text-cyan-400 transition-colors"
                    >
                      <MessageSquare className="w-3 h-3" />
                      Ask PayPilot
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

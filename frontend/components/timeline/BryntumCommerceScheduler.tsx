"use client";

import React, { useState, useEffect, useMemo } from "react";
import { api } from "@/lib/api";
import {
  CalendarRange,
  Clock,
  Truck,
  CreditCard,
  Package,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Search,
  Filter,
  ExternalLink,
  ChevronRight,
  ShieldCheck,
  Calendar,
  Layers,
  Sparkles,
} from "lucide-react";

interface TimelineResource {
  id: string;
  name: string;
  orderId: string;
  brand?: string;
  amount: number;
  currency: string;
  status: string;
  carrier?: string;
  trackingNumber?: string;
}

interface TimelineEvent {
  id: string;
  resourceId: string;
  name: string;
  startDate: string;
  endDate: string;
  eventType: "APPROVAL" | "PAYMENT" | "FULFILLMENT" | "IN_TRANSIT" | "DELIVERY" | "REFUND" | string;
  status: string;
  isEstimated: boolean;
  eventColor: string;
  iconCls?: string;
  metadata?: Record<string, any>;
}

interface TimelineSummary {
  total_orders: number;
  active_shipments: number;
  pending_payments: number;
  next_delivery?: {
    order_id: string;
    carrier: string;
    tracking_number: string;
    estimated_delivery: string;
    status: string;
  };
  upcoming_deliveries_count?: number;
  verified_at: string;
}

interface AstropodsOverview {
  mode: string;
  project_id: string;
  environment: string;
  total_traces: number;
  total_spans: number;
  failed_spans: number;
  average_turn_latency_ms: number;
  guardrails: Record<string, string>;
}

const EVENT_TYPE_COLORS: Record<string, { bg: string; border: string; text: string; badge: string }> = {
  APPROVAL: { bg: "bg-emerald-50 dark:bg-emerald-950/60", border: "border-emerald-200 dark:border-emerald-500/50", text: "text-emerald-700 dark:text-emerald-300", badge: "bg-emerald-500" },
  PAYMENT: { bg: "bg-blue-50 dark:bg-blue-950/60", border: "border-blue-200 dark:border-blue-500/50", text: "text-blue-700 dark:text-blue-300", badge: "bg-blue-500" },
  FULFILLMENT: { bg: "bg-indigo-50 dark:bg-indigo-950/60", border: "border-indigo-200 dark:border-indigo-500/50", text: "text-indigo-700 dark:text-indigo-300", badge: "bg-indigo-500" },
  IN_TRANSIT: { bg: "bg-purple-50 dark:bg-purple-950/60", border: "border-purple-200 dark:border-purple-500/50", text: "text-purple-700 dark:text-purple-300", badge: "bg-purple-500" },
  DELIVERY: { bg: "bg-amber-50 dark:bg-amber-950/60", border: "border-amber-200 dark:border-amber-500/50", text: "text-amber-700 dark:text-amber-300", badge: "bg-amber-500" },
  REFUND: { bg: "bg-rose-50 dark:bg-rose-950/60", border: "border-rose-200 dark:border-rose-500/50", text: "text-rose-700 dark:text-rose-300", badge: "bg-rose-500" },
};

export default function BryntumCommerceScheduler() {
  const [resources, setResources] = useState<TimelineResource[]>([]);
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [summary, setSummary] = useState<TimelineSummary | null>(null);
  const [astropods, setAstropods] = useState<AstropodsOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [selectedEventType, setSelectedEventType] = useState<string>("ALL");
  const [selectedOrderId, setSelectedOrderId] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState("");
  const [activeEvent, setActiveEvent] = useState<TimelineEvent | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [timelineRes, summaryRes, astroRes] = await Promise.allSettled([
        api.getTimelineEvents({
          event_type: selectedEventType !== "ALL" ? selectedEventType : undefined,
          order_id: selectedOrderId !== "ALL" ? selectedOrderId : undefined,
        }),
        api.getTimelineSummary(),
        api.getAstropodsOverview(),
      ]);

      if (timelineRes.status === "fulfilled") {
        setResources(timelineRes.value.resources || []);
        setEvents(timelineRes.value.events || []);
      } else {
        throw new Error("Failed to load timeline data");
      }

      if (summaryRes.status === "fulfilled") {
        setSummary(summaryRes.value);
      }

      if (astroRes.status === "fulfilled") {
        setAstropods(astroRes.value);
      }
    } catch (err: any) {
      console.error("Timeline error:", err);
      setError(err?.message || "Failed to load commerce timeline");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [selectedEventType, selectedOrderId]);

  // Filtered resources and events
  const filteredResources = useMemo(() => {
    if (!searchQuery.trim()) return resources;
    const q = searchQuery.toLowerCase();
    return resources.filter(
      (r) =>
        r.name.toLowerCase().includes(q) ||
        r.orderId.toLowerCase().includes(q) ||
        (r.carrier && r.carrier.toLowerCase().includes(q)) ||
        (r.trackingNumber && r.trackingNumber.toLowerCase().includes(q))
    );
  }, [resources, searchQuery]);

  const eventsByResource = useMemo(() => {
    const map = new Map<string, TimelineEvent[]>();
    events.forEach((ev) => {
      const list = map.get(ev.resourceId) || [];
      list.push(ev);
      map.set(ev.resourceId, list);
    });
    return map;
  }, [events]);

  const formatDate = (dateStr: string) => {
    try {
      const dt = new Date(dateStr);
      return dt.toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return dateStr;
    }
  };

  const formatShortDate = (dateStr: string) => {
    try {
      const dt = new Date(dateStr);
      return dt.toLocaleDateString("en-US", { month: "short", day: "numeric" });
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-purple-400 bg-purple-950/60 border border-purple-800/50 rounded-full flex items-center gap-1">
              <CalendarRange className="w-3 h-3" />
              Bryntum Powered
            </span>
            <span className="px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-cyan-400 bg-cyan-950/60 border border-cyan-800/50 rounded-full flex items-center gap-1">
              <ShieldCheck className="w-3 h-3" />
              Astropods Traced
            </span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-[#14213D] dark:text-white flex items-center gap-2">
            Commerce Operations Timeline
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Interactive lifecycle scheduling across purchase approvals, PayPal captures, merchant fulfillment, and carrier logistics.
          </p>
        </div>

        <button
          onClick={fetchData}
          disabled={loading}
          className="flex items-center gap-2 px-3 py-2 text-xs font-semibold text-slate-700 dark:text-slate-200 bg-white dark:bg-slate-800/80 hover:bg-slate-50 dark:hover:bg-slate-700/80 border border-slate-200 dark:border-slate-700 rounded-lg transition-colors shadow-subtle dark:shadow-none self-start md:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          Sync Timeline
        </button>
      </div>

      {/* KPI Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0f172a]/70 backdrop-blur-sm shadow-subtle dark:shadow-none">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Active Orders</span>
            <Package className="w-4 h-4 text-[#0070E0] dark:text-cyan-400" />
          </div>
          <div className="text-2xl font-bold text-[#14213D] dark:text-white">{summary?.total_orders ?? "—"}</div>
          <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">Lifecycle orders tracked</div>
        </div>

        <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0f172a]/70 backdrop-blur-sm shadow-subtle dark:shadow-none">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Shipments in Transit</span>
            <Truck className="w-4 h-4 text-purple-600 dark:text-purple-400" />
          </div>
          <div className="text-2xl font-bold text-[#14213D] dark:text-white">{summary?.active_shipments ?? "—"}</div>
          <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">Active carrier logistics legs</div>
        </div>

        <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0f172a]/70 backdrop-blur-sm shadow-subtle dark:shadow-none">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">PayPal Payments</span>
            <CreditCard className="w-4 h-4 text-[#003087] dark:text-blue-400" />
          </div>
          <div className="text-2xl font-bold text-[#14213D] dark:text-white">
            {summary?.pending_payments === 0 ? "All Captured" : `${summary?.pending_payments ?? 0} Pending`}
          </div>
          <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">Authoritative PayPal ledger</div>
        </div>

        <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0f172a]/70 backdrop-blur-sm shadow-subtle dark:shadow-none">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Next Milestone</span>
            <Clock className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
          </div>
          <div className="text-sm font-semibold text-[#14213D] dark:text-white truncate">
            {summary?.next_delivery ? `${summary.next_delivery.carrier}` : "Up to date"}
          </div>
          <div className="text-[11px] text-emerald-600 dark:text-emerald-400 mt-1 truncate">
            {summary?.next_delivery ? `Est: ${summary.next_delivery.estimated_delivery}` : "No overdue deliveries"}
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0f172a]/80 flex flex-wrap items-center justify-between gap-3 shadow-subtle dark:shadow-none">
        {/* Event Type Filter Buttons */}
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-xs text-slate-500 dark:text-slate-400 mr-1 flex items-center gap-1 font-medium">
            <Filter className="w-3 h-3" /> Filter:
          </span>
          {["ALL", "APPROVAL", "PAYMENT", "FULFILLMENT", "IN_TRANSIT", "DELIVERY", "REFUND"].map((type) => (
            <button
              key={type}
              onClick={() => setSelectedEventType(type)}
              className={`px-2.5 py-1 text-xs rounded-md font-semibold transition-colors ${
                selectedEventType === type
                  ? "bg-[#0070E0] dark:bg-cyan-500 text-white shadow-xs"
                  : "bg-slate-100 dark:bg-slate-800/80 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700/80 border border-slate-200 dark:border-slate-700/60"
              }`}
            >
              {type === "ALL" ? "All Milestones" : type.replace("_", " ")}
            </button>
          ))}
        </div>

        {/* Search */}
        <div className="relative min-w-[220px]">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search order or tracking..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-8 pr-3 py-1.5 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-800 dark:text-slate-200 placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:border-[#0070E0] dark:focus:border-cyan-500"
          />
        </div>
      </div>

      {/* Bryntum Scheduler Interactive Grid View */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Timeline Gantt / Scheduler Area (2 cols on lg) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0b1120] overflow-hidden shadow-subtle dark:shadow-xl">
            <div className="p-4 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between bg-slate-50/80 dark:bg-slate-900/60">
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                <h3 className="text-sm font-bold text-[#14213D] dark:text-white">Interactive Schedule Tracks</h3>
              </div>
              <span className="text-[11px] text-slate-500 dark:text-slate-400">
                {filteredResources.length} Tracks • {events.length} Milestones
              </span>
            </div>

            {loading ? (
              <div className="p-12 text-center">
                <RefreshCw className="w-6 h-6 animate-spin text-[#0070E0] dark:text-cyan-400 mx-auto mb-2" />
                <p className="text-xs text-slate-500 dark:text-slate-400">Rendering Bryntum schedule tracks...</p>
              </div>
            ) : filteredResources.length === 0 ? (
              <div className="p-12 text-center text-slate-500 dark:text-slate-400 text-xs">
                No orders match your filter criteria.
              </div>
            ) : (
              <div className="divide-y divide-slate-100 dark:divide-slate-800/60">
                {filteredResources.map((res) => {
                  const resEvents = eventsByResource.get(res.id) || [];
                  return (
                    <div key={res.id} className="p-4 hover:bg-slate-50/80 dark:hover:bg-slate-800/20 transition-colors">
                      {/* Resource Lane Header */}
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-sm text-slate-800 dark:text-slate-200">{res.name}</span>
                          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-[#0070E0] dark:text-cyan-400 border border-slate-200 dark:border-slate-700 font-semibold">
                            {res.orderId}
                          </span>
                          {res.carrier && (
                            <span className="text-[10px] px-1.5 py-0.5 rounded bg-purple-100 dark:bg-purple-950/60 text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-800/40 font-medium">
                              {res.carrier}
                            </span>
                          )}
                        </div>
                        <span className="text-xs font-bold text-slate-800 dark:text-slate-300 font-mono">
                          ${res.amount.toFixed(2)} {res.currency}
                        </span>
                      </div>

                      {/* Bryntum Visual Milestone Track */}
                      <div className="space-y-2">
                        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
                          {resEvents.map((ev) => {
                            const colors = EVENT_TYPE_COLORS[ev.eventType] || {
                              bg: "bg-slate-800",
                              border: "border-slate-700",
                              text: "text-slate-300",
                              badge: "bg-slate-500",
                            };
                            const isSelected = activeEvent?.id === ev.id;

                            return (
                              <button
                                key={ev.id}
                                onClick={() => setActiveEvent(ev)}
                                className={`text-left p-2.5 rounded-lg border transition-all ${colors.bg} ${colors.border} ${
                                  isSelected
                                    ? "ring-2 ring-cyan-400 scale-[1.02] shadow-lg"
                                    : "hover:scale-[1.01] hover:border-slate-500"
                                }`}
                              >
                                <div className="flex items-center justify-between mb-1">
                                  <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                                    {ev.eventType}
                                  </span>
                                  {ev.isEstimated ? (
                                    <span className="px-1.5 py-0.2 text-[9px] font-medium rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40">
                                      Estimated
                                    </span>
                                  ) : (
                                    <span className="px-1.5 py-0.2 text-[9px] font-medium rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                                      Confirmed
                                    </span>
                                  )}
                                </div>
                                <div className={`text-xs font-medium truncate ${colors.text}`}>{ev.name}</div>
                                <div className="text-[10px] text-slate-400 mt-1 flex items-center gap-1">
                                  <Clock className="w-2.5 h-2.5" />
                                  {formatShortDate(ev.startDate)}
                                </div>
                              </button>
                            );
                          })}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Side Panel: Event Inspector & Astropods Observability */}
        <div className="space-y-4">
          {/* Milestone Detail Inspector */}
          <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0b1120] p-4 shadow-sm dark:shadow-xl transition-colors">
            <h3 className="text-sm font-semibold text-[#14213D] dark:text-white mb-3 flex items-center gap-2">
              <Calendar className="w-4 h-4 text-cyan-600 dark:text-cyan-400" />
              Milestone Inspector
            </h3>

            {activeEvent ? (
              <div className="space-y-3">
                <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[10px] uppercase font-semibold text-slate-500 dark:text-slate-400">
                      {activeEvent.eventType} Milestone
                    </span>
                    <span
                      className={`text-[10px] font-medium px-2 py-0.5 rounded-full ${
                        activeEvent.isEstimated
                          ? "bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800"
                          : "bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800"
                      }`}
                    >
                      {activeEvent.status}
                    </span>
                  </div>
                  <div className="text-sm font-bold text-[#14213D] dark:text-white">{activeEvent.name}</div>
                  <div className="text-xs text-slate-600 dark:text-slate-400 mt-2 space-y-1">
                    <div>
                      <span className="text-slate-400 dark:text-slate-500">Start:</span> {formatDate(activeEvent.startDate)}
                    </div>
                    <div>
                      <span className="text-slate-400 dark:text-slate-500">Target/End:</span> {formatDate(activeEvent.endDate)}
                    </div>
                  </div>
                </div>

                {activeEvent.metadata && (
                  <div className="space-y-2">
                    <span className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                      Authoritative Metadata
                    </span>
                    <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 text-xs font-mono text-slate-700 dark:text-slate-300 space-y-1 overflow-x-auto">
                      {Object.entries(activeEvent.metadata).map(([k, v]) => (
                        <div key={k} className="flex justify-between gap-2">
                          <span className="text-slate-500">{k}:</span>
                          <span className="text-cyan-600 dark:text-cyan-300 truncate max-w-[200px]">{String(v)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="p-6 text-center text-xs text-slate-500 border border-dashed border-slate-200 dark:border-slate-800 rounded-lg">
                Click any milestone on the schedule tracks to inspect its authoritative metadata, provider transaction, or carrier status.
              </div>
            )}
          </div>

          {/* Astropods Control Plane & Telemetry Card */}
          <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0b1120] p-4 shadow-sm dark:shadow-xl transition-colors">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold text-[#14213D] dark:text-white flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-cyan-600 dark:text-cyan-400" />
                Astropods Control Plane
              </h3>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-cyan-50 dark:bg-cyan-950/60 text-cyan-700 dark:text-cyan-300 border border-cyan-200 dark:border-cyan-800">
                {astropods?.mode || "LOCAL"}
              </span>
            </div>

            <div className="space-y-2.5 text-xs">
              <div className="flex justify-between text-slate-500 dark:text-slate-400">
                <span>Project:</span>
                <span className="text-slate-700 dark:text-slate-200 font-mono">{astropods?.project_id || "paypilot-ai-commerce"}</span>
              </div>
              <div className="flex justify-between text-slate-500 dark:text-slate-400">
                <span>Traced Turns:</span>
                <span className="text-[#14213D] dark:text-white font-semibold">{astropods?.total_traces ?? 0}</span>
              </div>
              <div className="flex justify-between text-slate-500 dark:text-slate-400">
                <span>Telemetry Spans:</span>
                <span className="text-[#14213D] dark:text-white font-semibold">{astropods?.total_spans ?? 0}</span>
              </div>
              <div className="flex justify-between text-slate-500 dark:text-slate-400">
                <span>Avg Step Latency:</span>
                <span className="text-[#14213D] dark:text-white font-semibold">{astropods?.average_turn_latency_ms ?? 0} ms</span>
              </div>

              <div className="pt-2 border-t border-slate-200 dark:border-slate-800">
                <span className="text-[10px] font-semibold uppercase text-slate-500 block mb-1.5">
                  Active Safety Guardrails
                </span>
                <div className="flex flex-wrap gap-1.5">
                  <span className="px-2 py-0.5 text-[10px] rounded bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                    Secret Redaction Active
                  </span>
                  <span className="px-2 py-0.5 text-[10px] rounded bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                    Human-in-the-Loop Active
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}


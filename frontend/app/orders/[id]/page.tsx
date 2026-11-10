"use client";

import React, { useEffect, useState, useRef } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import Navbar from "@/components/Navbar";
import {
  Package,
  Truck,
  CheckCircle2,
  Clock,
  AlertTriangle,
  ArrowLeft,
  ShieldCheck,
  Send,
  Bot,
  User,
  Sparkles,
  FileText,
  MailCheck,
  Loader2,
} from "lucide-react";
import { API_BASE_URL } from "@/lib/api";

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

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

export default function OrderDetailPage() {
  const params = useParams();
  const orderId = params?.id as string;

  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Post-purchase chat states
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [sessionId] = useState(`order-sess-${orderId || "demo"}`);
  const [pendingDraft, setPendingDraft] = useState<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const fetchOrderDetail = async () => {
    if (!orderId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/api/orders/${orderId}?user_id=guest_user`);
      if (!res.ok) {
        throw new Error(`Order not found or access denied (${res.status})`);
      }
      const data = await res.json();
      setOrder(data);
    } catch (err: any) {
      setError(err.message || "Failed to load order details");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrderDetail();
  }, [orderId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, pendingDraft]);

  const handleSendMessage = async (textToSend?: string) => {
    const text = textToSend || inputMessage;
    if (!text.trim() || chatLoading) return;

    const userMsg: ChatMessage = {
      role: "user",
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInputMessage("");
    setChatLoading(true);

    try {
      const res = await fetch(`${API_BASE_URL}/api/agent/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          session_id: sessionId,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        const botMsg: ChatMessage = {
          role: "assistant",
          content: data.message,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        };
        setMessages((prev) => [...prev, botMsg]);
        if (data.draft) {
          setPendingDraft(data.draft);
        } else {
          setPendingDraft(null);
        }
      }
    } catch (err) {
      console.warn("Chat API notice:", err);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Checking telemetry for Order #${orderId}... Note: Backend is currently in offline mode.`,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  const handleApproveDraft = async () => {
    setChatLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/agent/${sessionId}/approve`, {
        method: "POST",
      });
      if (res.ok) {
        const data = await res.json();
        setPendingDraft(null);
        const botMsg: ChatMessage = {
          role: "assistant",
          content: data.message,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        };
        setMessages((prev) => [...prev, botMsg]);
      }
    } catch (err) {
      console.error("Draft approval error:", err);
    } finally {
      setChatLoading(false);
    }
  };

  const handleDenyDraft = async () => {
    setChatLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/agent/${sessionId}/deny`, {
        method: "POST",
      });
      if (res.ok) {
        const data = await res.json();
        setPendingDraft(null);
        const botMsg: ChatMessage = {
          role: "assistant",
          content: data.message,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        };
        setMessages((prev) => [...prev, botMsg]);
      }
    } catch (err) {
      console.error("Draft denial error:", err);
    } finally {
      setChatLoading(false);
    }
  };

  const shipment = order?.shipment;
  const isDelayed = shipment?.last_update.toLowerCase().includes("delay");

  return (
    <div className="flex flex-col min-h-screen bg-[#F5F8FC]/50 dark:bg-[#090D16] text-[#14213D] dark:text-slate-100 text-left transition-colors duration-200">
      <Navbar />

      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 py-6">
        {/* Back Link */}
        <Link
          href="/orders"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 dark:text-slate-400 hover:text-[#0070E0] dark:hover:text-[#38BDF8] transition-colors mb-4"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to all orders</span>
        </Link>

        {loading ? (
          <div className="py-20 text-center text-slate-500 dark:text-slate-400">
            <Loader2 className="w-8 h-8 animate-spin mx-auto text-[#0070E0] dark:text-[#38BDF8] mb-2" />
            <p className="text-sm font-medium">Retrieving order and shipment data...</p>
          </div>
        ) : error || !order ? (
          <div className="p-8 rounded-3xl border border-red-200 dark:border-red-900/40 bg-red-50 dark:bg-red-950/20 text-center">
            <AlertTriangle className="w-10 h-10 text-red-500 mx-auto mb-2" />
            <h3 className="text-base font-bold text-slate-900 dark:text-white mb-1">Order Access Notice</h3>
            <p className="text-xs text-slate-600 dark:text-slate-400 max-w-md mx-auto mb-4">{error}</p>
            <Link href="/orders" className="text-xs font-bold text-[#0070E0] dark:text-[#38BDF8] hover:underline">
              Return to Orders List
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left Column: Order & Shipment Details (7 cols) */}
            <div className="lg:col-span-7 flex flex-col gap-6">
              {/* Order Header Card */}
              <div className="rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0E1422] p-6 shadow-subtle">
                <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-slate-100 dark:border-slate-800">
                  <div>
                    <span className="text-xs font-mono font-bold text-[#0070E0] dark:text-[#38BDF8] bg-[#EAF3FF] dark:bg-[#0070E0]/20 border border-[#0070E0]/20 dark:border-[#0070E0]/40 px-2.5 py-0.5 rounded-md">
                      {order.id}
                    </span>
                    <h1 className="text-xl sm:text-2xl font-black text-[#14213D] dark:text-white mt-1.5">
                      {order.product_name}
                    </h1>
                  </div>

                  <div className="text-right">
                    <div className="text-xl font-black text-[#003087] dark:text-[#38BDF8] font-mono">
                      ${order.amount.toFixed(2)} {order.currency}
                    </div>
                    <div className="text-xs text-slate-500 dark:text-slate-400 font-medium">Qty: {order.quantity}</div>
                  </div>
                </div>

                {/* Metadata Grid */}
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mt-4 text-xs">
                  <div className="p-3 rounded-2xl bg-[#F5F8FC] dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700/60">
                    <span className="text-slate-500 dark:text-slate-400 text-[11px] font-medium">Payment Status</span>
                    <div className="font-bold text-emerald-700 dark:text-emerald-400 flex items-center gap-1 mt-0.5">
                      <ShieldCheck className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
                      Completed
                    </div>
                  </div>

                  <div className="p-3 rounded-2xl bg-[#F5F8FC] dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700/60">
                    <span className="text-slate-500 dark:text-slate-400 text-[11px] font-medium">PayPal Order</span>
                    <div className="font-mono text-slate-800 dark:text-slate-200 font-semibold truncate mt-0.5" title={order.paypal_order_id || "N/A"}>
                      {order.paypal_order_id || "MOCK-SANDBOX"}
                    </div>
                  </div>

                  <div className="p-3 rounded-2xl bg-[#F5F8FC] dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700/60">
                    <span className="text-slate-500 dark:text-slate-400 text-[11px] font-medium">Carrier</span>
                    <div className="font-bold text-slate-800 dark:text-slate-200 mt-0.5">
                      {shipment?.carrier || "FastShip Logistics"}
                    </div>
                  </div>
                </div>

                {/* Delay Notice Banner if applicable */}
                {isDelayed && (
                  <div className="mt-4 p-3.5 rounded-2xl border border-amber-200 bg-amber-50 flex items-start gap-3">
                    <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
                    <div className="text-xs">
                      <span className="font-bold text-amber-800">Delivery Delay Reported: </span>
                      <span className="text-slate-700">{shipment?.last_update}</span>
                      <div className="mt-1 text-[11px] text-amber-700 font-medium">
                        Ask the PayPilot Assistant on the right to draft a merchant inquiry.
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Shipment Milestone Progress & Timeline */}
              {shipment && (
                <div className="rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0E1422] p-6 shadow-subtle">
                  <div className="flex items-center justify-between mb-5">
                    <h2 className="text-xs font-bold text-[#14213D] dark:text-white uppercase tracking-wider flex items-center gap-2">
                      <Truck className="w-4 h-4 text-[#0070E0] dark:text-[#38BDF8]" />
                      Shipment Journey &amp; Milestones
                    </h2>
                    <span className="text-xs font-mono font-medium text-slate-500 dark:text-slate-400">
                      Tracking: {shipment.tracking_number}
                    </span>
                  </div>

                  {/* Visual Stepper */}
                  <div className="relative pl-6 space-y-6 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200 dark:before:bg-slate-700">
                    {(shipment.timeline.length > 0
                      ? shipment.timeline
                      : [
                          { title: "Payment Completed", description: "PayPal Sandbox transaction confirmed", timestamp: "Completed", completed: true, current: false },
                          { title: "In Transit", description: shipment.last_update, timestamp: "Current", completed: true, current: true },
                          { title: "Estimated Delivery", description: `Expected arrival: ${shipment.estimated_delivery}`, timestamp: shipment.estimated_delivery, completed: false, current: false },
                        ]
                    ).map((milestone, idx) => (
                      <div key={idx} className="relative flex flex-col items-start gap-1">
                        <div
                          className={`absolute -left-6 top-1 w-3.5 h-3.5 rounded-full border-2 ${
                            milestone.current
                              ? "bg-[#0070E0] border-white ring-4 ring-[#0070E0]/20"
                              : milestone.completed
                              ? "bg-emerald-500 border-white ring-2 ring-emerald-200 dark:ring-emerald-900/50"
                              : "bg-white dark:bg-slate-800 border-slate-300 dark:border-slate-600"
                          }`}
                        />
                        <div className="flex items-baseline justify-between w-full">
                          <span
                            className={`text-xs font-bold ${
                              milestone.current
                                ? "text-[#0070E0] dark:text-[#38BDF8]"
                                : milestone.completed
                                ? "text-slate-800 dark:text-slate-200"
                                : "text-slate-400 dark:text-slate-500"
                            }`}
                          >
                            {milestone.title}
                          </span>
                          <span className="text-[11px] font-mono text-slate-400 dark:text-slate-500">
                            {milestone.timestamp}
                          </span>
                        </div>
                        <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">{milestone.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Right Column: Embedded Post-Purchase Agent Chat (5 cols) */}
            <div className="lg:col-span-5 flex flex-col rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0E1422] shadow-card overflow-hidden min-h-[550px] max-h-[700px]">
              {/* Chat Header */}
              <div className="p-4 border-b border-slate-100 dark:border-slate-800 bg-[#F5F8FC] dark:bg-slate-800/40 flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-full bg-[#0070E0] flex items-center justify-center text-white font-extrabold text-xs">
                    <span className="italic">P</span>
                  </div>
                  <div>
                    <h3 className="text-xs font-bold text-[#14213D] dark:text-white tracking-tight">
                      Ask PayPilot About This Order
                    </h3>
                    <p className="text-[10px] text-slate-500 dark:text-slate-400">Grounded in authoritative order telemetry</p>
                  </div>
                </div>
                <span className="flex items-center gap-1.5 text-[11px] text-emerald-700 dark:text-emerald-400 font-semibold bg-emerald-50 dark:bg-emerald-950/40 px-2.5 py-0.5 rounded-full border border-emerald-200 dark:border-emerald-800/40">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                  Online
                </span>
              </div>

              {/* Chat Message Stream */}
              <div className="flex-1 overflow-y-auto p-4 space-y-3 text-xs bg-white dark:bg-[#090D16]">
                {messages.length === 0 ? (
                  <div className="text-center py-8 px-4 text-slate-500">
                    <Sparkles className="w-7 h-7 mx-auto text-[#0070E0] mb-2" />
                    <p className="font-bold text-[#14213D] mb-1">Need updates on this order?</p>
                    <p className="text-[11px] text-slate-500 max-w-xs mx-auto mb-4 leading-relaxed">
                      PayPilot can verify payment status, check shipment milestones, or prepare merchant support requests.
                    </p>

                    {/* Quick Action Chips */}
                    <div className="flex flex-col gap-1.5 text-left">
                      {[
                        "Where is my order?",
                        "When should it arrive?",
                        "Why hasn't it arrived yet?",
                        "Did my payment go through?",
                      ].map((prompt) => (
                        <button
                          key={prompt}
                          onClick={() => handleSendMessage(prompt)}
                          className="px-3 py-2 rounded-xl bg-[#F5F8FC] border border-slate-200 hover:border-[#0070E0]/30 hover:bg-[#EAF3FF] text-slate-700 hover:text-[#0070E0] text-xs font-medium transition-colors text-left cursor-pointer"
                        >
                          &ldquo;{prompt}&rdquo;
                        </button>
                      ))}
                    </div>
                  </div>
                ) : (
                  messages.map((m, idx) => (
                    <div
                      key={idx}
                      className={`flex gap-2.5 ${m.role === "user" ? "justify-end" : "justify-start"}`}
                    >
                      {m.role === "assistant" && (
                        <div className="w-6 h-6 rounded-full bg-[#0070E0] flex items-center justify-center text-white text-[10px] font-extrabold shrink-0 mt-0.5">
                          <span className="italic">P</span>
                        </div>
                      )}
                      <div
                        className={`max-w-[85%] rounded-2xl px-3.5 py-2.5 whitespace-pre-line leading-relaxed text-xs sm:text-sm ${
                          m.role === "user"
                            ? "bg-[#0070E0] text-white font-medium rounded-tr-none shadow-xs"
                            : "bg-[#F5F8FC] border border-slate-200/80 text-slate-800 rounded-tl-none"
                        }`}
                      >
                        {m.content}
                      </div>
                      {m.role === "user" && (
                        <div className="w-6 h-6 rounded-full bg-slate-200 flex items-center justify-center text-slate-600 shrink-0 mt-0.5">
                          <User className="w-3.5 h-3.5" />
                        </div>
                      )}
                    </div>
                  ))
                )}

                {/* Pending Support Draft Card with Approval Action */}
                {pendingDraft && (
                  <div className="p-3.5 rounded-2xl border-2 border-[#0070E0]/40 bg-white text-xs space-y-2.5 shadow-card">
                    <div className="flex items-center gap-1.5 text-[#0070E0] font-bold">
                      <FileText className="w-4 h-4" />
                      Pending Support Inquiry Draft
                    </div>
                    <div className="bg-[#F5F8FC] p-3 rounded-xl border border-slate-200 space-y-1">
                      <div>
                        <span className="text-slate-500 text-[10px] font-bold">Subject:</span>{" "}
                        <span className="text-slate-900 font-semibold">{pendingDraft.subject}</span>
                      </div>
                      <div>
                        <span className="text-slate-500 text-[10px] font-bold">To:</span>{" "}
                        <span className="text-slate-700">{pendingDraft.recipient}</span>
                      </div>
                      <div className="text-[11px] text-slate-700 whitespace-pre-line border-t border-slate-200 pt-2 mt-1 font-mono">
                        {pendingDraft.message}
                      </div>
                    </div>
                    <div className="flex items-center justify-end gap-2 pt-1">
                      <button
                        onClick={handleDenyDraft}
                        disabled={chatLoading}
                        className="px-3.5 py-1.5 rounded-xl border border-slate-200 bg-white text-slate-600 hover:text-slate-900 hover:bg-slate-50 text-xs font-semibold cursor-pointer"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={handleApproveDraft}
                        disabled={chatLoading}
                        className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-[#0070E0] hover:bg-[#005bb5] text-white text-xs font-bold transition-all shadow-sm cursor-pointer"
                      >
                        <MailCheck className="w-3.5 h-3.5" />
                        Approve &amp; Send
                      </button>
                    </div>
                  </div>
                )}

                {chatLoading && (
                  <div className="flex items-center gap-2 text-slate-500 text-xs pl-2">
                    <Loader2 className="w-3.5 h-3.5 text-[#0070E0] animate-spin" />
                    <span>PayPilot is checking order telemetry...</span>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Chat Input */}
              <div className="p-3 border-t border-slate-100 dark:border-slate-800 bg-white dark:bg-[#0E1422]">
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    handleSendMessage();
                  }}
                  className="flex items-center gap-2"
                >
                  <input
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    placeholder="Ask about this order (e.g. 'Why is it delayed?')..."
                    className="flex-1 bg-[#F5F8FC] dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-2xl px-3.5 py-2.5 text-xs text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:border-[#0070E0] dark:focus:border-[#38BDF8] focus:bg-white dark:focus:bg-slate-800 focus:ring-2 focus:ring-[#0070E0]/10 transition-all"
                  />
                  <button
                    type="submit"
                    disabled={!inputMessage.trim() || chatLoading}
                    className="p-2.5 rounded-2xl bg-[#0070E0] text-white hover:bg-[#005bb5] disabled:opacity-40 transition-colors cursor-pointer shadow-sm"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </form>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

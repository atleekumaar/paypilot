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
      const res = await fetch(`http://localhost:8000/api/orders/${orderId}?user_id=guest_user`);
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
      const res = await fetch("http://localhost:8000/api/agent/chat", {
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
      console.error("Chat error:", err);
    } finally {
      setChatLoading(false);
    }
  };

  const handleApproveDraft = async () => {
    setChatLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/agent/${sessionId}/approve`, {
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
      const res = await fetch(`http://localhost:8000/api/agent/${sessionId}/deny`, {
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
    <div className="flex flex-col min-h-screen bg-[#07090e] text-slate-100">
      <Navbar />

      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 py-6">
        {/* Back Link */}
        <Link
          href="/orders"
          className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-cyan-400 transition-colors mb-4"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          Back to all orders
        </Link>

        {loading ? (
          <div className="py-20 text-center text-slate-500">
            <Clock className="w-8 h-8 animate-spin mx-auto text-cyan-400 mb-2" />
            <p className="text-sm">Retrieving order and shipment data...</p>
          </div>
        ) : error || !order ? (
          <div className="p-8 rounded-2xl border border-red-500/20 bg-red-950/20 text-center">
            <AlertTriangle className="w-10 h-10 text-red-400 mx-auto mb-2" />
            <h3 className="text-base font-bold text-white mb-1">Order Access Error</h3>
            <p className="text-xs text-slate-300 max-w-md mx-auto mb-4">{error}</p>
            <Link href="/orders" className="text-xs font-semibold text-cyan-400 underline">
              Return to Orders
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left Column: Order & Shipment Details (7 cols) */}
            <div className="lg:col-span-7 flex flex-col gap-6">
              {/* Order Header Card */}
              <div className="rounded-2xl border border-slate-800/80 bg-slate-900/40 p-6">
                <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-slate-800/80">
                  <div>
                    <span className="text-xs font-mono font-semibold text-cyan-400 bg-cyan-950/50 border border-cyan-800/50 px-2 py-0.5 rounded">
                      {order.id}
                    </span>
                    <h1 className="text-xl sm:text-2xl font-bold text-white mt-1.5">
                      {order.product_name}
                    </h1>
                  </div>

                  <div className="text-right">
                    <div className="text-lg font-bold text-white">
                      ${order.amount.toFixed(2)} {order.currency}
                    </div>
                    <div className="text-[11px] text-slate-400">Qty: {order.quantity}</div>
                  </div>
                </div>

                {/* Metadata Grid */}
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mt-4 text-xs">
                  <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/60">
                    <span className="text-slate-400 text-[11px]">Payment</span>
                    <div className="font-semibold text-emerald-400 flex items-center gap-1 mt-0.5">
                      <ShieldCheck className="w-3.5 h-3.5" />
                      Completed
                    </div>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/60">
                    <span className="text-slate-400 text-[11px]">PayPal Order</span>
                    <div className="font-mono text-slate-200 truncate mt-0.5" title={order.paypal_order_id || "N/A"}>
                      {order.paypal_order_id || "MOCK-SANDBOX"}
                    </div>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/60">
                    <span className="text-slate-400 text-[11px]">Carrier</span>
                    <div className="font-medium text-slate-200 mt-0.5">
                      {shipment?.carrier || "FastShip Logistics"}
                    </div>
                  </div>
                </div>

                {/* Delay Notice Banner if applicable */}
                {isDelayed && (
                  <div className="mt-4 p-3.5 rounded-xl border border-amber-500/30 bg-amber-500/10 flex items-start gap-3">
                    <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                    <div className="text-xs">
                      <span className="font-bold text-amber-400">Delivery Delay Reported: </span>
                      <span className="text-slate-200">{shipment?.last_update}</span>
                      <div className="mt-1 text-[11px] text-amber-400/90">
                        Ask the agent below to draft a support inquiry to the merchant.
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Shipment Milestone Progress & Timeline */}
              {shipment && (
                <div className="rounded-2xl border border-slate-800/80 bg-slate-900/40 p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                      <Truck className="w-4 h-4 text-cyan-400" />
                      Shipment Journey & Milestones
                    </h2>
                    <span className="text-xs font-mono text-slate-400">
                      Tracking: {shipment.tracking_number}
                    </span>
                  </div>

                  {/* Visual Stepper */}
                  <div className="relative pl-6 space-y-6 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
                    {(shipment.timeline.length > 0
                      ? shipment.timeline
                      : [
                          { title: "Payment Completed", description: "PayPal transaction confirmed", timestamp: "Completed", completed: true, current: false },
                          { title: "In Transit", description: shipment.last_update, timestamp: "Current", completed: true, current: true },
                          { title: "Estimated Delivery", description: `Expected arrival: ${shipment.estimated_delivery}`, timestamp: shipment.estimated_delivery, completed: false, current: false },
                        ]
                    ).map((milestone, idx) => (
                      <div key={idx} className="relative flex flex-col items-start gap-1">
                        <div
                          className={`absolute -left-6 top-1 w-3.5 h-3.5 rounded-full border-2 ${
                            milestone.current
                              ? "bg-cyan-400 border-cyan-300 ring-4 ring-cyan-500/20"
                              : milestone.completed
                              ? "bg-emerald-500 border-emerald-400"
                              : "bg-slate-900 border-slate-700"
                          }`}
                        />
                        <div className="flex items-baseline justify-between w-full">
                          <span
                            className={`text-xs font-semibold ${
                              milestone.current
                                ? "text-cyan-400"
                                : milestone.completed
                                ? "text-slate-200"
                                : "text-slate-500"
                            }`}
                          >
                            {milestone.title}
                          </span>
                          <span className="text-[11px] font-mono text-slate-500">
                            {milestone.timestamp}
                          </span>
                        </div>
                        <p className="text-xs text-slate-400">{milestone.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Right Column: Embedded Post-Purchase Agent Chat (5 cols) */}
            <div className="lg:col-span-5 flex flex-col rounded-2xl border border-slate-800/80 bg-slate-900/60 overflow-hidden min-h-[550px] max-h-[700px]">
              {/* Chat Header */}
              <div className="p-4 border-b border-slate-800/80 bg-slate-950/60 flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="w-7 h-7 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
                    <Bot className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="text-xs font-bold text-white tracking-wide">
                      Ask PayPilot About This Order
                    </h3>
                    <p className="text-[10px] text-slate-400">Grounded in authoritative order telemetry</p>
                  </div>
                </div>
                <span className="flex items-center gap-1 text-[10px] text-emerald-400 font-medium">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                  Online
                </span>
              </div>

              {/* Chat Message Stream */}
              <div className="flex-1 overflow-y-auto p-4 space-y-3 text-xs">
                {messages.length === 0 ? (
                  <div className="text-center py-8 px-4 text-slate-400">
                    <Sparkles className="w-8 h-8 mx-auto text-cyan-400 mb-2" />
                    <p className="font-semibold text-white mb-1">Need updates on this order?</p>
                    <p className="text-[11px] text-slate-400 max-w-xs mx-auto mb-4">
                      PayPilot can verify payment status, track shipment milestones, or prepare merchant support requests.
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
                          className="px-3 py-2 rounded-xl bg-slate-950/80 border border-slate-800 hover:border-cyan-500/30 text-slate-300 hover:text-cyan-400 text-xs transition-colors text-left"
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
                        <div className="w-6 h-6 rounded-md bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shrink-0 mt-0.5">
                          <Bot className="w-3.5 h-3.5" />
                        </div>
                      )}
                      <div
                        className={`max-w-[85%] rounded-2xl px-3.5 py-2.5 whitespace-pre-line leading-relaxed ${
                          m.role === "user"
                            ? "bg-cyan-500 text-black font-medium"
                            : "bg-slate-950/90 border border-slate-800/80 text-slate-200"
                        }`}
                      >
                        {m.content}
                      </div>
                      {m.role === "user" && (
                        <div className="w-6 h-6 rounded-md bg-slate-800 flex items-center justify-center text-slate-300 shrink-0 mt-0.5">
                          <User className="w-3.5 h-3.5" />
                        </div>
                      )}
                    </div>
                  ))
                )}

                {/* Pending Support Draft Card with Approval Action */}
                {pendingDraft && (
                  <div className="p-3.5 rounded-2xl border border-cyan-500/40 bg-slate-950 text-xs space-y-2.5 shadow-lg shadow-cyan-500/5">
                    <div className="flex items-center gap-1.5 text-cyan-400 font-bold">
                      <FileText className="w-4 h-4" />
                      Pending Support Inquiry Draft
                    </div>
                    <div className="bg-slate-900/90 p-2.5 rounded-xl border border-slate-800 space-y-1">
                      <div>
                        <span className="text-slate-400 text-[10px]">Subject:</span>{" "}
                        <span className="text-white font-medium">{pendingDraft.subject}</span>
                      </div>
                      <div>
                        <span className="text-slate-400 text-[10px]">To:</span>{" "}
                        <span className="text-slate-300">{pendingDraft.recipient}</span>
                      </div>
                      <div className="text-[11px] text-slate-300 whitespace-pre-line border-t border-slate-800/80 pt-1.5 mt-1 font-mono">
                        {pendingDraft.message}
                      </div>
                    </div>
                    <div className="flex items-center justify-end gap-2 pt-1">
                      <button
                        onClick={handleDenyDraft}
                        disabled={chatLoading}
                        className="px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900 text-slate-400 hover:text-white text-xs font-semibold"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={handleApproveDraft}
                        disabled={chatLoading}
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-black text-xs font-bold transition-all shadow-md shadow-cyan-500/20"
                      >
                        <MailCheck className="w-3.5 h-3.5" />
                        Approve & Send
                      </button>
                    </div>
                  </div>
                )}

                {chatLoading && (
                  <div className="flex items-center gap-2 text-slate-400 text-xs pl-2">
                    <Bot className="w-3.5 h-3.5 text-cyan-400 animate-spin" />
                    <span>PayPilot is checking order telemetry...</span>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Chat Input */}
              <div className="p-3 border-t border-slate-800/80 bg-slate-950/60">
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
                    className="flex-1 bg-slate-900/90 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/60"
                  />
                  <button
                    type="submit"
                    disabled={!inputMessage.trim() || chatLoading}
                    className="p-2 rounded-xl bg-cyan-500 text-black hover:bg-cyan-400 disabled:opacity-40 transition-colors"
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

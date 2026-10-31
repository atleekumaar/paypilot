"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  Send,
  Bot,
  User,
  Sparkles,
  Loader2,
  CheckCircle2,
  RotateCcw,
  Laptop,
  ChevronRight,
  ShieldCheck,
} from "lucide-react";
import AgentActivityPanel, { AgentActionItem } from "@/components/AgentActivityPanel";
import PurchaseApprovalCard from "@/components/PurchaseApprovalCard";
import { api } from "@/lib/api";

interface ChatMessage {
  id: string;
  sender: "user" | "agent";
  text: string;
  timestamp: string;
  candidateProducts?: any[];
  purchasePlan?: any;
  paypalOrderId?: string;
  paymentReceipt?: any;
}

const DEMO_PROMPTS = [
  "I want a laptop for AI/ML under ₹90,000.",
  "Find me the best laptop for AI development under $1200.",
  "Why do you recommend this laptop?",
  "Buy it.",
  "Which one has the best battery life?",
];

const INITIAL_DEMO_PRODUCTS = [
  {
    id: "prod-1",
    name: "ASUS TUF A15 (Ryzen 7, RTX 4050)",
    price: 84990,
    currency: "INR",
    priceDisplay: "₹84,990",
    badge: "Best for AI/ML",
  },
  {
    id: "prod-2",
    name: "Lenovo LOQ (i7, RTX 4050)",
    price: 87990,
    currency: "INR",
    priceDisplay: "₹87,990",
    badge: "High performance",
  },
  {
    id: "prod-3",
    name: "HP Victus (Ryzen 7, RTX 3050)",
    price: 79990,
    currency: "INR",
    priceDisplay: "₹79,990",
    badge: "Value pick",
  },
];

export default function AgentCommerceChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "msg-sample-user",
      sender: "user",
      text: "I want a laptop for AI/ML under ₹90,000.",
      timestamp: "10:14 AM",
    },
    {
      id: "msg-welcome-preview",
      sender: "agent",
      text: "Here are some great options for AI/ML under ₹90,000:",
      timestamp: "10:14 AM",
      candidateProducts: INITIAL_DEMO_PRODUCTS,
    },
  ]);

  const [inputText, setInputText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>(
    () => `sess-${Math.random().toString(36).substring(2, 9)}`
  );
  const [agentActions, setAgentActions] = useState<AgentActionItem[]>([]);
  const [agentStatus, setAgentStatus] = useState<string>("IDLE");
  const [activePlan, setActivePlan] = useState<any>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, agentActions, activePlan]);

  const resetChat = () => {
    setSessionId(`sess-${Math.random().toString(36).substring(2, 9)}`);
    setAgentActions([]);
    setAgentStatus("IDLE");
    setActivePlan(null);
    setMessages([
      {
        id: "msg-welcome-clean",
        sender: "agent",
        text: "Hello! I am PayPilot, your autonomous AI commerce assistant. Describe what you're looking for (e.g., 'I want a laptop for AI/ML under ₹90,000') and I will discover, compare, and prepare verified purchases with PayPal Sandbox.",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      },
    ]);
  };

  const handleSendMessage = async (textToSend?: string) => {
    const text = (textToSend !== undefined ? textToSend : inputText).trim();
    if (!text || isLoading) return;

    setInputText("");
    const userMsgId = `user-${Date.now()}`;
    setMessages((prev) => [
      ...prev,
      {
        id: userMsgId,
        sender: "user",
        text,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      },
    ]);

    setIsLoading(true);

    try {
      const data: any = await api.post("/api/agent/chat", {
        message: text,
        session_id: sessionId,
      });

      setAgentStatus(data.status);
      if (data.actions) {
        setAgentActions(data.actions);
      }

      if (data.purchase_plan) {
        setActivePlan(data.purchase_plan);
      } else if (data.status !== "WAITING_FOR_APPROVAL") {
        setActivePlan(null);
      }

      setMessages((prev) => [
        ...prev,
        {
          id: `agent-${Date.now()}`,
          sender: "agent",
          text: data.message,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          candidateProducts: data.candidate_products,
          purchasePlan: data.purchase_plan,
        },
      ]);
    } catch (err: any) {
      console.warn("Agent API offline or unreachable:", err);
      // Graceful fallback response
      setMessages((prev) => [
        ...prev,
        {
          id: `agent-${Date.now()}`,
          sender: "agent",
          text: `I received your request: "${text}".\n\n(Backend Notice: Ensure the PayPilot FastAPI service is running at http://127.0.0.1:8000 to execute live database queries, policies, and PayPal Sandbox integrations.)`,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleApprovePurchase = async () => {
    setIsLoading(true);
    try {
      // 1. Send approval to agent
      const approveData: any = await api.post(`/api/agent/${sessionId}/approve`);

      setAgentStatus(approveData.status);
      if (approveData.actions) setAgentActions(approveData.actions);

      // 2. Automatically execute PayPal capture for verified Sandbox purchase
      const paymentData: any = await api.post("/api/payments/paypal/capture", {
        purchase_plan_id: approveData.purchase_plan_id,
        paypal_order_id: approveData.paypal_order_id,
      });
      setActivePlan(null);

      setMessages((prev) => [
        ...prev,
        {
          id: `agent-success-${Date.now()}`,
          sender: "agent",
          text: `Payment successfully captured! Verified by PayPal Sandbox with Order ID ${paymentData.provider_order_id} (Capture: ${paymentData.capture_id}).`,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          paymentReceipt: paymentData,
        },
      ]);
    } catch (err: any) {
      console.error("Approval error:", err);
      setMessages((prev) => [
        ...prev,
        {
          id: `agent-err-${Date.now()}`,
          sender: "agent",
          text: `Checkout failed: ${err.message || "Failed to communicate with payment processor."}`,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDenyPurchase = async () => {
    setIsLoading(true);
    try {
      const data: any = await api.post(`/api/agent/${sessionId}/deny`);
      setActivePlan(null);
      setAgentStatus("IDLE");
      if (data.actions) setAgentActions(data.actions);

      setMessages((prev) => [
        ...prev,
        {
          id: `agent-denied-${Date.now()}`,
          sender: "agent",
          text: data.message || "Purchase cancelled. Let me know if you would like other options.",
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    } catch (err: any) {
      console.error("Denial error:", err);
      setActivePlan(null);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      id="assistant"
      className="w-full bg-white border border-slate-200/90 rounded-3xl shadow-card flex flex-col h-[620px] max-h-[90vh] overflow-hidden transition-all text-left"
    >
      {/* Header */}
      <div className="px-5 py-4 bg-white border-b border-slate-100 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-[#0070E0] flex items-center justify-center text-white font-extrabold text-sm shadow-sm">
            <span className="italic">P</span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-[#14213D]">
                PayPilot Assistant
              </h3>
            </div>
            <div className="flex items-center gap-1.5 text-xs text-slate-500">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              <span>Online</span>
            </div>
          </div>
        </div>

        <button
          onClick={resetChat}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold transition-colors cursor-pointer"
        >
          <RotateCcw className="w-3.5 h-3.5 text-slate-500" />
          <span>New Chat</span>
        </button>
      </div>

      {/* Messages Stream */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-5 space-y-4 bg-white">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex flex-col ${
              msg.sender === "user" ? "items-end" : "items-start"
            }`}
          >
            {msg.sender === "user" ? (
              <div className="max-w-[85%] sm:max-w-md p-3.5 sm:p-4 rounded-2xl bg-[#0070E0] text-white text-xs sm:text-sm font-medium leading-relaxed rounded-tr-none shadow-sm">
                {msg.text}
              </div>
            ) : (
              <div className="flex items-start gap-2.5 max-w-full sm:max-w-[90%]">
                <div className="w-7 h-7 rounded-full bg-[#0070E0] flex items-center justify-center text-white font-bold text-xs shrink-0 mt-0.5 shadow-xs">
                  <span className="italic">P</span>
                </div>
                <div className="flex-1 space-y-3">
                  <div className="text-xs sm:text-sm text-[#14213D] leading-relaxed font-normal whitespace-pre-line">
                    {msg.text}
                  </div>

                  {/* Candidate Product Cards */}
                  {msg.candidateProducts && msg.candidateProducts.length > 0 && (
                    <div className="rounded-2xl border border-slate-200/90 overflow-hidden divide-y divide-slate-100 bg-[#F5F8FC]/50 max-w-md shadow-subtle">
                      {msg.candidateProducts.map((p: any, idx: number) => {
                        const name = p.name || p.product_name;
                        const price = p.priceDisplay || (p.price ? `$${p.price}` : "");
                        const badge =
                          p.badge ||
                          (idx === 0
                            ? "Best for AI/ML"
                            : idx === 1
                            ? "High performance"
                            : "Value pick");

                        return (
                          <div
                            key={p.id || idx}
                            onClick={() => handleSendMessage(`Tell me more about ${name}`)}
                            className="p-3 sm:p-3.5 flex items-center justify-between gap-3 hover:bg-white transition-colors cursor-pointer group"
                          >
                            <div className="flex items-center gap-3 min-w-0">
                              <div className="w-10 h-10 rounded-xl bg-white border border-slate-200 flex items-center justify-center text-slate-500 shrink-0 group-hover:border-[#0070E0] transition-colors">
                                <Laptop className="w-5 h-5 text-slate-600 group-hover:text-[#0070E0]" />
                              </div>
                              <div className="min-w-0">
                                <div className="text-xs sm:text-sm font-bold text-[#14213D] truncate group-hover:text-[#0070E0] transition-colors">
                                  {name}
                                </div>
                                <div className="flex items-center gap-2 mt-0.5">
                                  <span className="text-xs font-extrabold text-[#003087]">
                                    {price}
                                  </span>
                                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200/60">
                                    {badge}
                                  </span>
                                </div>
                              </div>
                            </div>
                            <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-[#0070E0] shrink-0 transition-transform group-hover:translate-x-0.5" />
                          </div>
                        );
                      })}
                    </div>
                  )}

                  {/* Payment Receipt */}
                  {msg.paymentReceipt && (
                    <div className="w-full max-w-md p-4 rounded-xl bg-emerald-50/80 border border-emerald-300 text-xs font-mono space-y-1.5 text-slate-700">
                      <div className="flex items-center gap-1.5 text-emerald-800 font-bold text-sm mb-2">
                        <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                        PAYMENT SUCCESSFUL
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-500">Amount:</span>
                        <span className="text-slate-900 font-bold">
                          ${msg.paymentReceipt.amount} {msg.paymentReceipt.currency || "USD"}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-500">Status:</span>
                        <span className="text-emerald-700 font-bold">COMPLETED</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-500">PayPal Order ID:</span>
                        <span className="text-slate-900 font-medium">{msg.paymentReceipt.provider_order_id}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-500">Capture ID:</span>
                        <span className="text-slate-900 font-medium">{msg.paymentReceipt.capture_id}</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}

        {/* Live Operational Activity Panel */}
        <AgentActivityPanel actions={agentActions} currentStatus={agentStatus} />

        {/* Inline Purchase Approval Card */}
        {activePlan && (
          <PurchaseApprovalCard
            productName={activePlan.product_name}
            totalAmount={activePlan.total_amount}
            currency={activePlan.currency}
            reason={activePlan.recommendation_reason}
            onApprove={handleApprovePurchase}
            onDeny={handleDenyPurchase}
            isLoading={isLoading}
          />
        )}

        {/* Loading Indicator */}
        {isLoading && !activePlan && (
          <div className="flex items-center gap-2 text-xs text-[#0070E0] pl-9 animate-pulse">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>PayPilot is searching live products and comparing options...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Prompts Bar */}
      <div className="px-4 py-2 bg-[#F5F8FC] border-t border-slate-100 flex items-center gap-1.5 overflow-x-auto">
        <span className="text-[11px] font-medium text-slate-500 shrink-0">Try:</span>
        {DEMO_PROMPTS.slice(0, 3).map((prompt, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => handleSendMessage(prompt)}
            disabled={isLoading}
            className="text-[11px] bg-white hover:bg-slate-50 text-slate-700 hover:text-[#0070E0] px-2.5 py-1 rounded-full border border-slate-200 shrink-0 transition-colors cursor-pointer disabled:opacity-50 truncate max-w-xs"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input Composer */}
      <div className="p-3 sm:p-4 bg-white border-t border-slate-100">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage();
          }}
          className="relative flex items-center"
        >
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Ask anything about products, prices, or purchases..."
            disabled={isLoading}
            className="w-full pl-4 pr-12 py-3 rounded-2xl bg-[#F5F8FC] border border-slate-200 text-xs sm:text-sm text-[#14213D] placeholder:text-slate-400 focus:outline-none focus:border-[#0070E0] focus:bg-white focus:ring-2 focus:ring-[#0070E0]/10 transition-all disabled:opacity-60"
          />
          <button
            type="submit"
            disabled={isLoading || !inputText.trim()}
            className="absolute right-2 w-8 h-8 rounded-full bg-[#0070E0] hover:bg-[#005bb5] text-white flex items-center justify-center transition-all disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer shadow-sm"
            aria-label="Send message"
          >
            {isLoading ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Send className="w-3.5 h-3.5" />
            )}
          </button>
        </form>
      </div>
    </div>
  );
}

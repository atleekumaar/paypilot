"use client";

import React, { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Sparkles, Loader2, ShieldCheck, CheckCircle2 } from "lucide-react";
import AgentActivityPanel, { AgentActionItem } from "@/components/AgentActivityPanel";
import PurchaseApprovalCard from "@/components/PurchaseApprovalCard";

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
  "Find me the best laptop for AI development under $1200.",
  "Why do you recommend this laptop?",
  "Buy it.",
  "Which one has the best battery life?",
];

export default function AgentCommerceChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "msg-welcome",
      sender: "agent",
      text: "Hello! I am PayPilot, your autonomous commerce agent. You can ask me to discover, compare, and safely purchase products with PayPal Sandbox.",
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    },
  ]);
  const [inputText, setInputText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>(() => `sess-${Math.random().toString(36).substring(2, 9)}`);
  const [agentActions, setAgentActions] = useState<AgentActionItem[]>([]);
  const [agentStatus, setAgentStatus] = useState<string>("IDLE");
  const [activePlan, setActivePlan] = useState<any>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, agentActions, activePlan]);

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
      const res = await fetch("http://127.0.0.1:8000/api/agent/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, session_id: sessionId }),
      });

      if (!res.ok) {
        throw new Error(`Server returned HTTP ${res.status}`);
      }

      const data = await res.json();
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
      console.error("Agent error:", err);
      setMessages((prev) => [
        ...prev,
        {
          id: `agent-${Date.now()}`,
          sender: "agent",
          text: "I encountered an error communicating with the backend. Please ensure the PayPilot FastAPI service is running.",
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
      const approveRes = await fetch(`http://127.0.0.1:8000/api/agent/${sessionId}/approve`, {
        method: "POST",
      });

      if (!approveRes.ok) {
        throw new Error("Failed to process approval");
      }

      const approveData = await approveRes.json();
      setAgentStatus(approveData.status);
      if (approveData.actions) setAgentActions(approveData.actions);

      // 2. Automatically execute PayPal capture for verified Sandbox purchase
      const captureRes = await fetch("http://127.0.0.1:8000/api/payments/paypal/capture", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          purchase_plan_id: approveData.purchase_plan_id,
          paypal_order_id: approveData.paypal_order_id,
        }),
      });

      if (!captureRes.ok) {
        throw new Error("Failed to capture PayPal order");
      }

      const paymentData = await captureRes.json();
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
          text: `Checkout failed: ${err.message}`,
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
      const res = await fetch(`http://127.0.0.1:8000/api/agent/${sessionId}/deny`, {
        method: "POST",
      });
      const data = await res.json();
      setActivePlan(null);
      setAgentStatus("IDLE");
      if (data.actions) setAgentActions(data.actions);

      setMessages((prev) => [
        ...prev,
        {
          id: `agent-denied-${Date.now()}`,
          sender: "agent",
          text: data.message,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    } catch (err: any) {
      console.error("Denial error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto flex flex-col h-[700px] bg-[#090d16] border border-cyan-500/20 rounded-2xl shadow-2xl overflow-hidden my-6">
      {/* Agent Chat Header */}
      <div className="px-6 py-4 bg-[#0d1322] border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center text-white font-bold shadow-lg shadow-cyan-500/20">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              PayPilot Autonomous Agent
              <span className="px-2 py-0.5 text-[10px] font-semibold text-emerald-400 bg-emerald-950/60 border border-emerald-500/30 rounded-full">
                Active Session
              </span>
            </h3>
            <p className="text-[11px] text-slate-400 font-mono">
              Session ID: {sessionId} &bull; Policy Guard: ACTIVE
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs text-cyan-400 bg-cyan-950/40 border border-cyan-500/20 px-3 py-1.5 rounded-full">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
          <span>PayPal Sandbox</span>
        </div>
      </div>

      {/* Messages Stream */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex flex-col ${msg.sender === "user" ? "items-end" : "items-start"}`}
          >
            <div className="flex items-center gap-2 mb-1 text-[11px] text-slate-500">
              <span>{msg.sender === "user" ? "You" : "PayPilot Agent"}</span>
              <span>&bull;</span>
              <span>{msg.timestamp}</span>
            </div>

            <div
              className={`max-w-xl p-4 rounded-2xl text-sm leading-relaxed whitespace-pre-line ${
                msg.sender === "user"
                  ? "bg-gradient-to-r from-cyan-600 to-blue-600 text-white rounded-tr-none shadow-md"
                  : "bg-slate-900/90 border border-slate-800 text-slate-200 rounded-tl-none shadow-sm"
              }`}
            >
              {msg.text}
            </div>

            {/* Verified Payment Receipt embedded in message */}
            {msg.paymentReceipt && (
              <div className="mt-3 w-full max-w-md p-4 rounded-xl bg-emerald-950/40 border border-emerald-500/30 text-xs font-mono space-y-1.5 text-slate-300">
                <div className="flex items-center gap-1.5 text-emerald-400 font-bold text-sm mb-2">
                  <CheckCircle2 className="w-4 h-4" />
                  PAYMENT SUCCESSFUL
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Amount:</span>
                  <span className="text-white font-bold">${msg.paymentReceipt.amount} USD</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Status:</span>
                  <span className="text-emerald-400 font-bold">COMPLETED</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Order ID:</span>
                  <span className="text-slate-300">{msg.paymentReceipt.provider_order_id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Capture ID:</span>
                  <span className="text-slate-300">{msg.paymentReceipt.capture_id}</span>
                </div>
              </div>
            )}
          </div>
        ))}

        {/* Live Agent Operational Activity Panel */}
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
          <div className="flex items-center gap-2 text-xs text-cyan-400 animate-pulse">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>PayPilot is reasoning, calling commerce tools, and evaluating policies...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Quick Prompts Bar */}
      <div className="px-6 py-2.5 bg-[#0b101c] border-t border-slate-800/80 flex items-center gap-2 overflow-x-auto">
        <span className="text-[11px] text-slate-500 shrink-0">Try asking:</span>
        {DEMO_PROMPTS.map((prompt, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => handleSendMessage(prompt)}
            disabled={isLoading}
            className="text-xs bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-cyan-300 px-3 py-1.5 rounded-full border border-slate-800 shrink-0 transition-colors cursor-pointer disabled:opacity-50"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Message Input Form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSendMessage();
        }}
        className="p-4 bg-[#0d1322] border-t border-slate-800 flex gap-3"
      >
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Ask PayPilot e.g. 'Find me the best laptop for AI development under $1200'..."
          disabled={isLoading}
          className="flex-1 px-4 py-3 rounded-xl bg-slate-900 border border-slate-700/80 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 transition-all disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={isLoading || !inputText.trim()}
          className="px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold text-sm shadow-lg shadow-cyan-500/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-1.5 cursor-pointer"
        >
          {isLoading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <>
              <span>Send</span>
              <Send className="w-4 h-4" />
            </>
          )}
        </button>
      </form>
    </div>
  );
}

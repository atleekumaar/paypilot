"use client";

import React, { useState } from "react";
import Navbar from "@/components/Navbar";
import ShoppingWorkspace from "@/components/ShoppingWorkspace";
import AgentCommerceChat from "@/components/AgentCommerceChat";
import { Bot, Search } from "lucide-react";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"agent" | "catalogue">("agent");

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />

      <main className="flex-1 flex flex-col items-center justify-start px-4">
        {/* Hero Section */}
        <div className="max-w-4xl mx-auto pt-8 pb-3 text-center">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-cyan-500/20 bg-cyan-500/5 text-cyan-400 text-xs font-medium tracking-wide mb-4">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></span>
            PayPal AI Hackathon &bull; Phase 5 Post-Purchase Agent
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white mb-2">
            PAYPILOT
          </h1>

          <h2 className="text-lg sm:text-xl font-medium text-cyan-400 tracking-wide mb-2">
            End-to-End Autonomous Commerce Agent
          </h2>

          <p className="text-xs sm:text-sm text-slate-400 max-w-xl mx-auto font-normal mb-6">
            Discover &bull; Approve &bull; Pay with PayPal &bull; Track Shipments &bull; Resolve Delivery Delays
          </p>

          {/* Mode Switcher Tabs */}
          <div className="inline-flex items-center p-1 rounded-xl bg-slate-900 border border-slate-800 mb-2">
            <button
              onClick={() => setActiveTab("agent")}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
                activeTab === "agent"
                  ? "bg-cyan-500 text-black shadow-md shadow-cyan-500/20"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              <Bot className="w-3.5 h-3.5" />
              Autonomous Agent Mode
            </button>
            <button
              onClick={() => setActiveTab("catalogue")}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
                activeTab === "catalogue"
                  ? "bg-cyan-500 text-black shadow-md shadow-cyan-500/20"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              <Search className="w-3.5 h-3.5" />
              Direct Search Mode
            </button>
          </div>
        </div>

        {/* View Selection */}
        {activeTab === "agent" ? <AgentCommerceChat /> : <ShoppingWorkspace />}
      </main>

      <footer className="border-t border-slate-800/80 py-6 text-center text-xs text-slate-500 mt-12">
        <p>PayPilot &copy; 2026 &bull; PayPal AI Hackathon Phase 4: Agentic Commerce</p>
      </footer>
    </div>
  );
}

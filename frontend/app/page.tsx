"use client";

import React, { useState, useEffect } from "react";
import Navbar from "@/components/Navbar";
import ShoppingWorkspace from "@/components/ShoppingWorkspace";
import AgentCommerceChat from "@/components/AgentCommerceChat";
import {
  MessageSquare,
  Search,
  ShieldCheck,
  Zap,
  Layers,
  CreditCard,
  Package,
  Play,
  ArrowRight,
  Bot,
  Clock,
  Sparkles,
  Lock,
  X,
} from "lucide-react";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"agent" | "catalogue">("agent");
  const [demoModalOpen, setDemoModalOpen] = useState(false);

  useEffect(() => {
    const handleOpenDemo = () => setDemoModalOpen(true);
    window.addEventListener("open-paypilot-demo", handleOpenDemo);

    if (window.location.hash) {
      const id = window.location.hash.replace("#", "");
      if (id === "demo") {
        setDemoModalOpen(true);
      }
      const el = document.getElementById(id);
      if (el) {
        setTimeout(() => el.scrollIntoView({ behavior: "smooth" }), 150);
      }
    }

    if (window.location.search.includes("demo=true")) {
      setDemoModalOpen(true);
    }

    return () => {
      window.removeEventListener("open-paypilot-demo", handleOpenDemo);
    };
  }, []);

  return (
    <div className="flex flex-col min-h-screen bg-white text-[#14213D] selection:bg-[#EAF3FF] selection:text-[#003087]">
      <Navbar />

      {/* Ambient background gradients matching screenshot */}
      <div className="relative overflow-hidden">
        {/* Soft blue glow mesh at top right and bottom right */}
        <div className="pointer-events-none absolute -top-40 right-[-10%] w-[650px] h-[650px] rounded-full bg-gradient-to-br from-[#EAF3FF] via-[#0070E0]/10 to-transparent blur-3xl opacity-80" />
        <div className="pointer-events-none absolute top-[400px] right-[-5%] w-[450px] h-[450px] rounded-full bg-[#0070E0]/5 blur-3xl" />
        <div className="pointer-events-none absolute bottom-0 right-0 w-[500px] h-[350px] bg-gradient-to-tl from-[#003087]/5 via-[#0070E0]/5 to-transparent blur-2xl" />

        <main className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 pb-16">
          {/* Hero Section: 2 Columns */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center mb-20">
            {/* Left Column: Headline & Value Proposition */}
            <div className="lg:col-span-6 flex flex-col items-start text-left">
              {/* Badge */}
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-[#0070E0]/20 bg-[#EAF3FF] text-[#0070E0] text-xs font-semibold tracking-wide mb-6">
                <Sparkles className="w-3.5 h-3.5 text-[#0070E0]" />
                <span>AI-Powered Commerce Assistant</span>
              </div>

              {/* Main Headline */}
              <h1 className="text-4xl sm:text-5xl xl:text-6xl font-black tracking-tight text-[#14213D] leading-[1.1] mb-5">
                Shop Smarter with{" "}
                <span className="text-[#0070E0]">PayPilot</span>
              </h1>

              {/* Supporting Description */}
              <p className="text-base sm:text-lg text-slate-600 leading-relaxed max-w-xl mb-8 font-normal">
                Your AI shopping assistant that helps you discover products, compare
                options, get trusted recommendations, and complete purchases — all
                in a natural conversation.
              </p>

              {/* Action Buttons */}
              <div className="flex flex-wrap items-center gap-3.5 mb-12">
                <a
                  href="#assistant"
                  onClick={() => setActiveTab("agent")}
                  className="inline-flex items-center gap-2 px-6 py-3.5 rounded-xl bg-[#0070E0] hover:bg-[#005bb5] text-white text-sm font-bold tracking-tight shadow-sm hover:shadow transition-all"
                >
                  <span>Try the Assistant</span>
                  <span className="text-base">→</span>
                </a>
                <button
                  type="button"
                  onClick={() => setDemoModalOpen(true)}
                  className="inline-flex items-center gap-2 px-6 py-3.5 rounded-xl bg-white hover:bg-slate-50 text-slate-700 text-sm font-bold tracking-tight border border-slate-200 shadow-xs transition-all cursor-pointer"
                >
                  <Play className="w-4 h-4 text-[#0070E0] fill-[#0070E0]/20" />
                  <span>Watch Demo</span>
                </button>
              </div>

              {/* 4 Trust & Capability Items from Screenshot */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 w-full pt-6 border-t border-slate-100">
                <div className="flex flex-col items-start gap-2">
                  <div className="w-10 h-10 rounded-xl bg-[#EAF3FF] text-[#0070E0] flex items-center justify-center">
                    <MessageSquare className="w-5 h-5" />
                  </div>
                  <span className="text-xs font-bold text-[#14213D] leading-tight">
                    Conversational Shopping
                  </span>
                </div>

                <div className="flex flex-col items-start gap-2">
                  <div className="w-10 h-10 rounded-xl bg-[#EAF3FF] text-[#0070E0] flex items-center justify-center">
                    <Layers className="w-5 h-5" />
                  </div>
                  <span className="text-xs font-bold text-[#14213D] leading-tight">
                    Trusted Recommendations
                  </span>
                </div>

                <div className="flex flex-col items-start gap-2">
                  <div className="w-10 h-10 rounded-xl bg-[#EAF3FF] text-[#0070E0] flex items-center justify-center">
                    <ShieldCheck className="w-5 h-5" />
                  </div>
                  <span className="text-xs font-bold text-[#14213D] leading-tight">
                    Safe &amp; Verified Purchase Flow
                  </span>
                </div>

                <div className="flex flex-col items-start gap-2">
                  <div className="w-10 h-10 rounded-xl bg-[#EAF3FF] text-[#0070E0] flex items-center justify-center">
                    <Zap className="w-5 h-5" />
                  </div>
                  <span className="text-xs font-bold text-[#14213D] leading-tight">
                    Real-Time Product Data
                  </span>
                </div>
              </div>
            </div>

            {/* Right Column: Live Conversational AI Assistant Card */}
            <div className="lg:col-span-6 w-full flex justify-center">
              <AgentCommerceChat />
            </div>
          </div>

          {/* Mode Switcher Tabs for Full Interactive Workspace */}
          <div className="flex flex-col items-center justify-center my-12 text-center">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2.5">
              Interactive Workspace
            </span>
            <div className="inline-flex items-center p-1.5 rounded-2xl bg-[#F5F8FC] border border-slate-200 shadow-xs">
              <button
                onClick={() => setActiveTab("agent")}
                className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs sm:text-sm font-bold transition-all cursor-pointer ${
                  activeTab === "agent"
                    ? "bg-white text-[#0070E0] shadow-sm border border-slate-200/80"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                <Bot className="w-4 h-4 text-[#0070E0]" />
                <span>Autonomous Agent Mode</span>
              </button>
              <button
                onClick={() => setActiveTab("catalogue")}
                className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs sm:text-sm font-bold transition-all cursor-pointer ${
                  activeTab === "catalogue"
                    ? "bg-white text-[#0070E0] shadow-sm border border-slate-200/80"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                <Search className="w-4 h-4 text-[#0070E0]" />
                <span>Direct Search Mode</span>
              </button>
            </div>
          </div>

          {/* Secondary View Area (Active when user picks direct catalog mode) */}
          {activeTab === "catalogue" && (
            <div className="mb-20 animate-in fade-in duration-200">
              <ShoppingWorkspace />
            </div>
          )}

          {/* How PayPilot Works Section (From Screenshot) */}
          <section id="how-it-works" className="pt-16 pb-20 border-t border-slate-100 text-center scroll-mt-24">
            <div className="max-w-2xl mx-auto mb-14">
              <h2 className="text-3xl sm:text-4xl font-black text-[#14213D] tracking-tight mb-2">
                How PayPilot Works
              </h2>
              <p className="text-sm sm:text-base text-slate-600">
                From discovery to purchase — a simple, AI-powered flow.
              </p>
            </div>

            {/* 4 Steps Process */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 relative">
              {/* Step 1 */}
              <div className="flex flex-col items-center text-center p-6 rounded-3xl bg-white border border-slate-200/80 shadow-subtle hover:shadow-card transition-all group">
                <div className="w-14 h-14 rounded-2xl bg-[#EAF3FF] text-[#0070E0] flex items-center justify-center mb-4 group-hover:scale-105 transition-transform">
                  <MessageSquare className="w-6 h-6" />
                </div>
                <h3 className="text-base font-bold text-[#14213D] mb-1.5">
                  1. Chat Your Need
                </h3>
                <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                  Describe what you want in natural language.
                </p>
              </div>

              {/* Step 2 */}
              <div className="flex flex-col items-center text-center p-6 rounded-3xl bg-white border border-slate-200/80 shadow-subtle hover:shadow-card transition-all group">
                <div className="w-14 h-14 rounded-2xl bg-[#EAF3FF] text-[#0070E0] flex items-center justify-center mb-4 group-hover:scale-105 transition-transform">
                  <Search className="w-6 h-6" />
                </div>
                <h3 className="text-base font-bold text-[#14213D] mb-1.5">
                  2. Get Recommendations
                </h3>
                <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                  Receive trusted, relevant product options.
                </p>
              </div>

              {/* Step 3 */}
              <div className="flex flex-col items-center text-center p-6 rounded-3xl bg-white border border-slate-200/80 shadow-subtle hover:shadow-card transition-all group">
                <div className="w-14 h-14 rounded-2xl bg-[#EAF3FF] text-[#0070E0] flex items-center justify-center mb-4 group-hover:scale-105 transition-transform">
                  <CreditCard className="w-6 h-6" />
                </div>
                <h3 className="text-base font-bold text-[#14213D] mb-1.5">
                  3. Review &amp; Approve
                </h3>
                <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                  Compare, verify, and approve the best choice.
                </p>
              </div>

              {/* Step 4 */}
              <div className="flex flex-col items-center text-center p-6 rounded-3xl bg-white border border-slate-200/80 shadow-subtle hover:shadow-card transition-all group">
                <div className="w-14 h-14 rounded-2xl bg-[#EAF3FF] text-[#0070E0] flex items-center justify-center mb-4 group-hover:scale-105 transition-transform">
                  <Package className="w-6 h-6" />
                </div>
                <h3 className="text-base font-bold text-[#14213D] mb-1.5">
                  4. Complete Purchase
                </h3>
                <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                  Let the agent handle the purchase (with your approval).
                </p>
              </div>
            </div>
          </section>

          {/* Features Section */}
          <section id="features" className="pt-16 pb-20 border-t border-slate-100 scroll-mt-24">
            <div className="max-w-3xl mx-auto text-center mb-14">
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#EAF3FF] text-[#0070E0] text-xs font-bold uppercase tracking-wider mb-3">
                <ShieldCheck className="w-3.5 h-3.5" />
                Fintech Security &amp; Autonomous AI
              </div>
              <h2 className="text-3xl sm:text-4xl font-black text-[#14213D] tracking-tight mb-3">
                Built for Autonomous, Safe Shopping
              </h2>
              <p className="text-slate-600 text-sm sm:text-base leading-relaxed">
                Combining PayPal&apos;s trusted payment rails with state-of-the-art
                agentic AI reasoning and deterministic policy guardrails.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {/* Feature 1 */}
              <div className="p-6 rounded-3xl bg-[#F5F8FC]/70 border border-slate-200/80 hover:bg-white hover:shadow-card transition-all text-left">
                <div className="w-11 h-11 rounded-2xl bg-[#0070E0] text-white flex items-center justify-center mb-4 shadow-sm">
                  <Bot className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-[#14213D] mb-2">
                  Conversational AI Shopping
                </h3>
                <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                  Natural conversation that converts open-ended requirements into structured, verifiable product filters.
                </p>
              </div>

              {/* Feature 2 */}
              <div className="p-6 rounded-3xl bg-[#F5F8FC]/70 border border-slate-200/80 hover:bg-white hover:shadow-card transition-all text-left">
                <div className="w-11 h-11 rounded-2xl bg-[#0070E0] text-white flex items-center justify-center mb-4 shadow-sm">
                  <Layers className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-[#14213D] mb-2">
                  Multi-Factor Scoring
                </h3>
                <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                  Evaluates specs, hardware requirements, ratings, and budgets against live catalogue data.
                </p>
              </div>

              {/* Feature 3 */}
              <div className="p-6 rounded-3xl bg-[#F5F8FC]/70 border border-slate-200/80 hover:bg-white hover:shadow-card transition-all text-left">
                <div className="w-11 h-11 rounded-2xl bg-[#0070E0] text-white flex items-center justify-center mb-4 shadow-sm">
                  <Lock className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-[#14213D] mb-2">
                  Human-in-the-Loop Safety
                </h3>
                <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                  The AI prepares purchase plans and verifies pricing, but requires explicit human authorization before payment.
                </p>
              </div>

              {/* Feature 4 */}
              <div className="p-6 rounded-3xl bg-[#F5F8FC]/70 border border-slate-200/80 hover:bg-white hover:shadow-card transition-all text-left">
                <div className="w-11 h-11 rounded-2xl bg-[#0070E0] text-white flex items-center justify-center mb-4 shadow-sm">
                  <CreditCard className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-[#14213D] mb-2">
                  PayPal Sandbox v2
                </h3>
                <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                  Direct server-side PayPal order creation, webhook verification, and capture execution.
                </p>
              </div>

              {/* Feature 5 */}
              <div className="p-6 rounded-3xl bg-[#F5F8FC]/70 border border-slate-200/80 hover:bg-white hover:shadow-card transition-all text-left">
                <div className="w-11 h-11 rounded-2xl bg-[#003087] text-white flex items-center justify-center mb-4 shadow-sm">
                  <Zap className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-[#14213D] mb-2">
                  Agent Execution Telemetry
                </h3>
                <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                  Full step-by-step visibility into tool selection, policy evaluations, and reasoning paths.
                </p>
              </div>

              {/* Feature 6 */}
              <div className="p-6 rounded-3xl bg-[#F5F8FC]/70 border border-slate-200/80 hover:bg-white hover:shadow-card transition-all text-left">
                <div className="w-11 h-11 rounded-2xl bg-[#003087] text-white flex items-center justify-center mb-4 shadow-sm">
                  <Package className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-[#14213D] mb-2">
                  Shipment Tracking
                </h3>
                <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                  Real-time carrier milestone tracking with estimated arrival times and journey visualizers.
                </p>
              </div>

              {/* Feature 7 */}
              <div className="p-6 rounded-3xl bg-[#F5F8FC]/70 border border-slate-200/80 hover:bg-white hover:shadow-card transition-all text-left">
                <div className="w-11 h-11 rounded-2xl bg-[#003087] text-white flex items-center justify-center mb-4 shadow-sm">
                  <Clock className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-[#14213D] mb-2">
                  Delay Resolution Agent
                </h3>
                <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                  Proactively identifies delivery bottlenecks and drafts merchant support inquiries for your review.
                </p>
              </div>

              {/* Feature 8 */}
              <div className="p-6 rounded-3xl bg-[#F5F8FC]/70 border border-slate-200/80 hover:bg-white hover:shadow-card transition-all text-left">
                <div className="w-11 h-11 rounded-2xl bg-[#003087] text-white flex items-center justify-center mb-4 shadow-sm">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-[#14213D] mb-2">
                  Audit Logging &amp; Outbox
                </h3>
                <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                  Cryptographic transaction audit trail with transactional outbox resilience for zero dropped events.
                </p>
              </div>
            </div>
          </section>

          {/* Interactive Demo Section */}
          <section id="demo" className="pt-16 pb-20 border-t border-slate-100 scroll-mt-24">
            <div className="p-8 sm:p-12 rounded-3xl bg-gradient-to-br from-[#003087] via-[#005bb5] to-[#0070E0] text-white flex flex-col lg:flex-row items-center justify-between gap-8 shadow-card">
              <div className="max-w-xl text-left">
                <span className="inline-block px-3 py-1 rounded-full bg-white/10 text-white text-xs font-semibold uppercase tracking-wider mb-3">
                  Live Interactive Experience
                </span>
                <h2 className="text-2xl sm:text-3xl font-black tracking-tight mb-3">
                  Experience Autonomous Commerce with PayPal Confidence
                </h2>
                <p className="text-slate-100 text-xs sm:text-sm leading-relaxed mb-6">
                  Try PayPilot with realistic laptop, audio, and peripheral shopping queries. Watch the agent evaluate policies and present clear human-in-the-loop approvals.
                </p>
                <div className="flex flex-wrap items-center gap-3">
                  <a
                    href="#assistant"
                    className="px-6 py-3 rounded-xl bg-white text-[#003087] text-xs sm:text-sm font-bold shadow-sm hover:bg-slate-100 transition-colors"
                  >
                    Launch Assistant Now
                  </a>
                  <button
                    onClick={() => setDemoModalOpen(true)}
                    className="px-6 py-3 rounded-xl bg-white/15 hover:bg-white/20 text-white text-xs sm:text-sm font-semibold transition-colors cursor-pointer"
                  >
                    View Interactive Walkthrough
                  </button>
                </div>
              </div>

              <div className="w-full max-w-md bg-white rounded-2xl p-5 text-slate-800 shadow-modal text-left space-y-3">
                <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
                  <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                    Quick Demo Prompts
                  </span>
                  <span className="text-[10px] font-mono text-[#0070E0] bg-[#EAF3FF] px-2 py-0.5 rounded-full font-bold">
                    Sandbox Ready
                  </span>
                </div>
                <div className="space-y-2">
                  {[
                    "I want a laptop for AI/ML under ₹90,000.",
                    "Find me the best laptop for AI development under $1200.",
                    "Why do you recommend this laptop?",
                    "Where is my order ord-guest-101?",
                  ].map((demoPrompt, idx) => (
                    <a
                      key={idx}
                      href="#assistant"
                      className="block p-2.5 rounded-xl bg-[#F5F8FC] hover:bg-[#EAF3FF] text-xs font-medium text-slate-700 hover:text-[#0070E0] transition-colors border border-slate-200/80"
                    >
                      &ldquo;{demoPrompt}&rdquo;
                    </a>
                  ))}
                </div>
              </div>
            </div>
          </section>
        </main>
      </div>

      {/* Demo Modal */}
      {demoModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="relative w-full max-w-2xl bg-white border border-slate-200 rounded-3xl shadow-modal p-6 sm:p-8 overflow-hidden text-left">
            <button
              onClick={() => setDemoModalOpen(false)}
              className="absolute top-5 right-5 p-2 rounded-full text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#EAF3FF] text-[#0070E0] text-xs font-bold uppercase tracking-wider mb-3">
              <Play className="w-3.5 h-3.5 fill-[#0070E0]" />
              Interactive Walkthrough
            </div>

            <h3 className="text-2xl font-black text-[#14213D] tracking-tight mb-3">
              How PayPilot Purchases Work
            </h3>
            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed mb-6">
              PayPilot executes an end-to-end commerce lifecycle with strict human-in-the-loop protection.
            </p>

            <div className="space-y-4 mb-6">
              <div className="flex items-start gap-3 p-3.5 rounded-2xl bg-[#F5F8FC] border border-slate-200">
                <div className="w-7 h-7 rounded-full bg-[#0070E0] text-white font-bold text-xs flex items-center justify-center shrink-0">
                  1
                </div>
                <div>
                  <h4 className="text-xs font-bold text-[#14213D]">User Inquires with Natural Language</h4>
                  <p className="text-[11px] text-slate-600 mt-0.5">
                    User states their preference: &ldquo;I want a laptop for AI/ML under ₹90,000.&rdquo;
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3 p-3.5 rounded-2xl bg-[#F5F8FC] border border-slate-200">
                <div className="w-7 h-7 rounded-full bg-[#0070E0] text-white font-bold text-xs flex items-center justify-center shrink-0">
                  2
                </div>
                <div>
                  <h4 className="text-xs font-bold text-[#14213D]">Multi-Factor Matching &amp; Explanation</h4>
                  <p className="text-[11px] text-slate-600 mt-0.5">
                    PayPilot evaluates live catalogue items, filters by budget and specs (GPU/RAM), and presents top candidates.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3 p-3.5 rounded-2xl bg-[#F5F8FC] border border-slate-200">
                <div className="w-7 h-7 rounded-full bg-[#0070E0] text-white font-bold text-xs flex items-center justify-center shrink-0">
                  3
                </div>
                <div>
                  <h4 className="text-xs font-bold text-[#14213D]">Human-in-the-Loop Explicit Approval</h4>
                  <p className="text-[11px] text-slate-600 mt-0.5">
                    The agent halts execution and presents an immutable Purchase Approval Card. Payment cannot occur without explicit user consent.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3 p-3.5 rounded-2xl bg-[#F5F8FC] border border-slate-200">
                <div className="w-7 h-7 rounded-full bg-emerald-600 text-white font-bold text-xs flex items-center justify-center shrink-0">
                  4
                </div>
                <div>
                  <h4 className="text-xs font-bold text-[#14213D]">PayPal Sandbox Capture &amp; Telemetry</h4>
                  <p className="text-[11px] text-slate-600 mt-0.5">
                    Upon approval, PayPal Sandbox v2 captures funds, creates an authoritative order record, and begins shipment telemetry.
                  </p>
                </div>
              </div>
            </div>

            <button
              onClick={() => {
                setDemoModalOpen(false);
                const el = document.getElementById("assistant");
                el?.scrollIntoView({ behavior: "smooth" });
                const input = el?.querySelector("input");
                input?.focus();
              }}
              className="w-full py-3.5 rounded-2xl bg-[#0070E0] hover:bg-[#005bb5] text-white font-bold text-xs sm:text-sm transition-all shadow-sm cursor-pointer"
            >
              Try with Live Assistant Now
            </button>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="border-t border-slate-100 bg-[#F5F8FC]/60 py-12 text-slate-500 text-xs mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-[#0070E0] flex items-center justify-center text-white font-extrabold text-xs">
              <span className="italic">P</span>
            </div>
            <span className="font-extrabold text-sm text-[#14213D] tracking-tight">
              PayPilot
            </span>
            <span className="text-slate-400">&bull;</span>
            <span className="text-slate-600">
              PayPal AI Hackathon: Autonomous Agentic Commerce
            </span>
          </div>

          <div className="flex items-center gap-6 text-xs text-slate-600">
            <span className="flex items-center gap-1.5">
              <Lock className="w-3.5 h-3.5 text-[#0070E0]" />
              Human-in-the-Loop Guaranteed
            </span>
            <span className="flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
              PayPal Sandbox Verified
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}

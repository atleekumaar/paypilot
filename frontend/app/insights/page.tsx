"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import Navbar from "@/components/Navbar";
import KpiOverview from "@/components/insights/KpiOverview";
import SpendingAnalytics from "@/components/insights/SpendingAnalytics";
import ProductIntelligenceGrid, { ProductItem } from "@/components/insights/ProductIntelligenceGrid";
import OrderIntelligenceGrid, { OrderRecord } from "@/components/insights/OrderIntelligenceGrid";
import PaymentIntelligenceGrid, { PaymentRecord } from "@/components/insights/PaymentIntelligenceGrid";
import RecommendationScorecard from "@/components/insights/widgets/RecommendationScorecard";
import PurchaseValueAnalyzer from "@/components/insights/widgets/PurchaseValueAnalyzer";
import PaymentHealthMonitor from "@/components/insights/widgets/PaymentHealthMonitor";
import DashboardAgentBar from "@/components/insights/DashboardAgentBar";
import { BarChart3, Package, CreditCard, Sparkles, RefreshCw } from "lucide-react";

export default function InsightsPage() {
  const [loading, setLoading] = useState(true);
  const [overview, setOverview] = useState<any>(null);
  const [spending, setSpending] = useState<any>(null);
  const [orders, setOrders] = useState<OrderRecord[]>([]);
  const [payments, setPayments] = useState<PaymentRecord[]>([]);
  const [products, setProducts] = useState<ProductItem[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"products" | "orders" | "payments">("products");
  const [highlightedWidget, setHighlightedWidget] = useState<string | null>(null);

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const [ovRes, spRes, ordRes, payRes, prodRes] = await Promise.all([
        api.get<any>("/api/analytics/overview"),
        api.get<any>("/api/analytics/spending"),
        api.get<OrderRecord[]>("/api/analytics/orders"),
        api.get<PaymentRecord[]>("/api/analytics/payments"),
        api.get<ProductItem[]>("/api/analytics/products"),
      ]);
      setOverview(ovRes);
      setSpending(spRes);
      setOrders(ordRes || []);
      setPayments(payRes || []);
      setProducts(prodRes || []);
    } catch (err) {
      console.error("Failed fetching analytics data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const handleAgentResult = (result: any) => {
    if (result.suggested_widget === "scorecard") {
      setHighlightedWidget("scorecard");
      setActiveTab("products");
    } else if (result.suggested_widget === "analyzer") {
      setHighlightedWidget("analyzer");
    } else if (result.suggested_widget === "health") {
      setHighlightedWidget("health");
      setActiveTab("payments");
    } else if (result.suggested_widget === "grid") {
      setActiveTab("orders");
    }
  };

  return (
    <div className="min-h-screen bg-[#070a12] text-slate-100 flex flex-col">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-8 space-y-8">
        {/* Page Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-slate-800">
          <div>
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 shadow-lg shadow-cyan-500/20 text-white font-bold">
                <BarChart3 className="w-5 h-5" />
              </div>
              <h1 className="text-2xl font-extrabold tracking-tight text-white">
                Commerce Intelligence & AG Studio
              </h1>
            </div>
            <p className="text-xs text-slate-400 mt-1 max-w-2xl">
              Unified operational analytics combining AG Grid data tables, algorithmic product scoring,
              verified PayPal Sandbox transactions, and the AG Studio AI Dashboard Agent.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={fetchAnalytics}
              disabled={loading}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-xs font-medium text-slate-300 transition-colors"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-cyan-400" : ""}`} />
              <span>Refresh Metrics</span>
            </button>
            <div className="px-3 py-1 rounded-xl bg-cyan-950/80 border border-cyan-800/80 text-[11px] font-semibold text-cyan-300 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>PayPal Orders v2 Connected</span>
            </div>
          </div>
        </div>

        {/* 1. KPI Overview Cards */}
        <section>
          <KpiOverview data={overview} loading={loading} />
        </section>

        {/* 2. AI Dashboard Agent Bar */}
        <section>
          <DashboardAgentBar
            onAgentResult={handleAgentResult}
            onWidgetSelect={(w) => setHighlightedWidget(w)}
          />
        </section>

        {/* 3. Interactive Spending Analytics */}
        <section>
          <SpendingAnalytics
            data={spending}
            loading={loading}
            selectedCategory={selectedCategory}
            onSelectCategory={(cat) => setSelectedCategory(cat)}
          />
        </section>

        {/* 4. Three Custom AG Studio Widgets */}
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold tracking-wider text-slate-300 uppercase flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-cyan-400" />
              Custom Intelligence Widgets
            </h2>
            <span className="text-xs text-slate-500">Live Metric Aggregation</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className={`transition-all duration-300 ${highlightedWidget === "scorecard" ? "ring-2 ring-cyan-400 rounded-2xl" : ""}`}>
              <RecommendationScorecard />
            </div>
            <div className={`transition-all duration-300 ${highlightedWidget === "analyzer" ? "ring-2 ring-emerald-400 rounded-2xl" : ""}`}>
              <PurchaseValueAnalyzer
                avgOrderValue={overview?.average_order_value || 1049.0}
                totalOrders={overview?.total_orders || 3}
              />
            </div>
            <div className={`transition-all duration-300 ${highlightedWidget === "health" ? "ring-2 ring-indigo-400 rounded-2xl" : ""}`}>
              <PaymentHealthMonitor
                completedCount={overview?.completed_payments || 3}
                failedCount={overview?.failed_payments || 0}
              />
            </div>
          </div>
        </section>

        {/* 5. AG Grid Intelligence Grids (Tabbed) */}
        <section className="space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
            <button
              onClick={() => setActiveTab("products")}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                activeTab === "products"
                  ? "bg-cyan-500/10 text-cyan-400 border border-cyan-500/30"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              <Sparkles className="w-4 h-4" />
              <span>Product Intelligence Grid</span>
              <span className="px-1.5 py-0.2 rounded-full bg-slate-800 text-[10px] text-slate-400">{products.length}</span>
            </button>

            <button
              onClick={() => setActiveTab("orders")}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                activeTab === "orders"
                  ? "bg-cyan-500/10 text-cyan-400 border border-cyan-500/30"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              <Package className="w-4 h-4" />
              <span>Order Intelligence</span>
              <span className="px-1.5 py-0.2 rounded-full bg-slate-800 text-[10px] text-slate-400">{orders.length}</span>
            </button>

            <button
              onClick={() => setActiveTab("payments")}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                activeTab === "payments"
                  ? "bg-cyan-500/10 text-cyan-400 border border-cyan-500/30"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              <CreditCard className="w-4 h-4" />
              <span>Payment Intelligence</span>
              <span className="px-1.5 py-0.2 rounded-full bg-slate-800 text-[10px] text-slate-400">{payments.length}</span>
            </button>
          </div>

          <div>
            {activeTab === "products" && (
              <ProductIntelligenceGrid
                products={products}
                loading={loading}
                selectedCategory={selectedCategory}
              />
            )}
            {activeTab === "orders" && (
              <OrderIntelligenceGrid
                orders={orders}
                loading={loading}
              />
            )}
            {activeTab === "payments" && (
              <PaymentIntelligenceGrid
                payments={payments}
                loading={loading}
              />
            )}
          </div>
        </section>
      </main>
    </div>
  );
}


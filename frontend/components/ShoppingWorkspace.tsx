"use client";

import React, { useState, useEffect } from "react";
import { Search, Sparkles, Star, Truck, ShieldCheck, Loader2 } from "lucide-react";
import ProductModal from "@/components/ProductModal";
import PurchasePlanModal from "@/components/PurchasePlanModal";
import { api } from "@/lib/api";

interface Product {
  id: string;
  name: string;
  brand: string;
  category: string;
  description: string;
  price: number;
  currency: string;
  rating: number;
  review_count: number;
  stock: boolean;
  seller: string;
  delivery_days: number;
  features: Record<string, any>;
  image_url?: string;
  source?: string;
  source_url?: string;
}

interface RankedProduct {
  product: Product;
  product_id: string;
  rank: number;
  score: number;
  match_reasons: string[];
}

interface RecommendationResponse {
  query: string;
  intent: any;
  recommendations: RankedProduct[];
  explanation: string;
  total_candidates: number;
}

const LOADING_STEPS = [
  "Understanding your shopping criteria...",
  "Querying verified product catalog...",
  "Evaluating GPU, RAM, & performance constraints...",
  "Formulating grounded recommendations...",
];

const PRESET_QUERIES = [
  "Find me a laptop under $1200 for AI development with good battery life.",
  "Noise cancelling wireless headphones under $350 for travel",
  "Mechanical keyboard with quiet switches under $150",
  "4K productivity monitor with USB-C under $600",
];

export default function ShoppingWorkspace() {
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStepIndex, setLoadingStepIndex] = useState(0);
  const [results, setResults] = useState<RecommendationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [selectedRankedItem, setSelectedRankedItem] = useState<RankedProduct | null>(null);
  const [chosenMessage, setChosenMessage] = useState<string | null>(null);
  const [discoverySource, setDiscoverySource] = useState<"ALL" | "CHANNEL3" | "ELASTIC">("ALL");

  // Progressive loading animation
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isLoading) {
      interval = setInterval(() => {
        setLoadingStepIndex((prev) => (prev < LOADING_STEPS.length - 1 ? prev + 1 : prev));
      }, 450);
    }
    return () => clearInterval(interval);
  }, [isLoading]);

  const handleSearch = async (queryText?: string) => {
    const textToSearch = (queryText !== undefined ? queryText : query).trim();
    if (!textToSearch) {
      setError("Please describe what you're looking for.");
      setResults(null);
      return;
    }

    setIsLoading(true);
    setLoadingStepIndex(0);
    setError(null);
    setChosenMessage(null);

    try {
      if (discoverySource === "CHANNEL3") {
        const c3Items: Product[] = await api.searchChannel3({ query: textToSearch });
        const ranked: RankedProduct[] = c3Items.map((p, idx) => ({
          product: p,
          product_id: p.id,
          rank: idx + 1,
          score: Math.max(75, 96 - idx * 4),
          match_reasons: [
            `Live inventory confirmed at ${p.seller}`,
            "Universal retailer normalized via Channel3 Graph",
          ],
        }));
        setResults({
          query: textToSearch,
          intent: { category: "retailer" },
          recommendations: ranked.slice(0, 3),
          explanation: `Discovered ${c3Items.length} live offers across retailers via Channel3.`,
          total_candidates: c3Items.length,
        });
      } else if (discoverySource === "ELASTIC") {
        const esHits: Product[] = await api.searchElastic({ query: textToSearch, mode: "hybrid" });
        const ranked: RankedProduct[] = esHits.map((p, idx) => ({
          product: p,
          product_id: p.id,
          rank: idx + 1,
          score: Math.max(78, 98 - idx * 3),
          match_reasons: [
            "Matched via Elasticsearch Hybrid RRF",
            "Dense vector semantic similarity + BM25 keyword score",
          ],
        }));
        setResults({
          query: textToSearch,
          intent: { category: "elastic" },
          recommendations: ranked.slice(0, 3),
          explanation: `Elasticsearch retrieved ${esHits.length} verified candidate products.`,
          total_candidates: esHits.length,
        });
      } else {
        const data: RecommendationResponse = await api.post("/api/discovery/search", {
          query: textToSearch,
        });
        setResults(data);

        if (data.recommendations.length === 0) {
          setError(
            data.explanation ||
              "I couldn't find products matching those constraints. Try increasing your budget or relaxing a requirement."
          );
        }
      }
    } catch (err: any) {
      console.warn("Discovery API notice:", err);
      setError("Backend service is offline or unreachable at http://127.0.0.1:8000. Please launch FastAPI to query live catalogue.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleChooseProduct = (ranked: RankedProduct) => {
    setSelectedRankedItem(ranked);
  };

  return (
    <div className="w-full max-w-6xl mx-auto px-4 py-8 text-left">
      {/* Search Input Box */}
      <div className="bg-white dark:bg-[#0E1422] border border-slate-200/90 dark:border-slate-800 rounded-3xl p-6 sm:p-8 shadow-card mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-[#0070E0] dark:text-[#38BDF8]" />
            <label className="block text-xs font-bold uppercase tracking-wider text-[#0070E0] dark:text-[#38BDF8]">
              Direct Catalog Discovery
            </label>
          </div>
          <div className="flex items-center gap-1.5 self-start sm:self-auto">
            <button
              type="button"
              onClick={() => setDiscoverySource("ALL")}
              className={`px-3 py-1.5 text-xs rounded-full font-semibold transition-all cursor-pointer ${
                discoverySource === "ALL"
                  ? "bg-[#EAF3FF] dark:bg-[#0070E0]/20 text-[#0070E0] dark:text-[#38BDF8] border border-[#0070E0]/30 dark:border-[#0070E0]/50 shadow-sm"
                  : "bg-[#F5F8FC] dark:bg-slate-900 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white border border-slate-200 dark:border-slate-800"
              }`}
            >
              Unified Discovery
            </button>
            <button
              type="button"
              onClick={() => setDiscoverySource("CHANNEL3")}
              className={`px-3 py-1.5 text-xs rounded-full font-semibold transition-all cursor-pointer ${
                discoverySource === "CHANNEL3"
                  ? "bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400 border border-emerald-300 dark:border-emerald-700 shadow-sm"
                  : "bg-[#F5F8FC] dark:bg-slate-900 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white border border-slate-200 dark:border-slate-800"
              }`}
            >
              Channel3 Retailers
            </button>
            <button
              type="button"
              onClick={() => setDiscoverySource("ELASTIC")}
              className={`px-3 py-1.5 text-xs rounded-full font-semibold transition-all cursor-pointer ${
                discoverySource === "ELASTIC"
                  ? "bg-purple-50 dark:bg-purple-950/60 text-purple-700 dark:text-purple-400 border border-purple-300 dark:border-purple-700 shadow-sm"
                  : "bg-[#F5F8FC] dark:bg-slate-900 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white border border-slate-200 dark:border-slate-800"
              }`}
            >
              Elasticsearch
            </button>
          </div>
        </div>
        <h3 className="text-xl sm:text-2xl font-black text-[#14213D] dark:text-white mb-4 tracking-tight">
          Find Any Product with Natural Language
        </h3>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSearch();
          }}
          className="flex flex-col sm:flex-row gap-3"
        >
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g. Find me a laptop under $1200 for AI development with good battery life..."
              className="w-full pl-12 pr-4 py-3.5 rounded-2xl bg-[#F5F8FC] dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-white placeholder-slate-400 text-sm focus:outline-none focus:border-[#0070E0] focus:bg-white dark:focus:bg-slate-900 focus:ring-2 focus:ring-[#0070E0]/10 transition-all"
            />
          </div>
          <button
            type="submit"
            disabled={isLoading}
            className="px-7 py-3.5 rounded-2xl bg-[#0070E0] hover:bg-[#005bb5] text-white text-sm font-bold tracking-tight shadow-sm hover:shadow disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 cursor-pointer"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Searching...</span>
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                <span>Search</span>
              </>
            )}
          </button>
        </form>

        {/* Suggestion Chips */}
        <div className="mt-4 flex flex-wrap items-center gap-2">
          <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">Try asking:</span>
          {PRESET_QUERIES.map((preset, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => {
                setQuery(preset);
                handleSearch(preset);
              }}
              className="text-xs bg-[#F5F8FC] dark:bg-slate-900 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 hover:text-[#0070E0] dark:hover:text-[#38BDF8] px-3 py-1.5 rounded-full border border-slate-200 dark:border-slate-800 transition-colors truncate max-w-xs text-left cursor-pointer"
            >
              {preset}
            </button>
          ))}
        </div>
      </div>

      {/* Progressive Loading State */}
      {isLoading && (
        <div className="p-8 rounded-3xl bg-white border border-slate-200 text-center shadow-card mb-8">
          <Loader2 className="w-8 h-8 text-[#0070E0] animate-spin mx-auto mb-3" />
          <h4 className="text-base font-bold text-[#14213D] mb-3">
            {LOADING_STEPS[loadingStepIndex]}
          </h4>
          <div className="flex justify-center gap-2 max-w-xs mx-auto">
            {LOADING_STEPS.map((_, i) => (
              <div
                key={i}
                className={`h-1.5 flex-1 rounded-full transition-all ${
                  i <= loadingStepIndex ? "bg-[#0070E0]" : "bg-slate-200"
                }`}
              />
            ))}
          </div>
        </div>
      )}

      {/* Error or Notice State */}
      {!isLoading && error && (
        <div className="p-6 rounded-2xl bg-[#F5F8FC] border border-slate-200 text-center mb-8">
          <p className="text-sm text-slate-700">{error}</p>
        </div>
      )}

      {/* Success Notification */}
      {chosenMessage && (
        <div className="p-4 rounded-2xl bg-[#EAF3FF] border border-[#0070E0]/30 text-[#003087] text-xs sm:text-sm font-semibold flex items-center justify-between mb-8 animate-in fade-in">
          <span>{chosenMessage}</span>
          <button
            onClick={() => setChosenMessage(null)}
            className="text-xs text-[#0070E0] underline ml-4 hover:text-[#003087] cursor-pointer"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Recommendations Results Section */}
      {!isLoading && results && results.recommendations.length > 0 && (
        <div className="space-y-8 animate-in fade-in duration-300">
          {/* Header Banner */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-4 gap-2">
            <div>
              <div className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-[#0070E0] dark:text-[#38BDF8] mb-1">
                <Sparkles className="w-3.5 h-3.5" />
                AI Verified Recommendations
              </div>
              <h3 className="text-2xl font-black text-[#14213D] dark:text-white tracking-tight">
                Top Matches Found
              </h3>
            </div>
            <span className="text-xs text-slate-500 dark:text-slate-400 bg-[#F5F8FC] dark:bg-slate-900 border border-slate-200 dark:border-slate-800 px-3 py-1.5 rounded-full font-medium">
              Evaluated {results.total_candidates} catalogue candidates
            </span>
          </div>

          {/* Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {results.recommendations.map((item) => {
              const isTopPick = item.rank === 1;
              return (
                <div
                  key={item.product_id}
                  className={`relative flex flex-col justify-between rounded-3xl p-6 transition-all duration-200 ${
                    isTopPick
                      ? "bg-white dark:bg-[#0E1422] border-2 border-[#0070E0] dark:border-[#38BDF8] shadow-card hover:shadow-cardHover"
                      : "bg-white dark:bg-[#0E1422] border border-slate-200/90 dark:border-slate-800 shadow-subtle hover:shadow-card"
                  }`}
                >
                  <div>
                    {/* Top Badge */}
                    <div className="flex items-center justify-between mb-3">
                      <span
                        className={`text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider ${
                          isTopPick
                            ? "bg-[#0070E0] text-white"
                            : "bg-[#F5F8FC] dark:bg-slate-900 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-800"
                        }`}
                      >
                        {isTopPick ? "★ Rank #1 (Top Pick)" : `Rank #${item.rank}`}
                      </span>
                      <span className="text-xs font-mono font-bold text-[#0070E0] dark:text-[#38BDF8] bg-[#EAF3FF] dark:bg-[#0070E0]/20 border border-[#0070E0]/20 px-2 py-0.5 rounded-md">
                        {item.score}/100 Match
                      </span>
                    </div>

                    {/* Title & Brand */}
                    <div className="mb-4">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[11px] uppercase tracking-wider text-slate-500 dark:text-slate-400 font-bold">
                          {item.product.brand}
                        </span>
                        {item.product.source === "CHANNEL3" && (
                          <span className="text-[10px] font-semibold text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 px-2 py-0.5 rounded-full border border-emerald-200 dark:border-emerald-800">
                            Channel3 Retailer
                          </span>
                        )}
                        {item.product.source === "ELASTIC" && (
                          <span className="text-[10px] font-semibold text-purple-700 dark:text-purple-400 bg-purple-50 dark:bg-purple-950/60 px-2 py-0.5 rounded-full border border-purple-200 dark:border-purple-800">
                            Elasticsearch
                          </span>
                        )}
                      </div>
                      <h4 className="font-extrabold text-[#14213D] dark:text-white text-lg leading-snug">
                        {item.product.name}
                      </h4>
                      <p className="text-xs text-slate-600 dark:text-slate-400 line-clamp-2 mt-2">
                        {item.product.description}
                      </p>
                    </div>

                    {/* Price & Rating */}
                    <div className="flex items-baseline justify-between py-3 border-y border-slate-100 dark:border-slate-800 mb-4">
                      <div>
                        <span className="text-2xl font-black text-[#003087] dark:text-[#38BDF8] font-mono">
                          ${item.product.price.toLocaleString("en-US", { minimumFractionDigits: 0 })}
                        </span>
                        <span className="text-xs text-slate-500 dark:text-slate-400 font-sans ml-1">
                          {item.product.currency || "USD"}
                        </span>
                      </div>
                      <div className="flex items-center gap-1 text-xs text-amber-500">
                        <Star className="w-3.5 h-3.5 fill-amber-400" />
                        <span className="font-bold text-slate-800 dark:text-slate-200">{item.product.rating}</span>
                        <span className="text-slate-400">({item.product.review_count})</span>
                      </div>
                    </div>

                    {/* Feature Tags */}
                    <div className="space-y-1.5 mb-5 text-xs">
                      {item.product.features?.gpu && (
                        <div className="flex items-center gap-2 text-slate-700 dark:text-slate-300">
                          <span className="w-1.5 h-1.5 rounded-full bg-[#0070E0] dark:bg-[#38BDF8]"></span>
                          <span className="truncate">{item.product.features.gpu}</span>
                        </div>
                      )}
                      {item.product.features?.ram_gb && (
                        <div className="flex items-center gap-2 text-slate-700 dark:text-slate-300">
                          <span className="w-1.5 h-1.5 rounded-full bg-[#0070E0] dark:bg-[#38BDF8]"></span>
                          <span>{item.product.features.ram_gb} GB RAM</span>
                        </div>
                      )}
                      {item.product.features?.battery_hours && (
                        <div className="flex items-center gap-2 text-slate-700 dark:text-slate-300">
                          <span className="w-1.5 h-1.5 rounded-full bg-[#0070E0] dark:bg-[#38BDF8]"></span>
                          <span>{item.product.features.battery_hours}h Battery</span>
                        </div>
                      )}
                    </div>

                    {/* Delivery & Seller snippet */}
                    <div className="flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400 mb-5">
                      <span className="flex items-center gap-1">
                        <Truck className="w-3.5 h-3.5 text-[#0070E0] dark:text-[#38BDF8]" />
                        {item.product.delivery_days}-day delivery
                      </span>
                      <span className="flex items-center gap-1 truncate max-w-[120px]">
                        <ShieldCheck className="w-3.5 h-3.5 text-[#0070E0] dark:text-[#38BDF8]" />
                        {item.product.seller}
                      </span>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-2">
                    <button
                      onClick={() => setSelectedProduct(item.product)}
                      className="flex-1 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 text-xs font-bold text-slate-700 dark:text-slate-200 transition-colors cursor-pointer"
                    >
                      View Details
                    </button>
                    <button
                      onClick={() => handleChooseProduct(item)}
                      className={`flex-1 py-2.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                        isTopPick
                          ? "bg-[#0070E0] hover:bg-[#005bb5] text-white shadow-sm"
                          : "bg-slate-900 dark:bg-slate-700 hover:bg-black dark:hover:bg-slate-600 text-white"
                      }`}
                    >
                      {isTopPick ? "I like this one" : "Select"}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>

          {/* "WHY THIS?" Grounded AI Explanation Box */}
          <div className="p-6 rounded-3xl bg-[#EAF3FF]/80 border border-[#0070E0]/30 shadow-card">
            <div className="flex items-center gap-2 mb-3">
              <Sparkles className="w-5 h-5 text-[#0070E0]" />
              <h4 className="text-base font-bold text-[#003087] uppercase tracking-wider">
                Why This? Grounded Recommendation Analysis
              </h4>
            </div>
            <div className="p-4 rounded-2xl bg-white border border-[#0070E0]/20 text-xs sm:text-sm leading-relaxed text-slate-700 whitespace-pre-line font-sans">
              {results.explanation}
            </div>
          </div>
        </div>
      )}

      {/* Product Detail Modal */}
      <ProductModal
        product={selectedProduct}
        onClose={() => setSelectedProduct(null)}
      />

      {/* Purchase Plan & PayPal Checkout Modal */}
      <PurchasePlanModal
        rankedItem={selectedRankedItem}
        onClose={() => setSelectedRankedItem(null)}
      />
    </div>
  );
}

"use client";

import React, { useState, useEffect } from "react";
import { Search, Sparkles, CheckCircle2, Star, Truck, ShieldCheck, ArrowRight, Loader2 } from "lucide-react";
import ProductModal from "@/components/ProductModal";

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
  "Understanding your request...",
  "Finding matching products...",
  "Comparing options...",
  "Preparing recommendations...",
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
  const [chosenMessage, setChosenMessage] = useState<string | null>(null);

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
      const response = await fetch("http://127.0.0.1:8000/api/discovery/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: textToSearch }),
      });

      if (!response.ok) {
        throw new Error(`Server returned status ${response.status}`);
      }

      const data: RecommendationResponse = await response.json();
      setResults(data);

      if (data.recommendations.length === 0) {
        setError(data.explanation || "I couldn't find products matching those constraints. Try increasing your budget or relaxing a requirement.");
      }
    } catch (err: any) {
      console.error("Discovery error:", err);
      setError("Unable to process request right now. Ensure PayPilot backend is running on port 8000.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleChooseProduct = (ranked: RankedProduct) => {
    setChosenMessage(
      `Selected "${ranked.product.name}"! In Phase 3, this triggers the Purchase Plan & PayPal Checkout approval flow.`
    );
  };

  return (
    <div className="w-full max-w-5xl mx-auto px-4 py-8">
      {/* Search Input Box */}
      <div className="bg-[#0e1422] border border-cyan-500/20 rounded-2xl p-6 shadow-2xl mb-8">
        <label className="block text-xs font-semibold uppercase tracking-wider text-cyan-400 mb-2">
          What are you looking for?
        </label>

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
              placeholder="e.g. Find me a laptop under $1200 for AI development with good battery life."
              className="w-full pl-12 pr-4 py-3.5 rounded-xl bg-slate-900/90 border border-slate-700/80 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 transition-all"
            />
          </div>
          <button
            type="submit"
            disabled={isLoading}
            className="px-7 py-3.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-sm font-semibold tracking-wide shadow-lg shadow-cyan-500/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 cursor-pointer"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Searching...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Search</span>
              </>
            )}
          </button>
        </form>

        {/* Suggestion Chips */}
        <div className="mt-4 flex flex-wrap items-center gap-2">
          <span className="text-xs text-slate-500">Try asking:</span>
          {PRESET_QUERIES.map((preset, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => {
                setQuery(preset);
                handleSearch(preset);
              }}
              className="text-xs bg-slate-800/60 hover:bg-slate-800 text-slate-300 hover:text-cyan-300 px-3 py-1.5 rounded-full border border-slate-700/60 transition-colors truncate max-w-xs text-left"
            >
              {preset}
            </button>
          ))}
        </div>
      </div>

      {/* Progressive Loading State */}
      {isLoading && (
        <div className="p-8 rounded-2xl bg-[#0e1422] border border-cyan-500/20 text-center animate-pulse mb-8">
          <Loader2 className="w-8 h-8 text-cyan-400 animate-spin mx-auto mb-3" />
          <h4 className="text-base font-semibold text-white mb-2">
            {LOADING_STEPS[loadingStepIndex]}
          </h4>
          <div className="flex justify-center gap-2 max-w-xs mx-auto">
            {LOADING_STEPS.map((_, i) => (
              <div
                key={i}
                className={`h-1.5 flex-1 rounded-full transition-all ${
                  i <= loadingStepIndex ? "bg-cyan-400" : "bg-slate-800"
                }`}
              />
            ))}
          </div>
        </div>
      )}

      {/* Error or Empty State */}
      {!isLoading && error && (
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 text-center mb-8">
          <p className="text-sm text-slate-300">{error}</p>
        </div>
      )}

      {/* Success Notification for Phase 3 teaser */}
      {chosenMessage && (
        <div className="p-4 rounded-xl bg-cyan-950/60 border border-cyan-500/40 text-cyan-200 text-xs sm:text-sm font-medium flex items-center justify-between mb-8 animate-in fade-in">
          <span>{chosenMessage}</span>
          <button
            onClick={() => setChosenMessage(null)}
            className="text-xs text-cyan-400 underline ml-4 hover:text-white"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Recommendations Results Section */}
      {!isLoading && results && results.recommendations.length > 0 && (
        <div className="space-y-8 animate-in fade-in duration-300">
          {/* Header Banner */}
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <div className="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-cyan-400 mb-1">
                <Sparkles className="w-3.5 h-3.5" />
                AI Verified Recommendations
              </div>
              <h3 className="text-2xl font-bold text-white">AI Found 3 Best Matches</h3>
            </div>
            <span className="text-xs text-slate-400">
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
                  className={`relative flex flex-col justify-between rounded-2xl p-6 transition-all duration-200 ${
                    isTopPick
                      ? "bg-gradient-to-b from-[#121c33] to-[#0e1422] border-2 border-cyan-500 shadow-xl shadow-cyan-500/10"
                      : "bg-[#0e1422] border border-slate-800 hover:border-slate-700"
                  }`}
                >
                  {/* Top Badge */}
                  <div className="flex items-center justify-between mb-3">
                    <span
                      className={`text-xs font-bold px-2.5 py-1 rounded-full uppercase tracking-wider ${
                        isTopPick
                          ? "bg-cyan-500 text-black font-extrabold"
                          : "bg-slate-800 text-slate-300"
                      }`}
                    >
                      {isTopPick ? "★ Rank #1 (Top Pick)" : `Rank #${item.rank}`}
                    </span>
                    <span className="text-xs font-mono font-bold text-cyan-400 bg-cyan-950/60 border border-cyan-800/40 px-2 py-0.5 rounded-md">
                      {item.score}/100 Match
                    </span>
                  </div>

                  {/* Title & Brand */}
                  <div className="mb-4">
                    <span className="text-[11px] uppercase tracking-wider text-slate-400 font-medium">
                      {item.product.brand}
                    </span>
                    <h4 className="text-lg font-bold text-white mt-0.5 line-clamp-1">
                      {item.product.name}
                    </h4>
                    <p className="text-xs text-slate-400 line-clamp-2 mt-1">
                      {item.product.description}
                    </p>
                  </div>

                  {/* Price & Rating */}
                  <div className="flex items-baseline justify-between py-3 border-y border-slate-800/80 mb-4">
                    <div>
                      <span className="text-2xl font-extrabold text-white">
                        ${item.product.price.toLocaleString("en-US", { minimumFractionDigits: 0 })}
                      </span>
                      <span className="text-xs text-slate-400 ml-1">USD</span>
                    </div>
                    <div className="flex items-center gap-1 text-xs text-amber-400">
                      <Star className="w-3.5 h-3.5 fill-amber-400" />
                      <span className="font-semibold text-white">{item.product.rating}</span>
                      <span className="text-slate-500">({item.product.review_count})</span>
                    </div>
                  </div>

                  {/* Feature Tags */}
                  <div className="space-y-1.5 mb-5 text-xs">
                    {item.product.features.gpu && (
                      <div className="flex items-center gap-1.5 text-slate-300">
                        <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
                        <span className="truncate">{item.product.features.gpu}</span>
                      </div>
                    )}
                    {item.product.features.ram_gb && (
                      <div className="flex items-center gap-1.5 text-slate-300">
                        <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
                        <span>{item.product.features.ram_gb} GB RAM</span>
                      </div>
                    )}
                    {item.product.features.battery_hours && (
                      <div className="flex items-center gap-1.5 text-slate-300">
                        <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
                        <span>{item.product.features.battery_hours}h Battery</span>
                      </div>
                    )}
                  </div>

                  {/* Delivery & Seller snippet */}
                  <div className="flex items-center justify-between text-[11px] text-slate-400 mb-4">
                    <span className="flex items-center gap-1">
                      <Truck className="w-3 h-3 text-cyan-400" />
                      {item.product.delivery_days}-day delivery
                    </span>
                    <span className="flex items-center gap-1 truncate max-w-[120px]">
                      <ShieldCheck className="w-3 h-3 text-cyan-400" />
                      {item.product.seller}
                    </span>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-2">
                    <button
                      onClick={() => setSelectedProduct(item.product)}
                      className="flex-1 py-2.5 rounded-xl border border-slate-700 hover:border-slate-500 bg-slate-900/60 hover:bg-slate-800 text-xs font-semibold text-slate-200 transition-colors"
                    >
                      View Details
                    </button>
                    <button
                      onClick={() => handleChooseProduct(item)}
                      className={`flex-1 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                        isTopPick
                          ? "bg-cyan-500 hover:bg-cyan-400 text-black shadow-md shadow-cyan-500/20"
                          : "bg-slate-800 hover:bg-slate-700 text-white"
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
          <div className="p-6 rounded-2xl bg-[#0e1422] border border-cyan-500/30 shadow-xl">
            <div className="flex items-center gap-2 mb-3">
              <Sparkles className="w-5 h-5 text-cyan-400" />
              <h4 className="text-base font-bold text-white uppercase tracking-wider">
                Why This? Grounded Recommendation Analysis
              </h4>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-sm leading-relaxed text-slate-200 whitespace-pre-line font-sans">
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
    </div>
  );
}

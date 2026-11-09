"use client";

import React from "react";
import { Award, Zap, ShieldCheck, Star } from "lucide-react";

interface RecommendationScorecardProps {
  topProduct?: {
    name: string;
    brand: string;
    price: number;
    rating: number;
    score: number;
    specs?: Record<string, any>;
  };
}

export default function RecommendationScorecard({ topProduct }: RecommendationScorecardProps) {
  const product = topProduct || {
    name: "NovaBook Pro 14",
    brand: "Nova",
    price: 1049.0,
    rating: 4.7,
    score: 94.0,
    specs: { cpu: "Intel Core Ultra 7", ram: "16GB", storage: "512GB SSD" },
  };

  const factors = [
    { label: "Hardware Performance", score: 96, icon: Zap, color: "text-amber-400" },
    { label: "Value-for-Money Index", score: 92, icon: Award, color: "text-cyan-400" },
    { label: "Merchant Trust & Shipping", score: 95, icon: ShieldCheck, color: "text-emerald-400" },
    { label: "Verified Buyer Rating", score: Math.round(product.rating * 20), icon: Star, color: "text-yellow-400" },
  ];

  return (
    <div className="p-5 rounded-2xl bg-gradient-to-br from-slate-900/90 via-slate-900/60 to-slate-950/90 border border-cyan-500/30 shadow-xl relative overflow-hidden">
      <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-500/10 rounded-full blur-2xl pointer-events-none" />

      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
            <Award className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">AI Recommendation Scorecard</h3>
            <p className="text-[11px] text-slate-400">Algorithmic Multi-Factor Ranking</p>
          </div>
        </div>
        <div className="px-2.5 py-1 rounded-full bg-cyan-950/80 border border-cyan-500/40 text-cyan-300 font-bold text-xs flex items-center gap-1">
          <span>{product.score.toFixed(1)}</span>
          <span className="text-[10px] text-cyan-400/70 font-normal">/ 100</span>
        </div>
      </div>

      <div className="p-3.5 rounded-xl bg-slate-800/40 border border-slate-700/60 mb-4">
        <div className="flex justify-between items-start mb-1">
          <div>
            <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-wider">{product.brand}</span>
            <h4 className="text-sm font-bold text-white">{product.name}</h4>
          </div>
          <span className="text-sm font-extrabold text-emerald-400">${product.price.toFixed(2)}</span>
        </div>
        {product.specs && (
          <div className="flex flex-wrap gap-1.5 mt-2">
            {Object.entries(product.specs).map(([k, v]) => (
              <span key={k} className="text-[10px] bg-slate-900/80 px-2 py-0.5 rounded text-slate-300 border border-slate-700/40">
                {String(v)}
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="space-y-2.5">
        {factors.map((f) => {
          const Icon = f.icon;
          return (
            <div key={f.label} className="space-y-1">
              <div className="flex justify-between text-xs">
                <span className="flex items-center gap-1.5 text-slate-300">
                  <Icon className={`w-3.5 h-3.5 ${f.color}`} />
                  {f.label}
                </span>
                <span className="font-semibold text-white">{f.score}%</span>
              </div>
              <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                <div style={{ width: `${f.score}%` }} className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full" />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}


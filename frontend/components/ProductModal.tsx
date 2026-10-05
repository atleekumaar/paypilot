"use client";

import React from "react";
import { X, CheckCircle, ShieldCheck, Truck, Star, Cpu, Battery, HardDrive } from "lucide-react";

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

interface ProductModalProps {
  product: Product | null;
  onClose: () => void;
}

export default function ProductModal({ product, onClose }: ProductModalProps) {
  if (!product) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="relative w-full max-w-2xl bg-[#0e1422] border border-cyan-500/20 rounded-2xl shadow-2xl p-6 overflow-hidden">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/80 transition-colors"
          aria-label="Close modal"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="flex items-start gap-4 mb-4">
          <div className="w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 font-bold text-lg">
            {product.brand.substring(0, 2).toUpperCase()}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs uppercase tracking-wider text-cyan-400 font-medium">
                {product.brand} &bull; {product.category}
              </span>
              {product.stock ? (
                <span className="inline-flex items-center gap-1 text-[11px] text-emerald-400 font-medium bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                  <CheckCircle className="w-3 h-3" /> In Stock
                </span>
              ) : (
                <span className="text-[11px] text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded-full border border-rose-500/20">
                  Out of Stock
                </span>
              )}
            </div>
            <h3 className="text-xl font-bold text-white mt-1">{product.name}</h3>
            <p className="text-xs text-slate-400">SKU: {product.id}</p>
          </div>
        </div>

        {/* Price & Rating Banner */}
        <div className="flex items-center justify-between p-4 rounded-xl bg-slate-900/60 border border-slate-800 mb-5">
          <div>
            <span className="text-xs text-slate-400">Selling Price</span>
            <div className="text-2xl font-extrabold text-cyan-400">
              ${product.price.toLocaleString("en-US", { minimumFractionDigits: 2 })}
              <span className="text-xs font-normal text-slate-400 ml-1">{product.currency}</span>
            </div>
          </div>
          <div className="text-right">
            <div className="flex items-center gap-1 text-amber-400 justify-end">
              <Star className="w-4 h-4 fill-amber-400" />
              <span className="font-semibold text-white">{product.rating}</span>
            </div>
            <span className="text-xs text-slate-400">({product.review_count.toLocaleString()} reviews)</span>
          </div>
        </div>

        {/* Description */}
        <div className="mb-5">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">Description</h4>
          <p className="text-sm text-slate-300 leading-relaxed">{product.description}</p>
        </div>

        {/* Specifications Grid */}
        <div className="mb-5">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Technical Specifications</h4>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
            {Object.entries(product.features).map(([key, val]) => (
              <div key={key} className="p-2.5 rounded-lg bg-slate-900/40 border border-slate-800/80">
                <div className="text-[11px] uppercase tracking-wider text-slate-400">
                  {key.replace(/_/g, " ")}
                </div>
                <div className="text-xs font-semibold text-slate-200 mt-0.5 truncate">
                  {typeof val === "boolean" ? (val ? "Yes" : "No") : String(val)}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Trust Badges */}
        <div className="flex items-center justify-between pt-4 border-t border-slate-800 text-xs text-slate-400">
          <div className="flex items-center gap-1.5">
            <Truck className="w-4 h-4 text-cyan-400" />
            <span>Delivers in {product.delivery_days} days</span>
          </div>
          <div className="flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-cyan-400" />
            <span>Fulfilled by {product.seller}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

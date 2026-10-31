"use client";

import React from "react";
import { X, CheckCircle, ShieldCheck, Truck, Star } from "lucide-react";

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
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-150 text-left">
      <div className="relative w-full max-w-2xl bg-white border border-slate-200 rounded-3xl shadow-modal p-6 sm:p-7 overflow-hidden">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-full text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
          aria-label="Close modal"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="flex items-start gap-4 mb-4 pr-8">
          <div className="w-12 h-12 rounded-2xl bg-[#EAF3FF] border border-[#0070E0]/20 flex items-center justify-center text-[#0070E0] font-black text-base shrink-0">
            {product.brand.substring(0, 2).toUpperCase()}
          </div>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[11px] uppercase tracking-wider text-[#0070E0] font-bold">
                {product.brand} &bull; {product.category}
              </span>
              {product.stock ? (
                <span className="inline-flex items-center gap-1 text-[11px] text-emerald-700 font-semibold bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                  <CheckCircle className="w-3 h-3 text-emerald-600" /> In Stock
                </span>
              ) : (
                <span className="text-[11px] text-rose-700 bg-rose-50 px-2 py-0.5 rounded-full border border-rose-200 font-semibold">
                  Out of Stock
                </span>
              )}
            </div>
            <h3 className="text-xl font-bold text-[#14213D] leading-snug">
              {product.name}
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">SKU: {product.id}</p>
          </div>
        </div>

        {/* Price & Rating Banner */}
        <div className="flex items-center justify-between p-4 rounded-2xl bg-[#F5F8FC] border border-slate-200/80 mb-5">
          <div>
            <span className="text-xs font-medium text-slate-500">Verified Price</span>
            <div className="text-2xl font-black text-[#003087] font-mono">
              ${product.price.toLocaleString("en-US", { minimumFractionDigits: 2 })}
              <span className="text-xs font-normal text-slate-500 font-sans ml-1">
                {product.currency}
              </span>
            </div>
          </div>
          <div className="text-right">
            <div className="flex items-center gap-1 text-amber-500 justify-end">
              <Star className="w-4 h-4 fill-amber-400" />
              <span className="font-bold text-slate-800 text-sm">{product.rating}</span>
            </div>
            <span className="text-xs text-slate-500">
              ({product.review_count.toLocaleString()} customer reviews)
            </span>
          </div>
        </div>

        {/* Description */}
        <div className="mb-5">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5">
            Product Summary
          </h4>
          <p className="text-xs sm:text-sm text-slate-700 leading-relaxed">
            {product.description}
          </p>
        </div>

        {/* Specifications Grid */}
        <div className="mb-5">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
            Technical Specifications
          </h4>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
            {Object.entries(product.features).map(([key, val]) => (
              <div
                key={key}
                className="p-2.5 rounded-xl bg-[#F5F8FC] border border-slate-200/60"
              >
                <div className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">
                  {key.replace(/_/g, " ")}
                </div>
                <div className="text-xs font-bold text-slate-800 mt-0.5 truncate">
                  {typeof val === "boolean" ? (val ? "Yes" : "No") : String(val)}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Trust Badges */}
        <div className="flex items-center justify-between pt-4 border-t border-slate-100 text-xs text-slate-500">
          <div className="flex items-center gap-1.5">
            <Truck className="w-4 h-4 text-[#0070E0]" />
            <span>Delivers in {product.delivery_days} business days</span>
          </div>
          <div className="flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-[#0070E0]" />
            <span>Fulfilled by {product.seller}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

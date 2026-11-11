"use client";

import React, { useState, useMemo, useRef, useEffect } from "react";
import { AgGridReact } from "ag-grid-react";
import { ColDef, ModuleRegistry, AllCommunityModule } from "ag-grid-community";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-quartz.css";
import { Search, SlidersHorizontal, Info, Check, X, Eye } from "lucide-react";

// Register AG Grid Community modules
ModuleRegistry.registerModules([AllCommunityModule]);

export interface ProductItem {
  id: string;
  name: string;
  brand: string;
  price: number;
  currency: string;
  category: string;
  in_stock: boolean;
  rating: number;
  review_count: number;
  seller: string;
  specs: Record<string, any>;
  recommendation_score: number;
}

interface ProductIntelligenceGridProps {
  products: ProductItem[];
  loading: boolean;
  selectedCategory: string | null;
  onSelectProduct?: (product: ProductItem) => void;
}

export default function ProductIntelligenceGrid({
  products,
  loading,
  selectedCategory,
  onSelectProduct,
}: ProductIntelligenceGridProps) {
  const [quickFilter, setQuickFilter] = useState("");
  const [drillDownProduct, setDrillDownProduct] = useState<ProductItem | null>(null);
  const gridRef = useRef<AgGridReact>(null);

  const filteredData = useMemo(() => {
    if (!selectedCategory) return products;
    return products.filter(
      (p) => p.category.toLowerCase() === selectedCategory.toLowerCase()
    );
  }, [products, selectedCategory]);

  const columnDefs = useMemo<ColDef<ProductItem>[]>(() => [
    {
      field: "name",
      headerName: "Product Name",
      flex: 2,
      minWidth: 220,
      filter: true,
      cellRenderer: (params: any) => (
        <div className="flex items-center gap-2 py-1">
          <span className="font-semibold text-[#14213D] dark:text-white truncate">{params.value}</span>
        </div>
      ),
    },
    {
      field: "brand",
      headerName: "Brand",
      width: 120,
      filter: true,
      cellRenderer: (params: any) => (
        <span className="text-cyan-600 dark:text-cyan-400 font-medium">{params.value}</span>
      ),
    },
    {
      field: "price",
      headerName: "Price",
      width: 120,
      filter: "agNumberColumnFilter",
      cellRenderer: (params: any) => (
        <span className="font-bold text-emerald-600 dark:text-emerald-400">
          ${Number(params.value).toFixed(2)}
        </span>
      ),
    },
    {
      field: "category",
      headerName: "Category",
      width: 130,
      filter: true,
      cellRenderer: (params: any) => (
        <span className="px-2 py-0.5 rounded text-[11px] bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
          {params.value}
        </span>
      ),
    },
    {
      field: "recommendation_score",
      headerName: "AI Score",
      width: 120,
      filter: "agNumberColumnFilter",
      cellRenderer: (params: any) => {
        const score = Number(params.value);
        const color = score >= 90 ? "text-emerald-400 bg-emerald-950/60 border-emerald-500/40" : "text-cyan-400 bg-cyan-950/60 border-cyan-500/40";
        return (
          <span className={`px-2 py-0.5 rounded-full text-xs font-bold border ${color}`}>
            {score.toFixed(1)}
          </span>
        );
      },
    },
    {
      field: "in_stock",
      headerName: "Status",
      width: 120,
      cellRenderer: (params: any) => (
        params.value ? (
          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-400">
            <Check className="w-3 h-3" /> In Stock
          </span>
        ) : (
          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-rose-400">
            <X className="w-3 h-3" /> Sold Out
          </span>
        )
      ),
    },
    {
      field: "seller",
      headerName: "Seller",
      width: 150,
      filter: true,
      cellRenderer: (params: any) => (
        <span className="text-slate-400 text-xs">{params.value}</span>
      ),
    },
    {
      headerName: "Action",
      width: 110,
      cellRenderer: (params: any) => (
        <button
          onClick={() => setDrillDownProduct(params.data)}
          className="flex items-center gap-1 px-2.5 py-1 text-xs font-medium text-cyan-300 bg-cyan-950/50 hover:bg-cyan-900/60 border border-cyan-800/60 rounded-lg transition-colors"
        >
          <Eye className="w-3 h-3" /> Inspect
        </button>
      ),
    },
  ], []);

  const defaultColDef = useMemo<ColDef>(() => ({
    sortable: true,
    resizable: true,
  }), []);

  return (
    <div className="p-6 rounded-2xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800/80 backdrop-blur-sm shadow-sm dark:shadow-xl flex flex-col gap-4 transition-colors">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-bold text-[#14213D] dark:text-white tracking-wide">Product Intelligence Grid</h3>
            <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded bg-cyan-50 dark:bg-cyan-950/80 text-cyan-700 dark:text-cyan-400 border border-cyan-200 dark:border-cyan-800/60">
              AG Grid Powered
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Verified commerce catalogue with hardware specifications, AI scoring, and live inventory.
          </p>
        </div>

        <div className="flex items-center gap-2.5 w-full sm:w-auto">
          <div className="relative flex-1 sm:w-64">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search products, brands, specs..."
              value={quickFilter}
              onChange={(e) => setQuickFilter(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/80 rounded-xl text-xs text-[#14213D] dark:text-white placeholder-slate-400 focus:outline-none focus:border-cyan-500 transition-colors"
            />
          </div>
        </div>
      </div>

      {/* Grid container with modern quartz theme */}
      <div className="ag-theme-quartz w-full h-[400px] rounded-xl overflow-hidden border border-slate-200 dark:border-slate-800 shadow-inner">
        <AgGridReact
          ref={gridRef}
          rowData={filteredData}
          columnDefs={columnDefs}
          defaultColDef={defaultColDef}
          quickFilterText={quickFilter}
          pagination={true}
          paginationPageSize={10}
          paginationPageSizeSelector={[10, 25, 50]}
          rowSelection={{ mode: "singleRow" }}
          onRowClicked={(event) => {
            if (event.data && onSelectProduct) {
              onSelectProduct(event.data);
            }
          }}
          loading={loading}
        />
      </div>

      {/* Product Drill-Down Modal */}
      {drillDownProduct && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="w-full max-w-lg bg-slate-900 border border-slate-700 rounded-2xl p-6 shadow-2xl relative">
            <button
              onClick={() => setDrillDownProduct(null)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white p-1 rounded-lg bg-slate-800"
            >
              <X className="w-4 h-4" />
            </button>

            <div className="mb-4">
              <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider">{drillDownProduct.brand}</span>
              <h3 className="text-lg font-bold text-white mt-1">{drillDownProduct.name}</h3>
              <div className="flex items-center gap-3 mt-2">
                <span className="text-xl font-extrabold text-emerald-400">${drillDownProduct.price.toFixed(2)}</span>
                <span className="px-2 py-0.5 rounded text-xs bg-slate-800 text-slate-300 border border-slate-700">
                  {drillDownProduct.category}
                </span>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-cyan-950 text-cyan-300 border border-cyan-800">
                  Score: {drillDownProduct.recommendation_score.toFixed(1)} / 100
                </span>
              </div>
            </div>

            <div className="space-y-3 mb-6">
              <h4 className="text-xs font-semibold uppercase text-slate-400 tracking-wider">Specifications & Features</h4>
              <div className="grid grid-cols-2 gap-2 text-xs">
                {Object.entries(drillDownProduct.specs || {}).map(([key, val]) => (
                  <div key={key} className="p-2.5 rounded-xl bg-slate-800/60 border border-slate-700/60">
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">{key.replace(/_/g, " ")}</span>
                    <span className="font-medium text-white">{String(val)}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex items-center justify-between pt-3 border-t border-slate-800 text-xs text-slate-400">
              <span>Merchant: <strong className="text-slate-200">{drillDownProduct.seller}</strong></span>
              <button
                onClick={() => setDrillDownProduct(null)}
                className="px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-medium shadow-lg shadow-cyan-600/30"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}


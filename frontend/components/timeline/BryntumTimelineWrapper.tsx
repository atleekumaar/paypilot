"use client";

import dynamic from "next/dynamic";
import React from "react";
import { RefreshCw } from "lucide-react";

const DynamicBryntumScheduler = dynamic(
  () => import("./BryntumCommerceScheduler"),
  {
    ssr: false,
    loading: () => (
      <div className="flex flex-col items-center justify-center min-h-[450px] p-12 text-center rounded-xl border border-slate-800 bg-[#0b1120]">
        <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin mb-3" />
        <h3 className="text-sm font-semibold text-white">Loading Bryntum Commerce Timeline</h3>
        <p className="text-xs text-slate-400 mt-1 max-w-sm">
          Initializing SSR-safe scheduler tracks, milestone data engine, and Astropods telemetry...
        </p>
      </div>
    ),
  }
);

export default function BryntumTimelineWrapper() {
  return <DynamicBryntumScheduler />;
}


"use client";

import React from "react";
import Navbar from "@/components/Navbar";
import BryntumTimelineWrapper from "@/components/timeline/BryntumTimelineWrapper";

export default function TimelinePage() {
  return (
    <div className="min-h-screen bg-[#F5F8FC]/50 dark:bg-[#070b14] text-[#14213D] dark:text-slate-100 flex flex-col font-sans transition-colors duration-200">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <BryntumTimelineWrapper />
      </main>

      <footer className="w-full border-t border-slate-200 dark:border-slate-800/80 bg-white dark:bg-[#090d16] py-6 mt-12 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>PayPilot © 2026 • AI-Powered Autonomous Commerce Platform</span>
          <div className="flex items-center gap-4 text-slate-500 dark:text-slate-400">
            <span>Powered by <strong>Bryntum</strong> & <strong>Astropods</strong></span>
            <span>•</span>
            <span>PayPal Sandbox Verified</span>
          </div>
        </div>
      </footer>
    </div>
  );
}


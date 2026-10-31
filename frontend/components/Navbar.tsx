"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Package,
  Bell,
  Menu,
  X,
  ExternalLink,
  Sparkles,
} from "lucide-react";

export default function Navbar() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isHome = pathname === "/";

  return (
    <header className="w-full border-b border-slate-100 bg-white/95 backdrop-blur-md sticky top-0 z-50 transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-18 py-3.5 flex items-center justify-between">
        {/* Brand Logo */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-[#003087] via-[#0070E0] to-[#0094FF] flex items-center justify-center font-black text-white text-base shadow-sm group-hover:scale-105 transition-transform">
            <span className="tracking-tighter font-extrabold italic">P</span>
          </div>
          <div className="flex items-baseline gap-1.5">
            <span className="font-extrabold text-xl tracking-tight text-[#14213D]">
              Pay<span className="text-[#0070E0]">Pilot</span>
            </span>
          </div>
        </Link>

        {/* Desktop Navigation Links */}
        <nav className="hidden lg:flex items-center gap-1 xl:gap-2">
          <Link
            href="/"
            className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all ${
              isHome
                ? "bg-[#EAF3FF] text-[#0070E0]"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
            }`}
          >
            Home
          </Link>
          <a
            href={isHome ? "#features" : "/#features"}
            className="px-3.5 py-1.5 rounded-full text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition-all"
          >
            Features
          </a>
          <a
            href={isHome ? "#how-it-works" : "/#how-it-works"}
            className="px-3.5 py-1.5 rounded-full text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition-all"
          >
            How it Works
          </a>
          <a
            href={isHome ? "#demo" : "/#demo"}
            className="px-3.5 py-1.5 rounded-full text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition-all"
          >
            Demo
          </a>
          <a
            href={isHome ? "#docs" : "/#docs"}
            className="px-3.5 py-1.5 rounded-full text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition-all"
          >
            Docs
          </a>
          <div className="h-4 w-px bg-slate-200 mx-1" />
          <Link
            href="/orders"
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
              pathname.startsWith("/orders")
                ? "bg-[#EAF3FF] text-[#0070E0] font-semibold"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
            }`}
          >
            <Package className="w-3.5 h-3.5" />
            <span>Orders</span>
          </Link>
          <Link
            href="/notifications"
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
              pathname.startsWith("/notifications")
                ? "bg-[#EAF3FF] text-[#0070E0] font-semibold"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
            }`}
          >
            <Bell className="w-3.5 h-3.5" />
            <span>Notifications</span>
          </Link>
        </nav>

        {/* Right Action Area */}
        <div className="hidden sm:flex items-center gap-3">
          {/* GitHub icon link */}
          <a
            href="https://github.com/atleekumaar/paypilot"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="GitHub Repository"
            className="p-2 text-slate-600 hover:text-slate-900 hover:bg-slate-50 rounded-full transition-colors"
          >
            <svg
              className="w-5 h-5 fill-current"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                fillRule="evenodd"
                clipRule="evenodd"
                d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
              />
            </svg>
          </a>

          {/* Primary CTA Button */}
          <Link
            href={isHome ? "#assistant" : "/#assistant"}
            className="inline-flex items-center gap-1.5 px-5 py-2.5 rounded-full bg-[#0070E0] hover:bg-[#005bb5] text-white text-xs sm:text-sm font-semibold tracking-tight shadow-sm hover:shadow transition-all"
          >
            <span>Try PayPilot</span>
            <span className="text-sm">→</span>
          </Link>
        </div>

        {/* Mobile menu button */}
        <div className="flex lg:hidden items-center gap-2">
          <Link
            href={isHome ? "#assistant" : "/#assistant"}
            className="sm:hidden px-3.5 py-1.5 rounded-full bg-[#0070E0] text-white text-xs font-semibold"
          >
            Try PayPilot
          </Link>
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 text-slate-600 hover:text-slate-900 rounded-lg hover:bg-slate-100 transition-colors"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile dropdown menu */}
      {mobileMenuOpen && (
        <div className="lg:hidden border-t border-slate-100 bg-white px-4 pt-3 pb-5 space-y-2 animate-in slide-in-from-top-2 duration-150">
          <Link
            href="/"
            onClick={() => setMobileMenuOpen(false)}
            className={`block px-3 py-2 rounded-lg text-sm font-medium ${
              isHome ? "bg-[#EAF3FF] text-[#0070E0] font-semibold" : "text-slate-700 hover:bg-slate-50"
            }`}
          >
            Home
          </Link>
          <a
            href={isHome ? "#features" : "/#features"}
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            Features
          </a>
          <a
            href={isHome ? "#how-it-works" : "/#how-it-works"}
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            How it Works
          </a>
          <a
            href={isHome ? "#demo" : "/#demo"}
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            Demo
          </a>
          <a
            href={isHome ? "#docs" : "/#docs"}
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            Documentation
          </a>
          <div className="border-t border-slate-100 my-2 pt-2 space-y-1">
            <Link
              href="/orders"
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              <Package className="w-4 h-4 text-[#0070E0]" />
              <span>Orders & Tracking</span>
            </Link>
            <Link
              href="/notifications"
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              <Bell className="w-4 h-4 text-[#0070E0]" />
              <span>Notifications</span>
            </Link>
            <a
              href="https://github.com/atleekumaar/paypilot"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              <ExternalLink className="w-4 h-4 text-slate-400" />
              <span>GitHub Repository</span>
            </a>
          </div>
        </div>
      )}
    </header>
  );
}

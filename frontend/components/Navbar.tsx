"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Bot, Package, Bell, Compass, Home } from "lucide-react";

export default function Navbar() {
  const pathname = usePathname();

  const navItems = [
    { label: "Home", href: "/", icon: Home },
    { label: "Orders", href: "/orders", icon: Package },
    { label: "Notifications", href: "/notifications", icon: Bell },
  ];

  return (
    <header className="w-full border-b border-slate-800/80 bg-[#090d16]/90 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        {/* Brand */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center font-bold text-white text-sm shadow-lg shadow-cyan-500/20 group-hover:scale-105 transition-transform">
            P
          </div>
          <span className="font-bold text-lg tracking-wider text-white">PAYPILOT</span>
          <span className="hidden sm:inline-block ml-2 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-cyan-400 bg-cyan-950/60 border border-cyan-800/40 rounded-full">
            Phase 5 Post-Purchase
          </span>
        </Link>

        {/* Navigation Links */}
        <nav className="flex items-center gap-1 sm:gap-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.label}
                href={item.href}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? "bg-cyan-500/10 text-cyan-400 border border-cyan-500/30"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Live Status indicator */}
        <div className="hidden md:flex items-center gap-4 text-xs text-slate-400">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            Post-Purchase Agent Active
          </span>
        </div>
      </div>
    </header>
  );
}

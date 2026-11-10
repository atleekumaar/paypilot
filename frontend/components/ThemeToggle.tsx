"use client";

import React, { useEffect, useState } from "react";
import { Sun, Moon } from "lucide-react";

export default function ThemeToggle({ className = "" }: { className?: string }) {
  const [theme, setTheme] = useState<"light" | "dark">("light");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    // Check initial document state or localStorage or system preference
    const isDark =
      document.documentElement.classList.contains("dark") ||
      localStorage.getItem("paypilot-theme") === "dark" ||
      (!("paypilot-theme" in localStorage) &&
        window.matchMedia("(prefers-color-scheme: dark)").matches);

    if (isDark) {
      document.documentElement.classList.add("dark");
      setTheme("dark");
    } else {
      document.documentElement.classList.remove("dark");
      setTheme("light");
    }
  }, []);

  const toggleTheme = () => {
    if (theme === "light") {
      document.documentElement.classList.add("dark");
      localStorage.setItem("paypilot-theme", "dark");
      setTheme("dark");
      window.dispatchEvent(new CustomEvent("paypilot-theme-change", { detail: { theme: "dark" } }));
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("paypilot-theme", "light");
      setTheme("light");
      window.dispatchEvent(new CustomEvent("paypilot-theme-change", { detail: { theme: "light" } }));
    }
  };

  if (!mounted) {
    return (
      <button
        aria-label="Toggle theme"
        className={`p-2 rounded-full border border-slate-200 dark:border-slate-800 text-slate-400 opacity-60 ${className}`}
        disabled
      >
        <Sun className="w-4 h-4" />
      </button>
    );
  }

  return (
    <button
      type="button"
      onClick={toggleTheme}
      aria-label={theme === "dark" ? "Switch to light theme" : "Switch to dark theme"}
      title={theme === "dark" ? "Switch to light theme" : "Switch to dark theme"}
      className={`relative inline-flex items-center justify-center p-2 rounded-full transition-all duration-200 border cursor-pointer ${
        theme === "dark"
          ? "bg-slate-900 border-slate-800 text-amber-400 hover:text-amber-300 hover:bg-slate-800 shadow-sm"
          : "bg-white border-slate-200 text-slate-700 hover:text-[#0070E0] hover:bg-slate-50 shadow-sm"
      } ${className}`}
    >
      {theme === "dark" ? (
        <Sun className="w-4 h-4 transition-transform duration-300 rotate-0 hover:rotate-45" />
      ) : (
        <Moon className="w-4 h-4 transition-transform duration-300 rotate-0 hover:-rotate-12" />
      )}
    </button>
  );
}


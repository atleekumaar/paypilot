import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#090d16",
        foreground: "#f3f4f6",
        surface: "#111827",
        border: "#1f293d",
        primary: {
          DEFAULT: "#00d2ff",
          hover: "#00b4db",
          glow: "rgba(0, 210, 255, 0.15)",
        },
        accent: {
          DEFAULT: "#38bdf8",
          muted: "#94a3b8",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;

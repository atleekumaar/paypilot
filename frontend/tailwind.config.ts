import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./frontend/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./frontend/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./frontend/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        paypilot: {
          dark: "#003087",      // Deep PayPilot blue
          primary: "#0070E0",   // Bright blue
          hover: "#005bb5",     // Button hover blue
          accent: "#EAF3FF",    // Soft light blue accent
          navy: "#14213D",      // Main text dark navy
          muted: "#64748B",     // Secondary text muted slate
          bg: "#FFFFFF",        // Clean white
          surface: "#F5F8FC",   // Soft cool grey
          border: "#E2E8F0",    // Crisp subtle border
          borderLight: "#F1F5F9",
        },
        primary: {
          DEFAULT: "#0070E0",
          dark: "#003087",
          light: "#EAF3FF",
          hover: "#005bb5",
        },
      },
      fontFamily: {
        sans: [
          "Inter",
          "-apple-system",
          "BlinkMacSystemFont",
          "'Segoe UI'",
          "Roboto",
          "Oxygen",
          "Ubuntu",
          "Cantarell",
          "sans-serif",
        ],
      },
      boxShadow: {
        subtle: "0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.03)",
        card: "0 4px 20px -2px rgba(0, 48, 135, 0.06), 0 2px 6px -1px rgba(0, 0, 0, 0.04)",
        cardHover: "0 10px 25px -3px rgba(0, 48, 135, 0.10), 0 4px 10px -2px rgba(0, 0, 0, 0.04)",
        modal: "0 20px 40px -4px rgba(0, 48, 135, 0.16), 0 8px 16px -4px rgba(0, 0, 0, 0.08)",
      },
    },
  },
  plugins: [],
};

export default config;

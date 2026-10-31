import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PayPilot — AI-Powered Autonomous Commerce Platform",
  description: "Shop smarter with PayPilot. Discover products, compare recommendations, and complete purchases with PayPal trust.",
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased bg-white text-paypilot-navy min-h-screen selection:bg-paypilot-accent selection:text-paypilot-dark">
        {children}
      </body>
    </html>
  );
}

import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PayPilot | Your AI Commerce Agent",
  description: "Discover. Decide. Pay. AI-powered commerce agent built for effortless shopping.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased bg-[#090d16] text-slate-100 min-h-screen selection:bg-cyan-500/30 selection:text-cyan-200">
        {children}
      </body>
    </html>
  );
}

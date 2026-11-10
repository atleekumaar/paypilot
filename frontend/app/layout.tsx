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
    <html lang="en" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              try {
                const stored = localStorage.getItem('paypilot-theme');
                const dark = stored === 'dark' || (!stored && window.matchMedia('(prefers-color-scheme: dark)').matches);
                if (dark) {
                  document.documentElement.classList.add('dark');
                } else {
                  document.documentElement.classList.remove('dark');
                }
              } catch (_) {}
            `,
          }}
        />
      </head>
      <body className="antialiased bg-white dark:bg-[#090D16] text-[#14213D] dark:text-slate-100 min-h-screen selection:bg-[#EAF3FF] selection:text-[#003087] dark:selection:bg-[#0070E0]/30 dark:selection:text-[#38BDF8] transition-colors duration-200">
        {children}
      </body>
    </html>
  );
}

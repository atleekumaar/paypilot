import Navbar from "@/components/Navbar";
import ShoppingWorkspace from "@/components/ShoppingWorkspace";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />

      <main className="flex-1 flex flex-col items-center justify-start px-4">
        {/* Hero Section */}
        <div className="max-w-4xl mx-auto pt-12 pb-4 text-center">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-cyan-500/20 bg-cyan-500/5 text-cyan-400 text-xs font-medium tracking-wide mb-6">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></span>
            PayPal AI Hackathon &bull; Phase 2 Active
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white mb-3">
            PAYPILOT
          </h1>

          <h2 className="text-lg sm:text-xl font-medium text-cyan-400 tracking-wide mb-3">
            Your AI Commerce Agent
          </h2>

          <p className="text-sm sm:text-base text-slate-400 max-w-lg mx-auto font-normal">
            Discover. Decide. Pay. Conversational intelligence for smart shopping.
          </p>
        </div>

        {/* Interactive Discovery Workspace */}
        <ShoppingWorkspace />
      </main>

      <footer className="border-t border-slate-800/80 py-6 text-center text-xs text-slate-500 mt-12">
        <p>PayPilot &copy; 2026 &bull; PayPal AI Hackathon Phase 2: AI Product Discovery Agent</p>
      </footer>
    </div>
  );
}

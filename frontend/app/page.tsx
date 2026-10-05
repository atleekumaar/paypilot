import Navbar from "@/components/Navbar";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />

      <main className="flex-1 flex flex-col items-center justify-center px-6 text-center">
        <div className="max-w-3xl mx-auto py-24 sm:py-32 flex flex-col items-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-cyan-500/20 bg-cyan-500/5 text-cyan-400 text-xs font-medium tracking-wide mb-8">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></span>
            PayPal AI Hackathon
          </div>

          {/* Main Title */}
          <h1 className="text-5xl sm:text-7xl font-extrabold tracking-tight text-white mb-4">
            PAYPILOT
          </h1>

          {/* Subtitle */}
          <h2 className="text-xl sm:text-2xl font-medium text-cyan-400 tracking-wide mb-6">
            Your AI Commerce Agent
          </h2>

          {/* Tagline */}
          <p className="text-base sm:text-lg text-slate-400 max-w-xl mx-auto mb-10 font-normal leading-relaxed">
            Discover. Decide. Pay.
          </p>

          {/* Call to action */}
          <div className="flex flex-col sm:flex-row items-center gap-4">
            <button
              type="button"
              className="px-8 py-3.5 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-medium text-sm tracking-wide shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 hover:brightness-110 transition-all duration-200 cursor-pointer"
            >
              Start Shopping
            </button>
          </div>

          {/* Minimalist prompt preview box */}
          <div className="mt-16 w-full max-w-lg p-4 rounded-xl border border-slate-800 bg-slate-900/50 text-left">
            <div className="text-[11px] font-mono uppercase text-slate-500 mb-1.5">Example Agent Prompt</div>
            <div className="text-sm font-mono text-slate-300">
              &quot;Find me a laptop under $1200 for AI development with good battery life.&quot;
            </div>
          </div>
        </div>
      </main>

      <footer className="border-t border-slate-800/80 py-6 text-center text-xs text-slate-500">
        <p>PayPilot &copy; 2026 &bull; Phase 1 Foundation</p>
      </footer>
    </div>
  );
}

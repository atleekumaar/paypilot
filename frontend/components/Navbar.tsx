export default function Navbar() {
  return (
    <header className="w-full border-b border-slate-800/80 bg-[#090d16]/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center font-bold text-white text-sm shadow-lg shadow-cyan-500/20">
            P
          </div>
          <span className="font-semibold text-lg tracking-wider text-white">PAYPILOT</span>
          <span className="ml-2 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wider text-cyan-400 bg-cyan-950/60 border border-cyan-800/40 rounded-full">
            Phase 1
          </span>
        </div>
        <div className="flex items-center gap-4 text-xs text-slate-400">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            Agent Foundation Ready
          </span>
        </div>
      </div>
    </header>
  );
}

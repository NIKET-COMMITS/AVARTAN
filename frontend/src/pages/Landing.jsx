import React from "react";
import { Link } from "react-router-dom";
import { 
  Leaf, Zap, MapPin, Trophy, 
  ArrowRight, Sparkles, Globe, ShieldCheck, Camera
} from "lucide-react";

const Landing = () => {
  return (
    <div className="min-h-screen bg-[#F4F7F9] text-slate-900 font-sans overflow-hidden selection:bg-emerald-200 flex flex-col items-center">
      
      {/* --- AMBIENT BACKGROUND GLOWS --- */}
      <div className="fixed top-0 w-full max-w-7xl h-full pointer-events-none z-0">
        <div className="absolute top-[-10%] left-[10%] w-[500px] h-[500px] rounded-full bg-emerald-400/20 blur-[100px] animate-pulse"></div>
        <div className="absolute top-[20%] right-[10%] w-[600px] h-[600px] rounded-full bg-teal-400/10 blur-[120px]"></div>
      </div>

      {/* --- FROSTED NAVBAR --- */}
      <nav className="fixed top-0 w-full z-50 bg-white/70 backdrop-blur-xl border-b border-slate-200/50">
        <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-br from-emerald-400 to-emerald-600 p-2.5 rounded-xl shadow-sm">
              <Leaf className="text-white" size={20} />
            </div>
            <span className="text-xl font-black tracking-tight text-slate-900">AVARTAN</span>
          </div>
          <div className="flex items-center gap-6">
            <Link to="/login" className="hidden sm:block text-sm font-bold text-slate-600 hover:text-emerald-600 transition-colors">
              Sign In
            </Link>
            <Link to="/register" className="px-5 py-2.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-sm font-bold transition-all shadow-md active:scale-95 flex items-center gap-2">
              Get Started <ArrowRight size={16} />
            </Link>
          </div>
        </div>
      </nav>

      {/* --- HERO SECTION (THE MAIN ATTRACTION) --- */}
      <header className="relative z-10 pt-36 pb-20 px-6 w-full max-w-4xl mx-auto text-center flex flex-col items-center animate-in fade-in slide-in-from-bottom-8 duration-1000">
        
        <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-50 border border-emerald-100 text-emerald-700 text-xs font-black uppercase tracking-widest mb-8 shadow-sm">
          <Sparkles size={14} className="text-emerald-500" /> AI Waste Intelligence
        </div>

        <h1 className="text-7xl sm:text-8xl md:text-9xl font-black text-transparent bg-clip-text bg-gradient-to-r from-emerald-500 via-teal-500 to-emerald-600 tracking-tighter leading-[1.1] mb-6 drop-shadow-sm pb-2">
          AVARTAN.
        </h1>
        
        <p className="text-lg sm:text-xl text-slate-500 font-medium max-w-2xl mb-10 leading-relaxed">
          Scan waste. Find routes. Track impact. A premium sustainability suite powered by proprietary Vision AI.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto">
          <Link to="/register" className="px-8 py-4 bg-emerald-500 hover:bg-emerald-400 text-slate-900 rounded-2xl text-lg font-black transition-all shadow-lg shadow-emerald-500/20 active:scale-95 flex items-center justify-center gap-2">
            Start Recycling <ArrowRight size={20} />
          </Link>
          <Link to="/login" className="px-8 py-4 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 rounded-2xl text-lg font-bold transition-all shadow-sm active:scale-95 flex items-center justify-center">
            Login
          </Link>
        </div>
      </header>

      {/* --- SUPPORTING 3-COLUMN GRID --- */}
      <section className="relative z-10 px-6 w-full max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-12 duration-1000 delay-200">
        
        <div className="bg-white/80 backdrop-blur-sm rounded-3xl p-8 shadow-sm border border-slate-100 hover:-translate-y-1 hover:shadow-lg hover:shadow-emerald-500/5 transition-all duration-300">
          <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center mb-6">
            <Camera size={24} />
          </div>
          <h3 className="text-xl font-black text-slate-900 mb-2 tracking-tight">AI Scanner</h3>
          <p className="text-slate-500 font-medium leading-relaxed text-sm">
            Point your camera. We instantly identify the material and calculate its eco-value.
          </p>
        </div>

        <div className="bg-white/80 backdrop-blur-sm rounded-3xl p-8 shadow-sm border border-slate-100 hover:-translate-y-1 hover:shadow-lg hover:shadow-emerald-500/5 transition-all duration-300">
          <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center mb-6">
            <MapPin size={24} />
          </div>
          <h3 className="text-xl font-black text-slate-900 mb-2 tracking-tight">Smart Routing</h3>
          <p className="text-slate-500 font-medium leading-relaxed text-sm">
            Find the closest verified drop-off hubs in Gandhinagar instantly via Google Maps.
          </p>
        </div>

        <div className="bg-white/80 backdrop-blur-sm rounded-3xl p-8 shadow-sm border border-slate-100 hover:-translate-y-1 hover:shadow-lg hover:shadow-emerald-500/5 transition-all duration-300">
          <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center mb-6">
            <Globe size={24} />
          </div>
          <h3 className="text-xl font-black text-slate-900 mb-2 tracking-tight">Real Impact</h3>
          <p className="text-slate-500 font-medium leading-relaxed text-sm">
            Measure your exact CO₂ savings and climb the community leaderboards.
          </p>
        </div>

      </section>

      {/* --- DARK CINEMATIC CLOSING BANNER --- */}
      <section className="relative z-10 px-6 w-full max-w-6xl mx-auto mt-12 mb-24 animate-in fade-in slide-in-from-bottom-12 duration-1000 delay-300">
        <div className="bg-slate-900 rounded-[2.5rem] overflow-hidden flex flex-col md:flex-row items-center shadow-2xl relative border border-slate-800">
          
          {/* Subtle Banner Background Glow */}
          <div className="absolute inset-0 bg-gradient-to-r from-emerald-900/30 to-transparent pointer-events-none"></div>
          <div className="absolute -right-20 -top-20 w-96 h-96 bg-emerald-500/10 blur-[80px] rounded-full pointer-events-none"></div>

          <div className="p-10 md:p-16 md:w-3/5 flex flex-col justify-center relative z-10">
            <h2 className="text-4xl md:text-5xl font-black text-white mb-4 leading-tight tracking-tight">
              Ready to join <br className="hidden md:block"/> <span className="text-emerald-400">AVARTAN?</span>
            </h2>
            <p className="text-slate-400 font-medium text-lg mb-10 max-w-md leading-relaxed">
              Step into the future of waste management. Start scanning, tracking, and earning Eco-Points today.
            </p>
            <Link to="/register" className="inline-flex items-center justify-center gap-2 bg-emerald-500 hover:bg-emerald-400 text-slate-900 px-8 py-4 rounded-2xl font-black transition-all active:scale-95 w-fit shadow-lg shadow-emerald-500/20">
              Create Free Account <ArrowRight size={20} />
            </Link>
          </div>

          <div className="md:w-2/5 w-full h-48 md:h-full relative overflow-hidden flex items-center justify-center pointer-events-none">
             <Trophy className="w-48 h-48 text-emerald-500/20 rotate-12 drop-shadow-2xl" />
          </div>
          
        </div>
      </section>

      {/* --- FOOTER --- */}
      <footer className="w-full border-t border-slate-200/60 py-8 px-6 bg-white/50 backdrop-blur-sm mt-auto relative z-10">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4 text-slate-400 font-bold text-xs uppercase tracking-widest">
          <div className="flex items-center gap-2">
             <ShieldCheck size={16} /> Secure Platform
          </div>
          <p>© 2026 AVARTAN. Gandhinagar, Gujarat.</p>
        </div>
      </footer>

    </div>
  );
};

export default Landing;
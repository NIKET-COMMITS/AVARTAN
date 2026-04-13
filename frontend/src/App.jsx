import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Leaf, Scan, Trophy, BarChart3, Recycle, 
  Wind, Sparkles, ArrowRight, Loader2, CheckCircle2 
} from 'lucide-react';

const API_BASE = "http://localhost:8000";

const App = () => {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingText, setLoadingText] = useState("");
  const [result, setResult] = useState(null);
  const [metrics, setMetrics] = useState({ co2: 12.5, items: 42, points: 2450 });
  const [leaderboard, setLeaderboard] = useState([]);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    try {
      // Fetch stats and leaderboard concurrently
      const [wasteRes, leadRes] = await Promise.all([
        axios.get(`${API_BASE}/waste/my-waste`),
        axios.get(`${API_BASE}/leaderboard/global?limit=5`)
      ]);
      
      if (wasteRes.data.success && wasteRes.data.data.summary) {
        setMetrics({
          co2: wasteRes.data.data.summary.total_co2_saved || 0,
          items: wasteRes.data.data.summary.total_count || 0,
          points: 2450 // Keeping static for visual impact unless your API returns it
        });
      }
      if (leadRes.data.success) {
        setLeaderboard(leadRes.data.data);
      }
    } catch (err) {
      console.error("Dashboard sync error", err);
    }
  };

  const handleAnalyze = async () => {
    if (!input) return;
    setLoading(true);
    setResult(null);
    setSaved(false);
    
    // Luxury detail: Dynamic loading text
    setLoadingText("Classifying materials...");
    setTimeout(() => setLoadingText("Calculating carbon offset..."), 1500);

    try {
      // Handles both query param and body flawlessly thanks to our backend fix
      const response = await axios.post(`${API_BASE}/waste/analyze`, { description: input });
      
      if (response.data.success) {
        setResult(response.data.data);
      }
    } catch (err) {
      console.error("Analysis failed", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveImpact = async () => {
    if (!result) return;
    try {
      await axios.post(`${API_BASE}/waste/add`, {
        item_name: result.item_name,
        quantity: 1, // Defaulting to 1 for the demo
        unit: "item",
        condition: result.condition || "fair",
        description: input
      });
      setSaved(true);
      fetchInitialData(); // Refresh the stats at the top!
    } catch (err) {
      console.error("Failed to save impact", err);
    }
  };

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_50%_0%,_#f0fdf4_0%,_#ffffff_70%)] text-slate-800 font-sans selection:bg-emerald-200">
      
      {/* 1. HEADER (Minimalist & Premium) */}
      <header className="max-w-7xl mx-auto px-6 py-8 flex justify-between items-center">
        <div className="flex items-center gap-3 cursor-pointer group">
          <div className="bg-emerald-600 p-2.5 rounded-2xl group-hover:rotate-12 transition-transform shadow-lg shadow-emerald-200">
            <Leaf className="text-white w-6 h-6" />
          </div>
          <h1 className="text-2xl font-semibold tracking-tighter uppercase text-slate-900">Avartan</h1>
        </div>
        <div className="bg-white/50 backdrop-blur-md px-5 py-2.5 rounded-full border border-white/80 shadow-sm flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-widest">Guardian</span>
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-emerald-700 font-bold">{metrics.points} PTS</span>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 grid grid-cols-1 lg:grid-cols-[1.5fr_1fr] gap-10 pb-40 mt-4">
        
        {/* 2. LEFT COLUMN: Stats & AI Result */}
        <div className="space-y-8">
          
          {/* Quick Stats */}
          <div className="grid grid-cols-3 gap-5">
            <StatCard icon={<Wind className="text-emerald-500 w-5 h-5"/>} label="CO2 Offset" value={`${metrics.co2}kg`} />
            <StatCard icon={<Recycle className="text-emerald-500 w-5 h-5"/>} label="Items Saved" value={metrics.items} />
            <StatCard icon={<BarChart3 className="text-emerald-500 w-5 h-5"/>} label="Rank" value="Top 5%" />
          </div>

          {/* AI Result Card (The Showstopper) */}
          {result && (
            <div className="animate-in fade-in slide-in-from-bottom-8 duration-700 ease-out backdrop-blur-2xl bg-white/60 rounded-[2.5rem] p-10 border border-white shadow-[0_20px_50px_rgba(0,0,0,0.05)]">
              
              <div className="flex justify-between items-start mb-8">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <Sparkles className="w-5 h-5 text-emerald-500" />
                    <span className="text-[10px] font-bold uppercase tracking-widest text-emerald-600">AI Analysis Complete</span>
                  </div>
                  <h3 className="text-4xl font-light tracking-tight text-slate-900 mb-3">{result.item_name}</h3>
                  <div className="flex gap-2">
                    <Badge color="emerald">{result.item_type}</Badge>
                    <Badge color="slate">{result.condition}</Badge>
                  </div>
                </div>
                <div className="text-right bg-emerald-50/80 px-6 py-4 rounded-3xl border border-emerald-100">
                  <p className="text-[10px] text-emerald-600 font-bold uppercase tracking-widest mb-1">Est. Value</p>
                  <p className="text-4xl font-bold text-emerald-700">₹{result.estimated_value_rupees}</p>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4 mt-8">
                <div className="bg-slate-900 text-white p-6 rounded-[2rem] flex flex-col justify-center relative overflow-hidden">
                  <div className="absolute top-0 right-0 p-4 opacity-10"><Leaf className="w-16 h-16"/></div>
                  <p className="text-slate-400 text-[10px] font-bold uppercase tracking-widest mb-1">Environmental Impact</p>
                  <p className="text-2xl font-medium">-{result.estimated_co2_saved_kg}kg CO2</p>
                </div>
                
                <button 
                  onClick={handleSaveImpact}
                  disabled={saved}
                  className={`p-6 rounded-[2rem] flex items-center justify-between group transition-all duration-300 ${
                    saved 
                    ? 'bg-emerald-100 text-emerald-700 cursor-default' 
                    : 'bg-emerald-600 text-white hover:bg-emerald-700 shadow-xl shadow-emerald-900/20 active:scale-95'
                  }`}
                >
                  <div>
                    <p className={`text-[10px] font-bold uppercase tracking-widest mb-1 ${saved ? 'text-emerald-500' : 'text-emerald-200'}`}>
                      {saved ? 'Impact Recorded' : 'Take Action'}
                    </p>
                    <p className="text-xl font-medium">{saved ? 'Saved to Profile' : 'Log This Item'}</p>
                  </div>
                  {saved ? <CheckCircle2 className="w-8 h-8" /> : <ArrowRight className="w-8 h-8 group-hover:translate-x-2 transition-transform" />}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* 3. RIGHT COLUMN: Global Leaderboard */}
        <div className="backdrop-blur-xl bg-white/50 rounded-[2.5rem] p-8 border border-white/80 shadow-[0_8px_30px_rgba(0,0,0,0.04)] h-fit">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-3">
              <div className="bg-emerald-100 p-2 rounded-xl text-emerald-600">
                <Trophy className="w-5 h-5" />
              </div>
              <h2 className="text-lg font-medium text-slate-800">Global Guardians</h2>
            </div>
          </div>
          
          <div className="space-y-5">
            {leaderboard?.length > 0 ? leaderboard.map((user, i) => (
              <div key={i} className="flex justify-between items-center group p-3 hover:bg-white/60 rounded-2xl transition-colors cursor-default">
                <div className="flex items-center gap-4">
                  <span className="text-xs font-bold text-slate-300 w-4">{i + 1}</span>
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-100 to-emerald-50 border border-emerald-100 flex items-center justify-center font-bold text-emerald-700 shadow-sm">
                    {user.full_name?.[0] || 'U'}
                  </div>
                  <span className="font-medium text-slate-700 group-hover:text-emerald-700 transition-colors">{user.full_name}</span>
                </div>
                <span className="text-sm font-bold text-slate-500">{user.total_points}</span>
              </div>
            )) : (
              <p className="text-sm text-slate-400 text-center py-4">No data yet.</p>
            )}
          </div>
        </div>
      </main>

      {/* 4. THE FLOATING HERO SCANNER */}
      <div className="fixed bottom-10 left-1/2 -translate-x-1/2 w-full max-w-2xl px-6 z-50">
        <div className="backdrop-blur-2xl bg-white/80 border border-white p-2.5 rounded-full shadow-[0_20px_60px_rgba(0,0,0,0.1)] flex items-center group transition-all duration-300 focus-within:ring-4 focus-within:ring-emerald-500/20 focus-within:bg-white focus-within:shadow-[0_30px_70px_rgba(16,185,129,0.15)]">
          <div className="pl-5 pr-2 hidden sm:block">
            {loading ? <Loader2 className="w-5 h-5 text-emerald-500 animate-spin" /> : <Scan className="w-5 h-5 text-slate-400 group-focus-within:text-emerald-500 transition-colors" />}
          </div>
          <input 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            placeholder={loading ? loadingText : "What are you recycling today? (e.g., Old iron rod)"}
            className="flex-1 bg-transparent px-4 sm:px-2 py-3 text-slate-800 placeholder:text-slate-400 focus:outline-none font-light text-lg disabled:opacity-50"
            onKeyDown={(e) => e.key === 'Enter' && handleAnalyze()}
          />
          <button 
            onClick={handleAnalyze}
            disabled={loading || !input.trim()}
            className="bg-slate-900 text-white p-4 rounded-full hover:bg-emerald-600 transition-all duration-300 shadow-md active:scale-95 disabled:opacity-40 disabled:hover:bg-slate-900"
          >
            {loading ? <Sparkles className="w-5 h-5 animate-pulse" /> : <ArrowRight className="w-5 h-5" />}
          </button>
        </div>
      </div>
    </div>
  );
};

// Reusable micro-components for cleanliness
const StatCard = ({ icon, label, value }) => (
  <div className="bg-white/50 backdrop-blur-sm p-6 rounded-[2rem] border border-white/80 shadow-[0_4px_20px_rgba(0,0,0,0.03)] flex flex-col items-center text-center group hover:-translate-y-1 transition-transform duration-300">
    <div className="mb-4 bg-white p-3 rounded-2xl shadow-sm group-hover:scale-110 transition-transform duration-300">{icon}</div>
    <p className="text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-1">{label}</p>
    <p className="text-2xl font-semibold tracking-tight text-slate-800">{value}</p>
  </div>
);

const Badge = ({ children, color }) => {
  const colors = {
    emerald: "bg-emerald-100 text-emerald-700 border-emerald-200",
    slate: "bg-slate-100 text-slate-600 border-slate-200"
  };
  return (
    <span className={`px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider border ${colors[color]}`}>
      {children}
    </span>
  );
};

export default App;
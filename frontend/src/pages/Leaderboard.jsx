import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Trophy, ChevronLeft, Medal, Award, Loader2 } from "lucide-react";
import api from "../api/axios";

const getTierColor = (tier) => {
  switch (tier?.toLowerCase()) {
    case 'eco-warrior': return 'bg-gradient-to-r from-emerald-400 to-teal-500 text-white shadow-emerald-500/30';
    case 'platinum': return 'bg-gradient-to-r from-slate-700 to-slate-900 text-slate-100 shadow-slate-900/30';
    case 'gold': return 'bg-gradient-to-r from-amber-300 to-yellow-500 text-yellow-950 shadow-amber-500/30';
    case 'silver': return 'bg-gradient-to-r from-slate-200 to-slate-400 text-slate-800 shadow-slate-400/30';
    default: return 'bg-gradient-to-r from-orange-200 to-orange-300 text-orange-900 shadow-orange-300/30'; // Bronze
  }
};

const Leaderboard = () => {
  const navigate = useNavigate();
  const [leaders, setLeaders] = useState([]);
  const [currentUserData, setCurrentUserData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        const response = await api.get("/leaderboards/global");
        setLeaders(response.data.data.top_10 || []);
        setCurrentUserData(response.data.data.current_user);
      } catch (error) {
        console.error("Failed to load leaderboard", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchLeaderboard();
  }, []);

  return (
    <div className="min-h-screen bg-[#F4F7F9] text-slate-900 font-sans pb-12">
      {/* Navbar */}
      <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-xl border-b border-slate-200/60 px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <button onClick={() => navigate("/dashboard")} className="flex items-center gap-2 text-slate-500 hover:text-slate-800 transition-colors font-bold text-sm">
            <ChevronLeft size={18} /> Back to Dashboard
          </button>
          <div className="flex items-center gap-2">
            <Trophy className="text-amber-500" size={20} />
            <span className="font-black tracking-tight">Global Rankings</span>
          </div>
        </div>
      </nav>

      <main className="max-w-5xl mx-auto p-4 sm:p-6 lg:p-8 mt-4">
        
        {/* Header */}
        <div className="text-center mb-12 animate-in fade-in slide-in-from-bottom-4 duration-700">
          <span className="text-xs font-black text-emerald-600 uppercase tracking-widest bg-emerald-100 px-3 py-1.5 rounded-lg mb-4 inline-block">Gandhinagar Region</span>
          <h1 className="text-4xl md:text-5xl font-black text-slate-900 tracking-tight mb-3">Community Leaderboard</h1>
          <p className="text-slate-500 font-medium max-w-xl mx-auto text-lg">Compete with neighbors to save the planet. Earn points for every item you recycle or donate.</p>
        </div>

        {isLoading ? (
          <div className="flex justify-center items-center py-20">
            <Loader2 className="animate-spin text-emerald-500" size={40} />
          </div>
        ) : (
          <>
            {/* Top 3 Podium */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12 items-end max-w-4xl mx-auto">
              {/* Rank 2 - Silver */}
              {leaders[1] && (
                <div className="order-2 md:order-1 bg-white rounded-[2rem] p-6 shadow-xl shadow-slate-200/50 border border-slate-100 text-center relative hover:-translate-y-2 transition-transform">
                  <div className="absolute -top-6 left-1/2 -translate-x-1/2 bg-slate-200 text-slate-600 w-12 h-12 rounded-full flex items-center justify-center font-black text-xl border-4 border-white shadow-sm">2</div>
                  <div className="mt-6 mb-2"><Medal size={32} className="mx-auto text-slate-400" /></div>
                  <h3 className="font-black text-lg text-slate-800 truncate">{leaders[1].name}</h3>
                  <span className={`text-[10px] font-black uppercase tracking-widest px-2.5 py-1 rounded-md inline-block mt-2 mb-4 ${getTierColor(leaders[1].tier)}`}>{leaders[1].tier}</span>
                  <p className="text-2xl font-black text-emerald-600">{leaders[1].points.toLocaleString()}</p>
                  <p className="text-xs text-slate-400 font-bold uppercase tracking-wider">Points</p>
                </div>
              )}

              {/* Rank 1 - Gold */}
              {leaders[0] && (
                <div className="order-1 md:order-2 bg-gradient-to-b from-amber-100 to-white rounded-[2rem] p-8 shadow-2xl shadow-amber-500/20 border border-amber-200 text-center relative z-10 hover:-translate-y-2 transition-transform transform md:-translate-y-4">
                  <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-gradient-to-br from-amber-300 to-amber-500 text-white w-16 h-16 rounded-full flex items-center justify-center font-black text-3xl border-4 border-white shadow-lg shadow-amber-500/40">1</div>
                  <div className="mt-6 mb-3"><Trophy size={48} className="mx-auto text-amber-500 drop-shadow-md" /></div>
                  <h3 className="font-black text-2xl text-slate-900 truncate">{leaders[0].name}</h3>
                  <span className={`text-xs font-black uppercase tracking-widest px-3 py-1.5 rounded-lg inline-block mt-2 mb-5 ${getTierColor(leaders[0].tier)}`}>{leaders[0].tier}</span>
                  <p className="text-4xl font-black text-emerald-600">{leaders[0].points.toLocaleString()}</p>
                  <p className="text-sm text-slate-500 font-bold uppercase tracking-wider">Points</p>
                </div>
              )}

              {/* Rank 3 - Bronze */}
              {leaders[2] && (
                <div className="order-3 md:order-3 bg-white rounded-[2rem] p-6 shadow-xl shadow-slate-200/50 border border-slate-100 text-center relative hover:-translate-y-2 transition-transform">
                  <div className="absolute -top-6 left-1/2 -translate-x-1/2 bg-orange-200 text-orange-800 w-12 h-12 rounded-full flex items-center justify-center font-black text-xl border-4 border-white shadow-sm">3</div>
                  <div className="mt-6 mb-2"><Award size={32} className="mx-auto text-orange-400" /></div>
                  <h3 className="font-black text-lg text-slate-800 truncate">{leaders[2].name}</h3>
                  <span className={`text-[10px] font-black uppercase tracking-widest px-2.5 py-1 rounded-md inline-block mt-2 mb-4 ${getTierColor(leaders[2].tier)}`}>{leaders[2].tier}</span>
                  <p className="text-2xl font-black text-emerald-600">{leaders[2].points.toLocaleString()}</p>
                  <p className="text-xs text-slate-400 font-bold uppercase tracking-wider">Points</p>
                </div>
              )}
            </div>

            {/* Current User Floating Banner (If not in top 3) */}
            {currentUserData && currentUserData.rank > 3 && (
               <div className="bg-emerald-600 rounded-2xl p-4 mb-6 shadow-lg shadow-emerald-500/20 text-white flex items-center justify-between max-w-4xl mx-auto border border-emerald-500">
                  <div className="flex items-center gap-4">
                     <div className="w-10 h-10 rounded-full bg-emerald-500 flex items-center justify-center font-black border-2 border-emerald-400">
                        #{currentUserData.rank}
                     </div>
                     <div>
                        <p className="font-black">Your Current Rank</p>
                        <p className="text-xs text-emerald-100 font-bold uppercase tracking-widest">{currentUserData.tier}</p>
                     </div>
                  </div>
                  <div className="text-right">
                     <p className="font-black text-xl">{currentUserData.points.toLocaleString()}</p>
                     <p className="text-[10px] uppercase tracking-widest text-emerald-200 font-bold">Points</p>
                  </div>
               </div>
            )}

            {/* The Rest of the Leaderboard */}
            <div className="bg-white rounded-3xl shadow-xl shadow-slate-200/40 border border-slate-100 overflow-hidden max-w-4xl mx-auto">
              <div className="grid grid-cols-12 gap-4 p-5 bg-slate-50 border-b border-slate-100 text-xs font-black text-slate-400 uppercase tracking-widest">
                <div className="col-span-2 sm:col-span-1 text-center">Rank</div>
                <div className="col-span-6 sm:col-span-5">Eco-Warrior</div>
                <div className="col-span-0 sm:col-span-3 hidden sm:block text-center">Tier</div>
                <div className="col-span-4 sm:col-span-3 text-right pr-4">Total Points</div>
              </div>

              <div className="divide-y divide-slate-100">
                {leaders.slice(3).map((user) => (
                  <div key={user.rank} className={`grid grid-cols-12 gap-4 p-5 items-center transition-colors group ${user.is_current_user ? 'bg-emerald-50/50' : 'hover:bg-slate-50'}`}>
                    <div className="col-span-2 sm:col-span-1 text-center">
                      <span className="font-black text-slate-400 group-hover:text-slate-700 transition-colors">#{user.rank}</span>
                    </div>
                    <div className="col-span-6 sm:col-span-5 flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center font-black shrink-0 ${user.is_current_user ? 'bg-emerald-500 text-white' : 'bg-emerald-100 text-emerald-700'}`}>
                        {user.name.charAt(0).toUpperCase()}
                      </div>
                      <div className="truncate">
                        <p className={`font-bold truncate ${user.is_current_user ? 'text-emerald-700' : 'text-slate-800'}`}>
                           {user.name} {user.is_current_user && "(You)"}
                        </p>
                        <p className="text-[10px] font-bold text-slate-400 uppercase sm:hidden">{user.tier}</p>
                      </div>
                    </div>
                    <div className="col-span-0 sm:col-span-3 hidden sm:flex justify-center">
                       <span className={`text-[10px] font-black uppercase tracking-widest px-2.5 py-1 rounded-md shadow-sm ${getTierColor(user.tier)}`}>
                         {user.tier}
                       </span>
                    </div>
                    <div className="col-span-4 sm:col-span-3 text-right pr-4">
                      <p className="font-black text-emerald-600">{user.points.toLocaleString()}</p>
                      <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest">{user.co2_saved}kg CO₂</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
};

export default Leaderboard;
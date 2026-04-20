import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { 
  Leaf, Package, Trophy, MapPin, 
  User, LogOut, ChevronRight,
  Award, Zap, X, ExternalLink
} from "lucide-react";
import AddWaste from "../components/AddWaste"; 
import api from "../api/axios";

// Strictly Gandhinagar verified E-Waste facilities
const verifiedHubs = [
  {
    name: "Infocity E-Waste Drop-off",
    area: "Infocity, Gandhinagar",
    address: "Supermall-1, Infocity IT Metropolis, Gandhinagar - 382421",
    accepts: "Computers, Mobiles, E-Waste"
  },
  {
    name: "Sector 11 Recycling Center",
    area: "Sector 11, Gandhinagar",
    address: "Service Market, Sector 11, Gandhinagar - 382010",
    accepts: "Appliances, Hardware, Plastic"
  },
  {
    name: "GIDC Electronics Recycler",
    area: "GIDC Estate, Gandhinagar",
    address: "Plot 45, GIDC Electronics Estate, Sector 25, Gandhinagar - 382024",
    accepts: "E-Waste, Hardware, Iron Scrap"
  }
];

const Dashboard = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState({ co2: 0, items: 0, points: 0 });
  const [leaderboard, setLeaderboard] = useState([]);
  const [userName, setUserName] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  
  const [selectedHub, setSelectedHub] = useState(null);

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good morning";
    if (hour < 18) return "Good afternoon";
    return "Good evening";
  };

  const handleLogout = () => {
    localStorage.removeItem("token"); 
    navigate("/login"); 
  };

  const goToProfile = () => {
    navigate("/profile"); 
  };

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setIsLoading(true);
        const [metricsRes, lbRes, profileRes] = await Promise.all([
          api.get("/dashboard/metrics"),
          api.get("/leaderboards/global"),
          api.get("/profile/me")
        ]);
        
        setStats({
          co2: metricsRes.data?.total_co2_saved || 0,
          items: metricsRes.data?.total_items || 0,
          points: metricsRes.data?.total_points || 0
        });
        
        // FIX: Safely parse the enterprise JSON structure from leaderboard.py
        const leaderboardArray = lbRes.data?.data?.top_10 || [];
        setLeaderboard(leaderboardArray.slice(0, 5));
        
        const actualName = profileRes.data?.name || (profileRes.data?.email ? profileRes.data.email.split('@')[0] : "Eco-Warrior");
        setUserName(actualName);

      } catch (err) {
        console.error("Dashboard Load Error:", err);
        if (err.response && err.response.status === 401) {
          handleLogout();
        }
      } finally {
        setIsLoading(false);
      }
    };
    fetchDashboardData();
  }, []);

  // --- THE TRUE GOOGLE MAPS CROSS-PLATFORM SEARCH API ---
  const openGoogleMaps = (hubName, hubAddress) => {
    const query = encodeURIComponent(`${hubName}, ${hubAddress}`);
    window.open(`https://www.google.com/maps/search/?api=1&query=$${query}`, '_blank');
  };

  return (
    <div className="min-h-screen bg-[#F4F7F9] text-slate-900 font-sans selection:bg-emerald-200">
      
      {/* --- HUB MAP MODAL POP-UP --- */}
      {selectedHub && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200" onClick={() => setSelectedHub(null)}>
          <div className="bg-white rounded-3xl p-6 md:p-8 max-w-md w-full shadow-2xl relative animate-in zoom-in-95 duration-200" onClick={e => e.stopPropagation()}>
            <button onClick={() => setSelectedHub(null)} className="absolute top-5 right-5 text-slate-400 hover:text-slate-700 bg-slate-100 hover:bg-slate-200 p-2 rounded-full transition-colors">
              <X size={20} />
            </button>
            
            <div className="bg-emerald-100 w-14 h-14 rounded-2xl flex items-center justify-center mb-5 shadow-inner">
              <MapPin className="text-emerald-600" size={28} />
            </div>
            
            <h3 className="text-2xl font-black text-slate-900 mb-1 leading-tight">{selectedHub.name}</h3>
            <p className="text-sm font-bold text-emerald-600 mb-6">{selectedHub.area}</p>
            
            <div className="bg-slate-50 rounded-2xl p-5 mb-6 border border-slate-200/60">
              <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1.5">Official Address</p>
              <p className="text-sm font-medium text-slate-700 mb-5 leading-relaxed">{selectedHub.address}</p>
              
              <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1.5">Materials Accepted</p>
              <p className="text-sm font-bold text-slate-800">{selectedHub.accepts}</p>
            </div>

            <button 
              onClick={() => openGoogleMaps(selectedHub.name, selectedHub.address)}
              className="w-full py-4 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-sm font-bold transition-all shadow-lg hover:shadow-xl hover:-translate-y-0.5 active:scale-95 flex items-center justify-center gap-2"
            >
              Open in Google Maps <ExternalLink size={18} />
            </button>
          </div>
        </div>
      )}

      {/* --- PREMIUM NAVBAR --- */}
      <nav className="sticky top-0 z-50 bg-white/70 backdrop-blur-xl border-b border-slate-200/60 px-6 py-4 transition-all">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-br from-emerald-400 to-emerald-600 p-2.5 rounded-xl shadow-lg shadow-emerald-500/30">
              <Leaf className="text-white" size={24} />
            </div>
            <div className="flex flex-col justify-center">
              <h1 className="text-2xl font-black tracking-tight text-slate-800 cursor-default leading-none mb-1">AVARTAN</h1>
              <span className="text-[10px] font-bold tracking-widest text-emerald-600 uppercase">E-Waste Intelligence</span>
            </div>
          </div>
          
          <div className="flex items-center gap-3 sm:gap-4">
            <div className="hidden md:flex items-center gap-2 bg-slate-50 px-4 py-2 rounded-full border border-slate-200/60 shadow-sm">
              <Award size={18} className="text-amber-500" />
              <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">Eco Hero</span>
              <span className="h-4 w-[1px] bg-slate-300 mx-1" />
              {isLoading ? (
                <div className="h-4 w-12 bg-slate-200 animate-pulse rounded"></div>
              ) : (
                <span className="text-sm font-black text-emerald-700">{stats.points} pts</span>
              )}
            </div>
            
            <button onClick={goToProfile} className="flex items-center gap-2 bg-white border border-slate-200 text-slate-700 px-4 py-2.5 rounded-xl text-sm font-bold hover:bg-emerald-50 hover:text-emerald-700 hover:border-emerald-200 transition-all shadow-sm active:scale-95">
                <User size={16} /> <span className="hidden sm:inline">Profile</span>
            </button>

            <button onClick={handleLogout} className="flex items-center gap-2 bg-slate-900 text-white px-4 sm:px-5 py-2.5 rounded-xl text-sm font-bold hover:bg-slate-800 hover:shadow-lg hover:-translate-y-0.5 active:scale-95 transition-all">
              <LogOut size={16} /> <span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8 space-y-8">
        <section className="animate-in fade-in slide-in-from-bottom-4 duration-700">
            <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
                {getGreeting()}, <span className="text-emerald-600">{isLoading ? "Eco-Warrior" : userName}</span>
            </h2>
            <p className="text-slate-500 font-medium mt-1 text-lg">Your personal e-waste command center is ready.</p>
        </section>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <StatCard icon={<Leaf className="text-emerald-500" size={24} />} label="CO₂ Saved" value={`${stats.co2.toFixed(2)} kg`} color="emerald" isLoading={isLoading} />
          <StatCard icon={<Package className="text-blue-500" size={24} />} label="Items Recycled" value={stats.items} color="blue" isLoading={isLoading} />
          <StatCard icon={<Trophy className="text-amber-500" size={24} />} label="Community Impact" value={stats.points} color="amber" isLoading={isLoading} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          <div className="lg:col-span-8 w-full">
            <div className="bg-white rounded-[2.5rem] p-2 sm:p-4 shadow-xl shadow-slate-200/40 border border-slate-100/60 ring-1 ring-slate-900/5">
              <AddWaste />
            </div>
          </div>

          <div className="lg:col-span-4 space-y-8 sticky top-24">
            <div className="bg-white rounded-3xl p-6 shadow-xl shadow-slate-200/40 border border-slate-100/60 overflow-hidden relative group">
              <div className="flex justify-between items-center mb-6">
                <h3 className="font-bold text-lg flex items-center gap-2 text-slate-800">
                    <Trophy className="text-amber-500" size={22}/> Leaderboard
                </h3>
                {/* FIX: Wired up the "View All" button to navigate properly */}
                <button 
                  onClick={() => navigate("/leaderboard")} 
                  className="text-xs font-bold text-emerald-600 hover:text-emerald-700 bg-emerald-50 hover:bg-emerald-100 px-3 py-1.5 rounded-lg transition-colors active:scale-95"
                >
                    View All
                </button>
              </div>
              
              <div className="space-y-3">
                {isLoading ? (
                  Array(5).fill(0).map((_, i) => (
                    <div key={i} className="flex justify-between items-center p-2">
                        <div className="flex items-center gap-3">
                            <div className="w-6 h-6 rounded-full bg-slate-100 animate-pulse"></div>
                            <div className="w-24 h-4 bg-slate-100 rounded animate-pulse"></div>
                        </div>
                        <div className="w-12 h-4 bg-slate-100 rounded animate-pulse"></div>
                    </div>
                  ))
                ) : leaderboard.length > 0 ? (
                  leaderboard.map((user, idx) => (
                    <div key={idx} className="flex items-center justify-between p-2 rounded-xl hover:bg-slate-50 transition-colors group/item cursor-default">
                      <div className="flex items-center gap-3">
                        <span className={`w-7 h-7 flex items-center justify-center rounded-full text-xs font-black shadow-sm ${
                            idx === 0 ? 'bg-gradient-to-br from-amber-200 to-amber-400 text-amber-900' : 
                            idx === 1 ? 'bg-gradient-to-br from-slate-200 to-slate-300 text-slate-700' :
                            idx === 2 ? 'bg-gradient-to-br from-orange-200 to-orange-300 text-orange-900' :
                            'bg-slate-100 text-slate-500'
                        }`}>
                            {idx + 1}
                        </span>
                        <p className="text-sm font-bold text-slate-700 group-hover/item:text-slate-900">{user.name}</p>
                      </div>
                      <p className="text-sm font-black text-emerald-600">{user.points} <span className="text-[10px] text-emerald-600/50 uppercase">pts</span></p>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 bg-slate-50 rounded-2xl border border-slate-100 border-dashed">
                    <Trophy className="mx-auto text-slate-300 mb-3" size={32} />
                    <p className="text-sm text-slate-500 font-medium">No eco-warriors yet.</p>
                    <p className="text-xs text-slate-400 mt-1">Recycle an item to claim 1st place!</p>
                  </div>
                )}
              </div>
            </div>

            <div className="bg-gradient-to-br from-emerald-900 to-emerald-950 rounded-3xl p-6 text-white shadow-2xl shadow-emerald-900/20 relative overflow-hidden ring-1 ring-emerald-800">
               <div className="absolute -bottom-8 -right-8 w-48 h-48 bg-emerald-500/20 rounded-full blur-3xl"></div>
               <Zap className="absolute -top-4 -right-2 text-emerald-800/50 h-24 w-24 rotate-12" />
               
               <h3 className="font-bold text-lg mb-1 flex items-center gap-2 relative z-10 text-emerald-50">
                   <MapPin size={22} className="text-emerald-400"/> Verified Hubs
               </h3>
               <p className="text-xs text-emerald-300/80 mb-5 relative z-10 font-medium">Gandhinagar Region</p>
               
               <div className="space-y-3 relative z-10">
                  {verifiedHubs.map((hub, index) => (
                    <DropOffItem 
                      key={index} 
                      hub={hub} 
                      onClick={() => setSelectedHub(hub)} 
                    />
                  ))}
               </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

const StatCard = ({ icon, label, value, color, isLoading }) => {
  const colorMap = {
    emerald: "bg-emerald-50 text-emerald-700 ring-emerald-100",
    blue: "bg-blue-50 text-blue-700 ring-blue-100",
    amber: "bg-amber-50 text-amber-700 ring-amber-100"
  };

  return (
    <div className="bg-white p-6 rounded-3xl shadow-xl shadow-slate-200/40 border border-slate-100/60 hover:-translate-y-1 hover:shadow-2xl hover:shadow-slate-200/50 transition-all duration-300 group">
      <div className="flex justify-between items-start mb-4">
        <div className={`p-3 rounded-2xl ring-1 ${colorMap[color]} transition-colors`}>{icon}</div>
      </div>
      <p className="text-slate-500 text-xs font-bold uppercase tracking-widest mb-1">{label}</p>
      {isLoading ? (
        <div className="h-8 w-24 bg-slate-100 animate-pulse rounded-lg mt-2"></div>
      ) : (
        <p className="text-3xl sm:text-4xl font-black text-slate-800 tracking-tight group-hover:text-slate-900 transition-colors">{value}</p>
      )}
    </div>
  );
};

const DropOffItem = ({ hub, onClick }) => (
  <div onClick={onClick} className="flex justify-between items-center p-3.5 rounded-2xl bg-white/5 border border-white/10 hover:bg-white/10 hover:border-emerald-500/30 transition-all cursor-pointer group backdrop-blur-sm active:scale-[0.98]">
    <div>
      <p className="text-sm font-bold text-slate-100 group-hover:text-emerald-300 transition-colors">{hub.name}</p>
      <p className="text-[10px] text-emerald-400/80 font-bold tracking-wide mt-0.5 uppercase">{hub.area}</p>
    </div>
    <div className="bg-white/10 p-1.5 rounded-full group-hover:bg-emerald-500/20 transition-colors">
        <ChevronRight size={16} className="text-emerald-400 group-hover:text-emerald-300 group-hover:translate-x-0.5 transition-all" />
    </div>
  </div>
);

export default Dashboard;
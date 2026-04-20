import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { 
  User, Mail, Calendar, Trash2, 
  ChevronLeft, ShieldAlert, Trophy, 
  Leaf, Package, Loader2, LogOut, Award
} from "lucide-react";
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

const Profile = () => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await api.get("/profile/me");
        setProfile(response.data.data);
      } catch (error) {
        console.error("Failed to load profile:", error);
        if (error.response?.status === 401) {
          localStorage.removeItem("token");
          navigate("/login");
        }
      } finally {
        setIsLoading(false);
      }
    };
    fetchProfile();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  const handleDeleteAccount = async () => {
    setIsDeleting(true);
    try {
      await api.delete("/auth/delete-account");
      localStorage.removeItem("token");
      navigate("/register", { state: { message: "Account deleted successfully." } });
    } catch (error) {
      console.error("Deletion failed:", error);
      alert("Failed to delete account. Please try again.");
      setIsDeleting(false);
      setShowDeleteModal(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#F4F7F9] flex items-center justify-center">
        <Loader2 className="animate-spin text-emerald-500" size={40} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F4F7F9] text-slate-900 font-sans pb-12">
      
      {/* --- DELETE CONFIRMATION MODAL --- */}
      {showDeleteModal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-white rounded-3xl p-6 md:p-8 max-w-md w-full shadow-2xl relative animate-in zoom-in-95 duration-200">
            <div className="bg-red-100 w-14 h-14 rounded-2xl flex items-center justify-center mb-5 shadow-inner">
              <ShieldAlert className="text-red-600" size={28} />
            </div>
            <h3 className="text-2xl font-black text-slate-900 mb-2">Delete Account?</h3>
            <p className="text-sm font-medium text-slate-600 mb-6 leading-relaxed">
              This action is permanent and cannot be undone. All your Eco-Points, saved CO₂, and ranking history will be permanently erased.
            </p>
            <div className="flex gap-3">
              <button 
                onClick={() => setShowDeleteModal(false)}
                disabled={isDeleting}
                className="flex-1 py-3.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-sm font-bold transition-all"
              >
                Cancel
              </button>
              <button 
                onClick={handleDeleteAccount}
                disabled={isDeleting}
                className="flex-1 py-3.5 bg-red-600 hover:bg-red-700 text-white rounded-xl text-sm font-bold transition-all shadow-lg shadow-red-600/20 flex justify-center items-center gap-2"
              >
                {isDeleting ? <Loader2 className="animate-spin" size={18} /> : "Yes, Delete"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* --- NAVBAR --- */}
      <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-xl border-b border-slate-200/60 px-6 py-4">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <button onClick={() => navigate("/dashboard")} className="flex items-center gap-2 text-slate-500 hover:text-slate-800 transition-colors font-bold text-sm">
            <ChevronLeft size={18} /> Dashboard
          </button>
          <div className="flex items-center gap-2">
            <User className="text-emerald-500" size={20} />
            <span className="font-black tracking-tight">Eco-Identity</span>
          </div>
        </div>
      </nav>

      <main className="max-w-3xl mx-auto p-4 sm:p-6 mt-6 animate-in slide-in-from-bottom-4 duration-700">
        
        {/* --- IDENTITY CARD --- */}
        <div className="bg-white rounded-[2.5rem] p-8 shadow-xl shadow-slate-200/40 border border-slate-100 mb-8 relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-50 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3"></div>
          
          <div className="flex flex-col md:flex-row items-center md:items-start gap-6 relative z-10">
            <div className="w-24 h-24 rounded-full bg-slate-900 text-white flex items-center justify-center text-4xl font-black shadow-lg">
              {profile?.name?.charAt(0).toUpperCase() || "E"}
            </div>
            
            <div className="text-center md:text-left flex-1">
              <h1 className="text-3xl font-black text-slate-900 tracking-tight">{profile?.name || "Eco Warrior"}</h1>
              
              <div className="flex flex-wrap justify-center md:justify-start gap-4 mt-3">
                <span className="flex items-center gap-1.5 text-sm font-bold text-slate-500">
                  <Mail size={16} className="text-slate-400" /> {profile?.email}
                </span>
                <span className="flex items-center gap-1.5 text-sm font-bold text-slate-500">
                  <Calendar size={16} className="text-slate-400" /> Joined {profile?.member_since}
                </span>
              </div>

              <div className="mt-6 inline-block">
                <span className={`flex items-center gap-2 text-sm font-black uppercase tracking-widest px-4 py-2 rounded-xl shadow-md ${getTierColor(profile?.impact?.tier)}`}>
                  <Award size={18} /> {profile?.impact?.tier || "Bronze"} Tier
                </span>
              </div>
            </div>
            
            <button 
              onClick={handleLogout}
              className="mt-4 md:mt-0 px-5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-sm font-bold transition-all flex items-center gap-2 active:scale-95"
            >
              <LogOut size={16} /> Logout
            </button>
          </div>
        </div>

        {/* --- IMPACT STATS --- */}
        <h3 className="font-black text-lg text-slate-800 mb-4 px-2">Lifetime Impact</h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-10">
          <div className="bg-white p-5 rounded-3xl border border-slate-100 shadow-sm flex flex-col items-center justify-center text-center hover:border-emerald-200 transition-colors">
            <div className="w-12 h-12 rounded-full bg-emerald-50 text-emerald-500 flex items-center justify-center mb-3"><Leaf size={24}/></div>
            <p className="text-3xl font-black text-slate-900">{profile?.impact?.co2_saved?.toFixed(1) || "0.0"}</p>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">KG CO₂ Saved</p>
          </div>
          <div className="bg-white p-5 rounded-3xl border border-slate-100 shadow-sm flex flex-col items-center justify-center text-center hover:border-blue-200 transition-colors">
            <div className="w-12 h-12 rounded-full bg-blue-50 text-blue-500 flex items-center justify-center mb-3"><Package size={24}/></div>
            <p className="text-3xl font-black text-slate-900">{profile?.impact?.items_recycled || 0}</p>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">Items Processed</p>
          </div>
          <div className="bg-white p-5 rounded-3xl border border-slate-100 shadow-sm flex flex-col items-center justify-center text-center hover:border-amber-200 transition-colors">
            <div className="w-12 h-12 rounded-full bg-amber-50 text-amber-500 flex items-center justify-center mb-3"><Trophy size={24}/></div>
            <p className="text-3xl font-black text-slate-900">{profile?.impact?.points?.toLocaleString() || 0}</p>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">Eco-Points</p>
          </div>
        </div>

        {/* --- DANGER ZONE --- */}
        <div className="mt-12 bg-red-50/50 rounded-3xl p-6 md:p-8 border border-red-100">
          <h3 className="font-black text-red-900 flex items-center gap-2 mb-2">
            <ShieldAlert size={20} className="text-red-600" /> Danger Zone
          </h3>
          <p className="text-sm font-medium text-red-800/70 mb-6">
            Permanently delete your account and all associated environmental impact data. This cannot be undone.
          </p>
          <button 
            onClick={() => setShowDeleteModal(true)}
            className="px-6 py-3 bg-white text-red-600 border border-red-200 hover:bg-red-50 hover:border-red-300 rounded-xl text-sm font-bold transition-all flex items-center gap-2 active:scale-95 shadow-sm"
          >
            <Trash2 size={18} /> Delete Account
          </button>
        </div>

      </main>
    </div>
  );
};

export default Profile;
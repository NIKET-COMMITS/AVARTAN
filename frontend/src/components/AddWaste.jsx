import React, { useState, useEffect } from "react";
import { 
  Camera, Zap, CheckCircle, ShieldAlert, 
  MapPin, ExternalLink, Loader2, X, UploadCloud, 
  MessageSquare, ShieldCheck, ChevronRight, Star
} from "lucide-react";
import api from "../api/axios";

// --- EMBEDDED DATA (CRASH-PROOF) ---
const verifiedPlatforms = {
  Sell: [
    { name: "Cashify", url: "https://www.cashify.in", desc: "Best for electronics and gadgets.", features: ["Free Doorstep Pickup", "Instant Cash"] },
    { name: "OLX", url: "https://www.olx.in", desc: "Best for furniture and general items.", features: ["Local Buyers", "Set Your Own Price"] }
  ],
  Repair: [
    { name: "Urban Company", url: "https://www.urbancompany.com/", desc: "At-home repair for appliances.", features: ["Verified Techs", "90-Day Guarantee"] },
    { name: "Onsitego", url: "https://onsitego.com/", desc: "Verified doorstep repair for electronics.", features: ["Genuine Parts", "Free Pickup"] }
  ],
  Donate: [
    { name: "Goonj", url: "https://goonj.org/", desc: "Donate clothes, toys, and household goods.", features: ["National Impact", "80G Tax Benefits"] },
    { name: "Share At Door Step", url: "https://sadsindia.org/", desc: "Convenient doorstep donation pickups.", features: ["Convenient Pickup", "Supports NGOs"] }
  ],
  Recycle: [
    { name: "Namo E-Waste", url: "https://namoewaste.com/", desc: "Certified e-waste recycling.", features: ["Govt Certified", "Data Destruction"] },
    { name: "The Kabadiwala", url: "https://www.thekabadiwala.com/", desc: "Scrap pickup for paper, plastic, metal.", features: ["Digital Weighing", "Instant Payment"] }
  ]
};

const verifiedOfflineHubs = {
  Sell: [
    { name: "Infocity Resale Hub", address: "Infocity Supermall, Gandhinagar", accepts: "Electronics & Laptops" },
    { name: "Sector 21 Electronics Market", address: "Sector 21, Gandhinagar", accepts: "Mobiles & Accessories" }
  ],
  Repair: [
    { name: "Sector 11 Service Market", address: "Sector 11, Gandhinagar", accepts: "Mobiles, Laptops & Appliances" },
    { name: "Pramukh Arcade Tech Repair", address: "Pramukh Arcade, Reliance Cross Road, Gandhinagar", accepts: "Hardware & PCs" }
  ],
  Donate: [
    { name: "Goonj Drop-off Center", address: "Sector 16, Gandhinagar", accepts: "Clothes & Household items" },
    { name: "Rotary Club Donation Drive", address: "Sector 8, Gandhinagar", accepts: "Working electronics" }
  ],
  Recycle: [
    { name: "GIDC Electronics Recycler", address: "Plot 45, GIDC Electronics Estate, Sector 25, Gandhinagar", accepts: "E-Waste, Hardware, Iron Scrap" },
    { name: "Sector 11 Recycling Center", address: "Service Market, Sector 11, Gandhinagar", accepts: "Appliances, Hardware, Plastic" }
  ]
};
// ------------------------------------

const AddWaste = ({ onSubmitted }) => {
  const [step, setStep] = useState(1);
  const [imageFiles, setImageFiles] = useState([]);
  const [previewUrls, setPreviewUrls] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingMsg, setLoadingMsg] = useState("Run AI Intelligence");
  const [error, setError] = useState("");
  
  // AI State
  const [aiReport, setAiReport] = useState(null);
  const [answers, setAnswers] = useState({});
  const [recommendation, setRecommendation] = useState(null);
  const [activeTab, setActiveTab] = useState("Sell");

  // UI Modal & Verification State
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [verifying, setVerifying] = useState(false);
  const [verificationResult, setVerificationResult] = useState(null);

  useEffect(() => {
    let interval;
    if (loading) {
      const msgs = ["Scanning image...", "Identifying components...", "Calculating market value...", "Consulting database..."];
      let i = 0;
      setLoadingMsg(msgs[0]);
      interval = setInterval(() => {
        i = (i + 1) % msgs.length;
        setLoadingMsg(msgs[i]);
      }, 2000);
    } else {
      setLoadingMsg("Run AI Intelligence");
    }
    return () => clearInterval(interval);
  }, [loading]);

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;

    const MAX_SIZE_BYTES = 15 * 1024 * 1024;
    const validFiles = [];
    for (const file of files) {
      if (file.size > MAX_SIZE_BYTES) {
        setError(`Whoops! "${file.name}" is too large. Keep it under 15MB.`);
        return;
      }
      validFiles.push(file);
    }

    setImageFiles(prev => [...prev, ...validFiles]);
    setPreviewUrls(prev => [...prev, ...validFiles.map(file => URL.createObjectURL(file))]);
    setStep(1); setAiReport(null); setError(""); setAnswers({}); setVerificationResult(null);
  };

  const removeImage = (index) => {
    const newFiles = [...imageFiles];
    const newUrls = [...previewUrls];
    newFiles.splice(index, 1);
    newUrls.splice(index, 1);
    setImageFiles(newFiles);
    setPreviewUrls(newUrls);
  };

  const runDiagnostic = async (previousAnswers = null) => {
    setLoading(true); 
    setError("");

    const formData = new FormData();
    if (!previousAnswers && imageFiles.length > 0) {
      imageFiles.forEach(file => formData.append("image", file));
    }
    if (previousAnswers) {
        formData.append("item_text", aiReport?.name || "");
        formData.append("user_answers", JSON.stringify(previousAnswers));
    }

    try {
      const response = await api.post("/waste/diagnose", formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
      });
      const data = response.data.data;

      setAiReport({
        name: data.item_identified || "Unknown Item",
        category: data.category || "General",
        status: data.status,
        range: data.estimated_value_range_inr || [0, 0],
        finalValue: data.final_value_inr || 0,
        questions: data.questions_to_ask || [],
        insight: data.reasoning
      });
      setStep(2);
    } catch (err) {
      setError("AI Engine failed to process the diagnostic. Please check your connection.");
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (idx, value) => {
      setAnswers(prev => ({...prev, [idx]: value}));
  };

  const submitAnswers = () => {
      const formattedAnswers = (aiReport?.questions || []).map((q, idx) => `Q: ${q} | A: ${answers[idx]}`);
      runDiagnostic(formattedAnswers);
      setAnswers({});
  };

  const generateFinalVerdict = () => {
    setLoading(true);
    setTimeout(() => {
      let action = "Recycle";
      let verdict = "Recycle Safely";
      
      // CRASH FIX: Hyper-safe fallbacks for all AI data
      let reason = aiReport?.insight || "This item should be responsibly handled.";
      const val = aiReport?.finalValue || 0;
      const cat = String(aiReport?.category || "").toLowerCase();

      if (val > 1500 && !cat.includes('appliance')) {
        action = "Sell"; verdict = "Highly Sellable";
      } else if (val > 500 && val <= 1500) {
        action = "Donate"; verdict = "Perfect for Donation";
      } else if (cat.includes("ewaste") && val > 2000) {
        action = "Repair"; verdict = "Repair Recommended";
      }

      setRecommendation({ action, verdict, reason, finalValue: val });
      setActiveTab(action); 
      setStep(3);
      setLoading(false);
    }, 800);
  };

  const handleVerificationUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setVerifying(true);
    const formData = new FormData();
    formData.append("receipt_image", file);
    formData.append("action_type", activeTab);

    try {
      const response = await api.post("/waste/verify-action", formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setVerificationResult(response.data);
    } catch (err) {
      setVerificationResult({ verified: false, message: "Server error. Could not verify receipt." });
    } finally {
      setVerifying(false);
    }
  };

  // Safe data extraction
  const currentPlatforms = verifiedPlatforms[activeTab] || [];
  const currentHubs = verifiedOfflineHubs[activeTab] || [];

  return (
    <div className="w-full relative">
      
      {/* MAP MODAL OVERLAY */}
      {selectedLocation && (
        <div className="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200" onClick={() => setSelectedLocation(null)}>
          <div className="bg-white rounded-3xl p-6 md:p-8 max-w-md w-full shadow-2xl relative animate-in zoom-in-95 duration-200" onClick={e => e.stopPropagation()}>
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-xl font-black text-slate-900">{selectedLocation.name}</h3>
                <p className="flex items-start gap-1 text-sm text-slate-500 mt-2 font-medium">
                  <MapPin size={16} className="text-emerald-500 shrink-0 mt-0.5" />
                  <span>{selectedLocation.address}</span>
                </p>
              </div>
              <button type="button" onClick={() => setSelectedLocation(null)} className="p-2 rounded-lg hover:bg-slate-100 text-slate-500 transition-colors">
                <X size={20} />
              </button>
            </div>
            
            <p className="text-xs font-bold uppercase tracking-wide text-slate-400 mb-1 mt-4">Accepts</p>
            <p className="text-sm text-slate-700 font-bold mb-5">{selectedLocation.accepts || "Various Items"}</p>
            
            <a
              href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(selectedLocation.address)}`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-center gap-2 w-full py-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-black uppercase tracking-widest text-sm transition-all shadow-lg active:scale-95"
            >
              Open in Google Maps <ExternalLink size={18} />
            </a>
          </div>
        </div>
      )}

      {/* Progress Bar */}
      <div className="flex items-center gap-2 mb-6 px-2">
        {[1, 2, 3].map(i => (
          <div key={i} className={`h-1.5 rounded-full transition-all duration-500 ${step >= i ? 'bg-emerald-500 w-12 shadow-sm shadow-emerald-500/20' : 'bg-slate-100 w-6'}`} />
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6">
        
        {/* ================= STEP 1: UPLOAD ================= */}
        {step === 1 && (
          <div className="animate-in fade-in zoom-in-95 duration-300">
            <div className={`relative w-full min-h-[240px] rounded-3xl border-2 border-dashed p-6 mb-6 transition-colors ${previewUrls.length > 0 ? 'border-emerald-300 bg-emerald-50/30' : 'border-slate-200 bg-slate-50 hover:bg-slate-100/50'}`}>
              {previewUrls.length > 0 ? (
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                  {previewUrls.map((url, idx) => (
                    <div key={idx} className="relative aspect-square rounded-2xl overflow-hidden shadow-sm group">
                      <img src={url} alt={`Preview`} className="w-full h-full object-cover transition-transform group-hover:scale-105" />
                      <button onClick={() => removeImage(idx)} className="absolute top-2 right-2 p-1.5 bg-red-500/90 text-white rounded-full hover:bg-red-600 transition-colors backdrop-blur-sm"><X size={14} /></button>
                    </div>
                  ))}
                  <label className="cursor-pointer aspect-square rounded-2xl border-2 border-dashed border-emerald-300 flex flex-col items-center justify-center text-emerald-600 hover:bg-emerald-50 transition-colors">
                    <Camera size={24} className="mb-2 opacity-80" />
                    <span className="text-sm font-bold">Add Angle</span>
                    <input type="file" accept="image/*" multiple onChange={handleFileChange} className="hidden" />
                  </label>
                </div>
              ) : (
                <label className="absolute inset-0 flex flex-col items-center justify-center cursor-pointer text-center p-6 group">
                  <div className="bg-white p-4 rounded-full shadow-sm mb-4 group-hover:scale-110 group-hover:shadow-md transition-all">
                    <Camera className="h-8 w-8 text-slate-400 group-hover:text-emerald-500 transition-colors" />
                  </div>
                  <p className="text-lg font-bold text-slate-800 tracking-tight">Scan Any Item</p>
                  <p className="text-sm text-slate-400 mt-1 max-w-xs font-medium">Upload photos of electronics, appliances, or recyclables to get an AI appraisal.</p>
                  <input type="file" accept="image/*" multiple onChange={handleFileChange} className="hidden" />
                </label>
              )}
            </div>
            
            {error && (
               <div className="bg-red-50 text-red-700 p-4 rounded-2xl mb-6 border border-red-100 text-sm font-bold flex items-center gap-3">
                 <ShieldAlert className="shrink-0 text-red-500" size={20} />
                 <p>{error}</p>
               </div>
            )}
            
            <button 
              onClick={() => runDiagnostic()} 
              disabled={imageFiles.length === 0 || loading} 
              className={`w-full font-black py-4 rounded-2xl flex justify-center items-center gap-2 transition-all active:scale-[0.98] ${imageFiles.length === 0 ? 'bg-slate-100 text-slate-400 cursor-not-allowed' : 'bg-slate-900 hover:bg-slate-800 text-white shadow-xl shadow-slate-900/20'}`}
            >
              {loading ? <Loader2 className="animate-spin" /> : <Zap size={18}/>} {loadingMsg}
            </button>
          </div>
        )}

        {/* ================= STEP 2: DYNAMIC ASSESSMENT ================= */}
        {step === 2 && aiReport && (
          <div className="bg-slate-900 rounded-[2rem] p-6 sm:p-8 shadow-2xl text-white relative overflow-hidden animate-in slide-in-from-right-8 duration-500">
            <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl transform translate-x-1/3 -translate-y-1/3"></div>

            <div className="flex flex-col md:flex-row justify-between items-start mb-8 gap-6 relative z-10">
              <div>
                <span className="text-[10px] uppercase font-black px-2.5 py-1 rounded-lg bg-blue-500/20 text-blue-300 border border-blue-500/30 mb-3 inline-block tracking-widest">
                  {aiReport.category}
                </span>
                <h3 className="text-3xl font-black tracking-tight">{aiReport.name}</h3>
                {aiReport.insight && <p className="text-slate-300 text-sm mt-3 max-w-md leading-relaxed font-medium">{aiReport.insight}</p>}
              </div>
              <div className="md:text-right bg-slate-800/80 backdrop-blur-sm p-5 rounded-2xl border border-slate-700 w-full md:w-auto shadow-inner">
                <p className="text-[10px] text-slate-400 uppercase tracking-widest mb-1.5 font-black">
                    {aiReport.status === 'complete' ? 'Locked AI Valuation' : 'Est. Market Range'}
                </p>
                <p className="text-3xl font-black text-emerald-400">
                    {aiReport.status === 'complete' 
                        ? `₹${aiReport.finalValue.toLocaleString('en-IN')}`
                        : `₹${(aiReport.range?.[0] || 0).toLocaleString('en-IN')} - ₹${(aiReport.range?.[1] || 0).toLocaleString('en-IN')}`
                    }
                </p>
              </div>
            </div>

            {aiReport.status === 'needs_info' ? (
                <div className="space-y-4 relative z-10">
                  <div className="flex items-center gap-2 mb-5">
                    <MessageSquare size={16} className="text-amber-400"/> 
                    <p className="text-sm text-slate-200 font-bold">The AI needs context to lock in the final price:</p>
                  </div>
                  {(aiReport.questions || []).map((q, idx) => (
                      <div key={idx} className="flex flex-col gap-2 bg-slate-800/50 p-4 rounded-2xl border border-slate-700/50 focus-within:border-emerald-500/50 transition-colors">
                        <p className="text-sm font-bold text-slate-100">{q}</p>
                        <input 
                            type="text" 
                            placeholder="Type your answer here..." 
                            value={answers[idx] || ""}
                            autoFocus={idx === 0}
                            onChange={(e) => handleAnswerChange(idx, e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' && Object.keys(answers).length === (aiReport.questions || []).length) {
                                    submitAnswers();
                                }
                            }}
                            className="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-sm text-white focus:outline-none focus:ring-1 focus:ring-emerald-500 transition-all placeholder:text-slate-600 font-medium"
                        />
                      </div>
                  ))}
                  
                  <button 
                      onClick={submitAnswers} 
                      disabled={loading || Object.keys(answers).length < (aiReport.questions || []).length} 
                      className="w-full font-black py-4 rounded-2xl bg-emerald-500 hover:bg-emerald-400 text-slate-900 flex justify-center items-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-xl mt-6 active:scale-[0.98]"
                  >
                      {loading ? <Loader2 className="animate-spin" /> : <Zap size={18}/>} {loading ? loadingMsg : "Analyze Answers"}
                  </button>
                </div>
            ) : (
                <button 
                  onClick={generateFinalVerdict} 
                  disabled={loading} 
                  className="w-full font-black py-4 rounded-2xl bg-emerald-500 hover:bg-emerald-400 text-slate-900 flex justify-center items-center gap-2 transition-all shadow-xl shadow-emerald-500/20 active:scale-[0.98] relative z-10"
                >
                  {loading ? <Loader2 className="animate-spin" /> : <CheckCircle size={18}/>} {loading ? "Generating Action Plan..." : "Generate Action Plan"}
                </button>
            )}
          </div>
        )}

        {/* ================= STEP 3: ACTION ROUTER ================= */}
        {step === 3 && recommendation && (
          <div className="space-y-6 animate-in slide-in-from-bottom-8 duration-500">
            
            {/* Verdict Banner */}
            <div className={`rounded-3xl p-6 sm:p-8 shadow-sm border ${
              recommendation.action === 'Sell' ? 'bg-emerald-50 border-emerald-200' :
              recommendation.action === 'Repair' ? 'bg-blue-50 border-blue-200' :
              recommendation.action === 'Donate' ? 'bg-purple-50 border-purple-200' :
              'bg-amber-50 border-amber-200'
            }`}>
              <div className="flex justify-between items-start gap-4">
                <div>
                  <p className="text-[10px] font-black uppercase tracking-widest opacity-60 mb-2">AI Routing Complete</p>
                  <h2 className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight mb-3">{recommendation.verdict}</h2>
                  <p className="opacity-80 text-sm leading-relaxed text-slate-700 max-w-xl font-medium">{recommendation.reason}</p>
                </div>
                {recommendation.finalValue > 0 && (
                   <div className="bg-white px-5 py-3 rounded-2xl shadow-sm border border-slate-100 hidden sm:block shrink-0 text-right">
                     <p className="text-[10px] font-black uppercase tracking-widest text-slate-400 mb-1">Locked Value</p>
                     <p className="font-black text-2xl text-emerald-600">₹{recommendation.finalValue.toLocaleString('en-IN')}</p>
                   </div>
                )}
              </div>
            </div>

            {/* Custom Tab Navigation */}
            <div className="flex bg-slate-100/80 p-1.5 rounded-2xl mb-2 overflow-x-auto border border-slate-200/60 hide-scrollbar">
              {['Sell', 'Repair', 'Donate', 'Recycle'].map(tab => (
                <button 
                  key={tab} 
                  onClick={() => setActiveTab(tab)} 
                  className={`flex-1 min-w-[80px] py-2.5 text-sm font-bold rounded-xl transition-all ${
                    activeTab === tab 
                      ? 'bg-white text-slate-900 shadow-sm ring-1 ring-slate-900/5' 
                      : 'text-slate-500 hover:text-slate-700 hover:bg-slate-200/50'
                  }`}
                >
                  {tab}
                </button>
              ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              
              {/* Online Platforms */}
              <div className="bg-white p-5 rounded-3xl border border-slate-200/60 shadow-sm">
                <h3 className="text-xs font-black text-slate-500 mb-4 uppercase tracking-widest flex items-center gap-2">🌐 Top Online Platforms</h3>
                <div className="space-y-3">
                  {currentPlatforms.length > 0 ? currentPlatforms.map((platform, idx) => (
                    <div 
                      key={idx} 
                      onClick={() => window.open(platform.url, '_blank')}
                      className="p-4 rounded-2xl border border-slate-100 bg-slate-50 cursor-pointer hover:bg-white hover:border-emerald-200 hover:shadow-md transition-all group active:scale-[0.98]"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <p className="font-bold text-slate-800 group-hover:text-emerald-700 transition-colors">{platform.name}</p>
                        <ExternalLink size={14} className="text-slate-400 group-hover:text-emerald-500" />
                      </div>
                      <p className="text-xs text-slate-500 font-medium mb-3">{platform.desc || "Verified Platform"}</p>
                      <div className="flex flex-wrap gap-1.5">
                        {(platform.features || []).map((f, i) => (
                          <span key={i} className="text-[9px] font-bold uppercase tracking-wider bg-white text-slate-600 px-2 py-1 rounded border border-slate-100">{f}</span>
                        ))}
                      </div>
                    </div>
                  )) : (
                    <p className="text-sm text-slate-400 font-medium p-4 text-center">No online platforms available.</p>
                  )}
                </div>
              </div>

              {/* Offline Hubs */}
              <div className="bg-white p-5 rounded-3xl border border-slate-200/60 shadow-sm">
                 <h3 className="text-xs font-black text-slate-500 mb-4 uppercase tracking-widest flex items-center gap-2">
                    <MapPin size={14} className="text-emerald-500"/> Verified Local Hubs
                 </h3>
                 <div className="space-y-3">
                   {currentHubs.length > 0 ? currentHubs.map((fac, idx) => (
                      <div 
                        key={idx} 
                        onClick={() => setSelectedLocation(fac)}
                        className="flex items-center justify-between p-4 rounded-2xl border border-slate-100 bg-slate-50 cursor-pointer hover:bg-emerald-50/50 hover:border-emerald-200 hover:shadow-md transition-all group active:scale-[0.98]"
                      >
                        <div className="pr-4">
                          <p className="font-bold text-slate-800 group-hover:text-emerald-700 transition-colors">{fac.name}</p>
                          <p className="text-xs text-slate-500 mt-1 font-medium leading-relaxed">{fac.address}</p>
                        </div>
                        <div className="bg-white shadow-sm border border-slate-100 p-2 rounded-full group-hover:bg-emerald-100 group-hover:border-emerald-200 transition-colors shrink-0">
                            <MapPin size={16} className="text-slate-400 group-hover:text-emerald-600" />
                        </div>
                      </div>
                   )) : (
                     <p className="text-sm text-slate-400 font-medium p-4 text-center">No local hubs found.</p>
                   )}
                 </div>
              </div>
            </div>

            {/* AI Verification Block */}
            <div className="mt-8 bg-slate-900 rounded-3xl p-6 sm:p-8 text-white relative overflow-hidden shadow-xl">
               <div className="absolute -right-10 -bottom-10 opacity-10">
                 <ShieldCheck size={150} />
               </div>
               
               <div className="relative z-10 max-w-lg">
                 <h3 className="text-xl font-black mb-2 flex items-center gap-2">
                    Claim Your Eco-Points <Trophy className="text-amber-400" size={20} />
                 </h3>
                 <p className="text-sm text-slate-400 font-medium mb-6 leading-relaxed">
                   Did you successfully {activeTab.toLowerCase()} this item? Upload a photo of your receipt, chat, or drop-off to earn up to 500 leaderboard points.
                 </p>

                 {verificationResult ? (
                   <div className={`p-4 rounded-2xl border backdrop-blur-sm ${verificationResult.verified ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-100' : 'bg-red-500/20 border-red-500/50 text-red-100'}`}>
                     <p className="font-bold mb-1 flex items-center gap-2">
                        {verificationResult.verified ? <CheckCircle size={18} className="text-emerald-400"/> : <ShieldAlert size={18} className="text-red-400"/>}
                        {verificationResult.message}
                     </p>
                     {verificationResult.verified && (
                        <p className="text-xs opacity-80 mt-2 font-medium bg-black/20 p-2 rounded-xl inline-block">
                          AI Verification: {verificationResult.details?.reasoning}
                        </p>
                     )}
                   </div>
                 ) : (
                   <label className="flex items-center justify-center gap-3 w-full sm:w-auto px-6 py-4 bg-white/10 hover:bg-white/20 border border-white/20 rounded-2xl cursor-pointer transition-all active:scale-[0.98] font-bold text-sm group">
                     {verifying ? (
                       <><Loader2 className="animate-spin text-emerald-400" size={18} /> Verifying Proof...</>
                     ) : (
                       <><UploadCloud size={18} className="text-emerald-400 group-hover:-translate-y-0.5 transition-transform"/> Upload Proof Image</>
                     )}
                     <input type="file" accept="image/*" onChange={handleVerificationUpload} disabled={verifying} className="hidden" />
                   </label>
                 )}
               </div>
            </div>

          </div>
        )}

      </div>
    </div>
  );
};

export default AddWaste;
import React, { useState, useEffect } from "react";
import { Coins, Leaf, Loader2, MapPin, Sparkles, ExternalLink, X, Camera, Zap, CheckCircle, ShieldAlert, Star, Globe, Clock, ShieldCheck, MessageSquare } from "lucide-react";
import api from "../api/axios";

// Verified Platforms Data
const verifiedPlatforms = {
  Sell: [
    { id: 'p1', name: "Cashify", url: "https://www.cashify.in", desc: "Best for electronics and gadgets.", rating: 4.6, speed: "Instant", features: ["Free Doorstep Pickup", "Instant Cash", "No Haggling"] },
    { id: 'p2', name: "OLX", url: "https://www.olx.in", desc: "Best for furniture, appliances, and general items.", rating: 4.2, speed: "1-3 Days", features: ["Local Buyers", "Set Your Own Price", "Direct Chat"] }
  ],
  Repair: [
    { id: 'p3', name: "Urban Company", url: "https://www.urbancompany.com/", desc: "At-home repair for appliances and furniture.", rating: 4.8, speed: "Same Day", features: ["Background Checked Techs", "90-Day Guarantee", "Transparent Pricing"] },
    { id: 'p4', name: "Onsitego", url: "https://onsitego.com/", desc: "Verified doorstep repair for electronics.", rating: 4.5, speed: "24-48 Hours", features: ["Genuine Parts", "Free Pickup & Drop", "Device Tracking"] }
  ],
  Donate: [
    { id: 'p5', name: "Goonj", url: "https://goonj.org/", desc: "Donate clothes, toys, and household goods.", rating: 4.9, speed: "Drop-off", features: ["National Impact", "Tax Benefits (80G)", "Transparent Operations"] },
    { id: 'p6', name: "Share At Door Step", url: "https://sadsindia.org/", desc: "Convenient doorstep donation pickups.", rating: 4.6, speed: "Scheduled", features: ["Convenient Pickup", "Rewards Program", "Supports NGOs"] }
  ],
  Recycle: [
    { id: 'p7', name: "Namo E-Waste", url: "https://namoewaste.com/", desc: "Certified e-waste recycling.", rating: 4.7, speed: "Scheduled", features: ["Govt Certified", "Data Destruction", "Zero Landfill Policy"] },
    { id: 'p8', name: "The Kabadiwala", url: "https://www.thekabadiwala.com/", desc: "Scrap pickup for paper, plastic, metal.", rating: 4.5, speed: "Same Day", features: ["Digital Weighing", "Instant Payment", "Eco-Friendly Routing"] }
  ]
};

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
  
  // UI Routing & Modal State
  const [activeTab, setActiveTab] = useState("Sell");
  const [facilities, setFacilities] = useState([]);
  const [selectedLocation, setSelectedLocation] = useState(null); 
  const [selectedPlatform, setSelectedPlatform] = useState(null);

  // Dynamic Loading Messages Effect
  useEffect(() => {
    let interval;
    if (loading) {
      const msgs = ["Scanning image...", "Identifying components...", "Calculating market value...", "Consulting database..."];
      let i = 0;
      setLoadingMsg(msgs[0]);
      interval = setInterval(() => {
        i = (i + 1) % msgs.length;
        setLoadingMsg(msgs[i]);
      }, 2000); // Changes every 2 seconds
    } else {
      setLoadingMsg("Run AI Intelligence");
    }
    return () => clearInterval(interval);
  }, [loading]);

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;

    // --- Frontend 15MB Size Check (Network Speed Protection) ---
    const MAX_SIZE_MB = 15;
    const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;
    
    const validFiles = [];
    for (const file of files) {
      if (file.size > MAX_SIZE_BYTES) {
        setError(`Whoops! "${file.name}" is too large (${(file.size/1024/1024).toFixed(1)}MB). Please upload a picture under 15MB.`);
        return; // Stop the upload entirely
      }
      validFiles.push(file);
    }
    // -----------------------------------------------------------

    setImageFiles(prev => [...prev, ...validFiles]);
    setPreviewUrls(prev => [...prev, ...validFiles.map(file => URL.createObjectURL(file))]);
    setStep(1); setAiReport(null); setError(""); setAnswers({});
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
    
    // Optimize Payload: ONLY send the image if this is the first analysis turn.
    if (!previousAnswers && imageFiles.length > 0) {
      imageFiles.forEach(file => formData.append("image", file));
    }
    
    // Pass text context if we are in a follow-up loop
    if (previousAnswers) {
        formData.append("item_text", aiReport?.name || "");
        formData.append("user_answers", JSON.stringify(previousAnswers));
    }

    try {
      const response = await api.post("/waste/diagnose", formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
      });
      const data = response.data.data;

      // Handle the new diagnostic loop logic
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
      console.error(err);
      if (err.response && err.response.data && err.response.data.detail) {
        setError(err.response.data.detail);
      } else {
        setError("AI Engine failed to process the diagnostic. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (idx, value) => {
      setAnswers(prev => ({...prev, [idx]: value}));
  };

  const submitAnswers = () => {
      // Map user answers to the actual AI questions to send back for final valuation
      const formattedAnswers = aiReport.questions.map((q, idx) => `Q: ${q} | A: ${answers[idx]}`);
      runDiagnostic(formattedAnswers);
      setAnswers({}); // Clear answers immediately for potential follow-ups
  };

  const generateFinalVerdict = () => {
    setLoading(true);
    setTimeout(() => {
      let action = "Recycle";
      let verdict = "Recycle Safely";
      let reason = aiReport?.insight || "This item has reached the end of its lifecycle and should be responsibly recycled.";
      
      const val = aiReport.finalValue;

      if (val > 1500 && aiReport.category !== 'appliance') {
        action = "Sell"; verdict = "Highly Sellable";
      } else if (val > 500 && val <= 1500) {
        action = "Donate"; verdict = "Perfect for Donation";
      } else if (aiReport.category.includes("ewaste") && val > 2000) {
        action = "Repair"; verdict = "Repair Recommended";
      }

      setRecommendation({ action, verdict, reason, finalValue: val });
      setActiveTab(action);
      
      setFacilities([
        { id: 1, name: `City ${action} Hub`, address: "Sector 4, Main Road", distance: "1.2 km", rating: 4.8, accepts: `${aiReport.category}, Mixed Materials` },
        { id: 2, name: `Eco ${action} Drop-off`, address: "Industrial Area Phase 1", distance: "3.5 km", rating: 4.2, accepts: "All Household Items & Electronics" }
      ]);
      
      setStep(3);
      setLoading(false);
    }, 800);
  };

  return (
    <div className="max-w-4xl mx-auto p-4 md:p-6 space-y-8">
      <header>
        <h1 className="text-3xl font-extrabold text-slate-900 flex items-center gap-2">
          <Sparkles className="text-emerald-500" /> AI Assessor
        </h1>
        <p className="text-slate-500 mt-2">Upload any item. The AI will adapt, assess, and recommend the best path.</p>
      </header>

      <div className="flex items-center gap-2 mb-8">
        {[1, 2, 3].map(i => (
          <div key={i} className={`h-2 rounded-full transition-all ${step >= i ? 'bg-emerald-500 w-16' : 'bg-slate-200 w-8'}`} />
        ))}
      </div>

      <div className="grid grid-cols-1 gap-8">
        
        {/* ================= STEP 1: UPLOAD ================= */}
        {step === 1 && (
          <div className="bg-white rounded-3xl p-8 shadow-xl border border-slate-100">
            <div className={`relative w-full min-h-[200px] rounded-2xl border-2 border-dashed p-4 mb-6 ${previewUrls.length > 0 ? 'border-emerald-400 bg-emerald-50/10' : 'border-slate-300 bg-slate-50'}`}>
              {previewUrls.length > 0 ? (
                <div className="grid grid-cols-3 md:grid-cols-4 gap-4">
                  {previewUrls.map((url, idx) => (
                    <div key={idx} className="relative aspect-square rounded-xl overflow-hidden shadow-sm">
                      <img src={url} alt={`Preview`} className="w-full h-full object-cover" />
                      <button onClick={() => removeImage(idx)} className="absolute top-1 right-1 p-1 bg-red-500 text-white rounded-full"><X size={14} /></button>
                    </div>
                  ))}
                  <label className="cursor-pointer aspect-square rounded-xl border-2 border-dashed border-emerald-300 flex flex-col items-center justify-center text-emerald-600 hover:bg-emerald-50 transition-colors">
                    <Camera size={24} />
                    <span className="text-xs font-bold mt-1">Add Angle</span>
                    <input type="file" accept="image/*" multiple onChange={handleFileChange} className="hidden" />
                  </label>
                </div>
              ) : (
                <label className="absolute inset-0 flex flex-col items-center justify-center cursor-pointer text-center p-6 group">
                  <Camera className="mx-auto h-12 w-12 text-slate-300 mb-3 group-hover:text-emerald-500 transition-colors" />
                  <p className="text-base font-bold text-slate-600">Scan Any Item</p>
                  <p className="text-sm text-slate-400 mt-1">Phones, furniture, clothes, or recyclables.</p>
                  <input type="file" accept="image/*" multiple onChange={handleFileChange} className="hidden" />
                </label>
              )}
            </div>
            
            {error && (
               <div className="bg-red-50 text-red-700 p-4 rounded-xl mb-6 border border-red-200 text-sm font-bold flex items-center gap-3 animate-in fade-in">
                 <ShieldAlert className="shrink-0" size={20} />
                 <p>{error}</p>
               </div>
            )}
            
            <button onClick={() => runDiagnostic()} disabled={imageFiles.length === 0 || loading} className={`w-full font-bold py-4 rounded-xl flex justify-center gap-2 transition-all ${imageFiles.length === 0 ? 'bg-slate-200 text-slate-400 cursor-not-allowed' : 'bg-emerald-600 hover:bg-emerald-700 text-white shadow-lg shadow-emerald-200'}`}>
              {loading ? <Loader2 className="animate-spin" /> : <Zap />} {loadingMsg}
            </button>
          </div>
        )}

        {/* ================= STEP 2: DYNAMIC ASSESSMENT ================= */}
        {step === 2 && aiReport && (
          <div className="bg-slate-900 rounded-3xl p-8 shadow-2xl text-white relative overflow-hidden animate-in slide-in-from-right-8 duration-500">
            <div className="flex flex-col md:flex-row justify-between items-start mb-6 gap-4">
              <div>
                <span className="text-[10px] uppercase font-bold px-2 py-1 rounded-md bg-blue-500/20 text-blue-400 border border-blue-500/30 mb-3 inline-block">
                  {aiReport.category}
                </span>
                <h3 className="text-3xl font-extrabold">{aiReport.name}</h3>
                {aiReport.insight && <p className="text-slate-400 text-sm mt-2 max-w-md">{aiReport.insight}</p>}
              </div>
              <div className="md:text-right bg-slate-800/50 p-4 rounded-2xl border border-slate-700 w-full md:w-auto">
                <p className="text-[10px] text-slate-400 uppercase tracking-wider mb-1">
                    {aiReport.status === 'complete' ? 'Final Locked Value' : 'Est. Market Range'}
                </p>
                <p className="text-2xl sm:text-3xl font-bold text-emerald-400 transition-all duration-500">
                    {aiReport.status === 'complete' 
                        ? `₹${aiReport.finalValue.toLocaleString('en-IN')}`
                        : `₹${aiReport.range[0].toLocaleString('en-IN')} - ₹${aiReport.range[1].toLocaleString('en-IN')}`
                    }
                </p>
              </div>
            </div>

            {aiReport.status === 'needs_info' ? (
                <div className="space-y-4 mb-8">
                <p className="text-sm text-slate-300 mb-4 flex items-center gap-2"><MessageSquare size={16}/> The AI needs context to lock in the final price:</p>
                {aiReport.questions.map((q, idx) => (
                    <div key={idx} className="flex flex-col justify-between items-start bg-white/5 p-4 rounded-xl border border-white/10 gap-3">
                    <p className="text-sm font-medium flex-1">{q}</p>
                    <input 
                        type="text" 
                        placeholder="Type your answer..." 
                        value={answers[idx] || ""}
                        autoFocus={idx === 0}
                        onChange={(e) => handleAnswerChange(idx, e.target.value)}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' && Object.keys(answers).length === aiReport.questions.length) {
                                submitAnswers();
                            }
                        }}
                        className="w-full bg-slate-800 border border-slate-600 rounded-lg p-3 text-sm text-white focus:outline-none focus:border-emerald-500 transition-colors"
                    />
                    </div>
                ))}
                
                <button 
                    onClick={submitAnswers} 
                    disabled={loading || Object.keys(answers).length < aiReport.questions.length} 
                    className="w-full font-bold py-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white flex justify-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-xl mt-4"
                >
                    {loading ? <Loader2 className="animate-spin" /> : <Zap />} {loading ? loadingMsg : "Analyze Answers"}
                </button>
                </div>
            ) : (
                <button onClick={generateFinalVerdict} disabled={loading} className="w-full font-bold py-4 rounded-xl bg-blue-600 hover:bg-blue-700 text-white flex justify-center gap-2 transition-all shadow-xl">
                  {loading ? <Loader2 className="animate-spin" /> : <CheckCircle />} {loading ? "Generating Action Plan..." : "Generate Action Plan"}
                </button>
            )}
          </div>
        )}

        {/* ================= STEP 3: ACTION ROUTER ================= */}
        {step === 3 && recommendation && (
          <div className="space-y-6 animate-in slide-in-from-bottom-8 duration-500">
            
            <div className={`rounded-3xl p-8 shadow-sm border-2 ${
              recommendation.action === 'Sell' ? 'bg-emerald-50 border-emerald-500' :
              recommendation.action === 'Repair' ? 'bg-blue-50 border-blue-500' :
              recommendation.action === 'Donate' ? 'bg-purple-50 border-purple-500' :
              'bg-amber-50 border-amber-500'
            }`}>
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-xs font-bold uppercase tracking-widest opacity-70 mb-2">AI Routing Complete</p>
                  <h2 className="text-4xl font-extrabold mb-4">{recommendation.verdict}</h2>
                </div>
                {recommendation.finalValue > 0 && (
                   <div className="bg-white px-4 py-2 rounded-xl shadow-sm border opacity-90 hidden sm:block">
                     <p className="text-[10px] font-bold uppercase tracking-wider opacity-60">Locked Value</p>
                     <p className="font-extrabold text-lg text-emerald-700">₹{recommendation.finalValue.toLocaleString('en-IN')}</p>
                   </div>
                )}
              </div>
              <p className="opacity-80 text-sm leading-relaxed max-w-2xl">{recommendation.reason}</p>
            </div>

            <div className="bg-white rounded-3xl p-6 md:p-8 shadow-xl border border-slate-100">
              <div className="flex bg-slate-100 p-1 rounded-xl mb-8 overflow-x-auto">
                {['Sell', 'Repair', 'Donate', 'Recycle'].map(tab => (
                  <button key={tab} onClick={() => setActiveTab(tab)} className={`flex-1 min-w-[80px] py-3 text-sm font-bold rounded-lg transition-all ${activeTab === tab ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-400 hover:text-slate-600'}`}>{tab}</button>
                ))}
              </div>

              {/* Verified Online Platforms (Triggers Popup) */}
              <div className="mb-8">
                <h3 className="text-sm font-bold text-slate-800 mb-4 flex items-center gap-2">🌐 Verified Online Platforms</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {verifiedPlatforms[activeTab]?.map((platform) => (
                    <div 
                      key={platform.id} 
                      onClick={() => setSelectedPlatform(platform)}
                      className="flex items-start gap-3 p-4 rounded-xl border border-slate-200 hover:border-blue-400 bg-slate-50 cursor-pointer transition-all group hover:shadow-md"
                    >
                      <div className="flex-1">
                        <p className="font-bold text-slate-800 flex items-center gap-2 group-hover:text-blue-700">{platform.name}</p>
                        <p className="text-xs text-slate-500 mt-1">{platform.desc}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Nearby Offline Locations (Triggers Popup) */}
              <div>
                 <h3 className="text-sm font-bold text-slate-800 mb-4 flex items-center gap-2"><MapPin size={18} className="text-red-500"/> Nearby Verified Drop-offs</h3>
                 <div className="space-y-3">
                   {facilities.map((fac) => (
                      <div 
                        key={fac.id} 
                        onClick={() => setSelectedLocation(fac)}
                        className="flex items-center justify-between p-4 rounded-xl border border-slate-200 bg-slate-50 cursor-pointer hover:border-emerald-400 hover:bg-emerald-50/50 hover:shadow-md transition-all group"
                      >
                        <div>
                          <p className="font-bold text-slate-800 group-hover:text-emerald-800">{fac.name}</p>
                          <p className="text-xs text-slate-500 mt-1">{fac.address}</p>
                        </div>
                        <span className="inline-block px-3 py-1 bg-white border border-slate-200 text-slate-700 text-xs font-bold rounded-full shadow-sm">{fac.distance}</span>
                      </div>
                    ))}
                 </div>
              </div>
            </div>
            
            <button onClick={() => setStep(1)} className="w-full py-4 text-slate-500 font-bold hover:text-slate-800 transition-colors">Scan Another Item</button>
          </div>
        )}

        {selectedPlatform && (
          <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4" onClick={() => setSelectedPlatform(null)}>
            <div className="bg-white rounded-3xl p-6 md:p-8 max-w-md w-full relative shadow-2xl animate-in zoom-in-95 duration-200" onClick={e => e.stopPropagation()}>
              <button className="absolute top-4 right-4 p-2 bg-slate-100 text-slate-500 hover:bg-red-100 hover:text-red-600 rounded-full transition-colors" onClick={() => setSelectedPlatform(null)}>
                <X size={20} />
              </button>
              
              <div className="mb-6 pr-8">
                <span className="inline-block bg-blue-100 text-blue-700 text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded-md mb-3 flex items-center w-fit gap-1"><ShieldCheck size={12}/> Verified Partner</span>
                <h2 className="text-2xl font-extrabold text-slate-900 mb-2 leading-tight">{selectedPlatform.name}</h2>
                <p className="text-sm text-slate-500">{selectedPlatform.desc}</p>
              </div>
              
              <div className="flex gap-3 mb-6">
                <div className="flex-1 bg-amber-50 p-3 rounded-2xl border border-amber-100">
                  <p className="text-[10px] text-amber-600 font-bold uppercase tracking-wider mb-1">Trust Score</p>
                  <p className="font-bold text-amber-900 flex items-center gap-1 text-lg"><Star size={16} className="fill-amber-500 text-amber-500"/> {selectedPlatform.rating}</p>
                </div>
                <div className="flex-1 bg-blue-50 p-3 rounded-2xl border border-blue-100">
                  <p className="text-[10px] text-blue-600 font-bold uppercase tracking-wider mb-1">Timeline</p>
                  <p className="font-bold text-blue-900 flex items-center gap-1 text-lg"><Clock size={16} className="text-blue-600"/> {selectedPlatform.speed}</p>
                </div>
              </div>

              <div className="bg-slate-50 p-4 rounded-2xl border border-slate-100 mb-6 space-y-2">
                <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider mb-2">Why choose them?</p>
                {selectedPlatform.features.map((feature, idx) => (
                  <p key={idx} className="text-sm font-medium text-slate-800 flex items-center gap-2"><CheckCircle size={14} className="text-emerald-500"/> {feature}</p>
                ))}
              </div>
              
              <a href={selectedPlatform.url} target="_blank" rel="noreferrer" className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 rounded-xl flex items-center justify-center gap-2 transition-all shadow-lg shadow-blue-200">
                <Globe size={18} /> Visit {selectedPlatform.name} Website
              </a>
            </div>
          </div>
        )}

        {selectedLocation && (
          <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4" onClick={() => setSelectedLocation(null)}>
            <div className="bg-white rounded-3xl p-6 md:p-8 max-w-md w-full relative shadow-2xl animate-in zoom-in-95 duration-200" onClick={e => e.stopPropagation()}>
              <button className="absolute top-4 right-4 p-2 bg-slate-100 text-slate-500 hover:bg-red-100 hover:text-red-600 rounded-full transition-colors" onClick={() => setSelectedLocation(null)}>
                <X size={20} />
              </button>
              
              <div className="mb-6 pr-8">
                <h2 className="text-2xl font-extrabold text-slate-900 mb-2 leading-tight">{selectedLocation.name}</h2>
                <p className="text-sm text-slate-500 flex items-start gap-1"><MapPin size={16} className="shrink-0 mt-0.5 text-slate-400"/> {selectedLocation.address}</p>
              </div>
              
              <div className="flex gap-3 mb-6">
                <div className="flex-1 bg-amber-50 p-3 rounded-2xl border border-amber-100">
                  <p className="text-[10px] text-amber-600 font-bold uppercase tracking-wider mb-1">Rating</p>
                  <p className="font-bold text-amber-900 flex items-center gap-1 text-lg"><Star size={16} className="fill-amber-500 text-amber-500"/> {selectedLocation.rating}</p>
                </div>
                <div className="flex-1 bg-emerald-50 p-3 rounded-2xl border border-emerald-100">
                  <p className="text-[10px] text-emerald-600 font-bold uppercase tracking-wider mb-1">Distance</p>
                  <p className="font-bold text-emerald-900 text-lg">{selectedLocation.distance}</p>
                </div>
              </div>
              
              <div className="bg-slate-50 p-4 rounded-2xl border border-slate-100 mb-6">
                <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider mb-2">Accepts Materials</p>
                <p className="text-sm font-medium text-slate-800">{selectedLocation.accepts}</p>
              </div>
              
              <a href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(selectedLocation.name + ' ' + selectedLocation.address)}`} target="_blank" rel="noreferrer" className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-4 rounded-xl flex items-center justify-center gap-2 transition-all shadow-lg shadow-emerald-200">
                <MapPin size={18} /> Get Directions in Maps
              </a>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AddWaste;
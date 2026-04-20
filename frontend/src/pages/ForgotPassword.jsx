import React, { useState } from "react";
import { Link } from "react-router-dom";
import { Leaf, Mail, Loader2, ArrowLeft, CheckCircle } from "lucide-react";
import api from "../api/axios";

const ForgotPassword = () => {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");

  const handleResetRequest = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    
    try {
      await api.post("/auth/forgot-password", { email });
      setSuccess(true);
    } catch (err) {
      setError("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F4F7F9] flex flex-col justify-center py-12 sm:px-6 lg:px-8 selection:bg-emerald-200">
      <div className="sm:mx-auto sm:w-full sm:max-w-md animate-in slide-in-from-bottom-4 duration-700">
        <div className="flex justify-center mb-6">
          <div className="bg-slate-200 p-3 rounded-2xl">
            <Lock className="text-slate-600 h-8 w-8" />
          </div>
        </div>
        <h2 className="text-center text-3xl font-black tracking-tight text-slate-900">
          Reset Password
        </h2>
        <p className="mt-2 text-center text-sm font-medium text-slate-500">
          Enter your email to receive a reset link.
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md animate-in fade-in duration-700 delay-150">
        <div className="bg-white py-8 px-4 shadow-2xl shadow-slate-200/50 sm:rounded-3xl sm:px-10 border border-slate-100">
          
          {success ? (
            <div className="text-center animate-in zoom-in-95">
              <CheckCircle className="mx-auto h-12 w-12 text-emerald-500 mb-4" />
              <h3 className="text-lg font-black text-slate-900 mb-2">Check your inbox</h3>
              <p className="text-sm text-slate-500 font-medium mb-6">
                If an account exists for <span className="font-bold text-slate-700">{email}</span>, we've sent instructions to reset your password.
              </p>
              <Link to="/login" className="w-full flex justify-center items-center gap-2 py-3.5 px-4 rounded-xl text-sm font-black text-slate-700 bg-slate-100 hover:bg-slate-200 transition-all">
                <ArrowLeft size={18}/> Back to Login
              </Link>
            </div>
          ) : (
            <form className="space-y-6" onSubmit={handleResetRequest}>
              {error && <p className="text-red-600 text-sm font-bold bg-red-50 p-3 rounded-lg text-center">{error}</p>}
              
              <div>
                <label className="block text-xs font-black text-slate-500 uppercase tracking-widest mb-2">Email Address</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Mail className="h-5 w-5 text-slate-400" />
                  </div>
                  <input
                    type="email" required
                    value={email} onChange={(e) => setEmail(e.target.value)}
                    className="block w-full pl-11 pr-3 py-3 border border-slate-200 rounded-xl text-slate-900 bg-slate-50 focus:ring-2 focus:ring-emerald-500 focus:bg-white transition-all font-medium sm:text-sm"
                    placeholder="you@example.com"
                  />
                </div>
              </div>

              <button
                type="submit" disabled={loading || !email}
                className="w-full flex justify-center items-center gap-2 py-3.5 px-4 rounded-xl shadow-lg shadow-emerald-500/20 text-sm font-black text-white bg-emerald-600 hover:bg-emerald-500 transition-all active:scale-95 disabled:opacity-70"
              >
                {loading ? <Loader2 className="animate-spin h-5 w-5" /> : "Send Reset Link"}
              </button>

              <div className="mt-4 text-center">
                <Link to="/login" className="text-sm font-bold text-slate-500 hover:text-slate-800 transition-colors">
                  Cancel
                </Link>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;
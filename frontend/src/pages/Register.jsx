import React, { useRef, useState, useMemo } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api/axios";

const Register = () => {
  const navigate = useNavigate();
  const nameRef = useRef(null);
  const emailRef = useRef(null);
  const otpRef = useRef(null);
  const passwordRef = useRef(null);

  // Core State
  const [step, setStep] = useState(1);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [password, setPassword] = useState("");
  
  // Security & UX State
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [otpAttempts, setOtpAttempts] = useState(0);
  const MAX_ATTEMPTS = 5;

  // Validations
  const isEmailValid = email.includes("@");
  const isPasswordValid = password.length >= 8;
  const isOtpValid = otp.length === 6;

  const isStep1Valid = useMemo(() => name.trim() !== "" && email.trim() !== "" && isEmailValid, [name, email, isEmailValid]);
  const isStep2Valid = useMemo(() => isOtpValid, [isOtpValid]);
  const isStep3Valid = useMemo(() => password.trim() !== "" && isPasswordValid, [password, isPasswordValid]);

  // ================= STEP 1: SEND OTP =================
  const handleSendOTP = async (event) => {
    event.preventDefault();
    if (!isStep1Valid) {
      setError("Please enter a valid name and email.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      await api.post("/auth/send-otp", { name: name.trim(), email: email.trim() });
      setSuccess("Verification code sent! Please check your inbox.");
      setOtpAttempts(0); // Reset attempts
      setStep(2);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to send OTP. Email may already be in use.");
    } finally {
      setLoading(false);
    }
  };

  // ================= STEP 2: VERIFY OTP =================
  const handleVerifyOTP = async (event) => {
    event.preventDefault();
    if (otpAttempts >= MAX_ATTEMPTS) {
      setError("Maximum attempts reached. Please go back and request a new code.");
      return;
    }

    setLoading(true);
    setError("");
    try {
      await api.post("/auth/verify-otp", { email: email.trim(), otp: otp.trim() });
      setSuccess("Identity verified! You may now create a secure password.");
      setStep(3); // Unlocks the password creation step
    } catch (err) {
      const newAttempts = otpAttempts + 1;
      setOtpAttempts(newAttempts);
      if (newAttempts >= MAX_ATTEMPTS) {
        setError("Maximum attempts reached. Please go back and request a new code.");
      } else {
        setError(`Invalid OTP. You have ${MAX_ATTEMPTS - newAttempts} attempts remaining.`);
      }
    } finally {
      setLoading(false);
    }
  };

  // ================= STEP 3: CREATE ACCOUNT =================
  const handleRegister = async (event) => {
    event.preventDefault();
    if (!isStep3Valid) {
      setError("Please ensure your password is at least 8 characters.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const response = await api.post("/auth/register", {
        name: name.trim(),
        email: email.trim(),
        password,
        otp: otp.trim()
      });
      
      const payload = response?.data?.data ?? response?.data ?? {};
      const accessToken = payload.access_token ?? payload.token;
      
      if (accessToken) {
        localStorage.setItem("token", accessToken);
        navigate("/dashboard");
      } else {
        navigate("/login", { state: { message: "Account created successfully! Please log in." } });
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // Keyboard Handlers
  const handleNameKeyDown = (e) => { if (e.key === "Enter") { e.preventDefault(); emailRef.current?.focus(); } };
  const handleEmailKeyDown = (e) => { if (e.key === "Enter" && isStep1Valid) handleSendOTP(e); };
  const handleOtpKeyDown = (e) => { if (e.key === "Enter" && isStep2Valid) handleVerifyOTP(e); };
  const handlePasswordKeyDown = (e) => { if (e.key === "Enter" && isStep3Valid) handleRegister(e); };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-b from-gray-50 via-emerald-50/30 to-white px-4 text-slate-900">
      <div className="w-full max-w-md rounded-xl border border-gray-200 bg-white p-6 shadow-sm transition-all duration-200 relative overflow-hidden">
        
        {/* Progress Bar Header */}
        <div className="absolute top-0 left-0 w-full h-1 bg-gray-100">
          <div className={`h-full bg-emerald-500 transition-all duration-500 ${step === 1 ? 'w-1/3' : step === 2 ? 'w-2/3' : 'w-full'}`}></div>
        </div>

        <div className="mb-6 mt-2">
          <p className="text-xs font-medium uppercase tracking-wide text-emerald-700">AVARTAN</p>
          <h1 className="mt-2 text-2xl font-semibold text-slate-900">Create account</h1>
          <p className="mt-1 text-sm text-gray-600">
            {step === 1 && "Join AVARTAN and start tracking your impact."}
            {step === 2 && "We need to verify your email address."}
            {step === 3 && "Create a secure password to finish."}
          </p>
        </div>

        {error && <p className="mb-4 text-sm font-medium text-red-500 bg-red-50 p-3 rounded-lg border border-red-100">{error}</p>}
        {success && !error && <p className="mb-4 text-sm font-medium text-emerald-700 bg-emerald-50 p-3 rounded-lg border border-emerald-100">{success}</p>}

        {/* STEP 1: Name and Email */}
        {step === 1 && (
          <form className="space-y-4 animate-in slide-in-from-left-4" onSubmit={handleSendOTP}>
            <div>
              <label className="mb-1 block text-sm text-gray-700">Full Name</label>
              <input
                ref={nameRef} type="text" value={name} onChange={(e) => setName(e.target.value)} onKeyDown={handleNameKeyDown}
                placeholder="Niket Patel" disabled={loading}
                className="w-full rounded-lg border border-gray-200 bg-white px-3 py-2.5 text-sm text-slate-900 placeholder:text-gray-400 transition-all focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm text-gray-700">Email</label>
              <input
                ref={emailRef} type="email" value={email} onChange={(e) => setEmail(e.target.value)} onKeyDown={handleEmailKeyDown}
                placeholder="you@example.com" disabled={loading}
                className="w-full rounded-lg border border-gray-200 bg-white px-3 py-2.5 text-sm text-slate-900 placeholder:text-gray-400 transition-all focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
            <button
              type="submit" disabled={!isStep1Valid || loading}
              className="w-full rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-medium text-white transition-all hover:bg-emerald-700 focus:ring-2 focus:ring-emerald-500 disabled:opacity-50 mt-2"
            >
              {loading ? "Sending Code..." : "Continue"}
            </button>
          </form>
        )}

        {/* STEP 2: OTP Verification (HIDDEN INPUT) */}
        {step === 2 && (
          <form className="space-y-4 animate-in slide-in-from-right-4" onSubmit={handleVerifyOTP}>
            <div>
              <label className="mb-1 block text-sm text-gray-700">6-Digit Verification Code</label>
              <input
                ref={otpRef} 
                type="password" /* Hides the OTP */
                maxLength="6" 
                value={otp} 
                onChange={(e) => setOtp(e.target.value)} 
                onKeyDown={handleOtpKeyDown}
                placeholder="••••••" 
                disabled={loading || otpAttempts >= MAX_ATTEMPTS} 
                autoFocus
                className="w-full rounded-lg border border-gray-200 bg-white px-3 py-2.5 text-center tracking-[0.5em] text-lg font-bold text-slate-900 transition-all focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
            
            <div className="flex gap-3 mt-4">
              <button
                type="button" onClick={() => { setStep(1); setError(""); setSuccess(""); }} disabled={loading}
                className="px-4 py-2.5 rounded-lg border border-gray-200 text-sm font-medium text-gray-600 hover:bg-gray-50 transition-all"
              >
                Back
              </button>
              <button
                type="submit" disabled={!isStep2Valid || loading || otpAttempts >= MAX_ATTEMPTS}
                className="flex-1 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-medium text-white transition-all hover:bg-emerald-700 focus:ring-2 focus:ring-emerald-500 disabled:opacity-50"
              >
                {loading ? "Verifying..." : "Verify Code"}
              </button>
            </div>
          </form>
        )}

        {/* STEP 3: Password Creation */}
        {step === 3 && (
          <form className="space-y-4 animate-in slide-in-from-right-4" onSubmit={handleRegister}>
            <div>
              <label className="mb-1 block text-sm text-gray-700">Create Password</label>
              <div className="relative">
                <input
                  ref={passwordRef} type={showPassword ? "text" : "password"} value={password} onChange={(e) => setPassword(e.target.value)} onKeyDown={handlePasswordKeyDown}
                  placeholder="Minimum 8 characters" disabled={loading} autoFocus
                  className={`w-full rounded-lg border bg-white px-3 py-2.5 pr-10 text-sm text-slate-900 placeholder:text-gray-400 transition-all focus:outline-none focus:ring-2 ${password.length > 0 && !isPasswordValid ? "border-red-300 focus:ring-red-500" : "border-gray-200 focus:ring-emerald-500"}`}
                />
                <button
                  type="button" onClick={() => setShowPassword((prev) => !prev)}
                  className="absolute inset-y-0 right-3 flex items-center text-gray-400 hover:text-emerald-600 transition-colors focus:outline-none"
                >
                  {showPassword ? (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                  ) : (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.542-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.542 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" /></svg>
                  )}
                </button>
              </div>
              {password.length > 0 && !isPasswordValid && <p className="mt-1 text-xs text-red-500">Must be at least 8 characters. Currently {password.length}.</p>}
            </div>

            <button
              type="submit" disabled={!isStep3Valid || loading}
              className="w-full rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-medium text-white transition-all hover:bg-emerald-700 focus:ring-2 focus:ring-emerald-500 disabled:opacity-50 mt-2"
            >
              {loading ? "Registering..." : "Create Account"}
            </button>
          </form>
        )}

        <p className="mt-5 text-center text-sm text-gray-600">
          Already have an account?{" "}
          <Link to="/login" className="text-emerald-700 font-medium transition-all hover:text-emerald-800 focus:ring-2 focus:ring-emerald-500">
            Login
          </Link>
        </p>
      </div>
    </div>
  );
};

export default Register;
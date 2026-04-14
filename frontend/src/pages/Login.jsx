import React, { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api/axios";

const Login = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const isEmailValid = email.includes("@");
  const isPasswordValid = password.length >= 6;
  const isFormValid = useMemo(
    () => email.trim() !== "" && password.trim() !== "" && isEmailValid && isPasswordValid,
    [email, password, isEmailValid, isPasswordValid],
  );

  const handleLogin = async (event) => {
    event.preventDefault();

    if (!isEmailValid) {
      setError("Please enter a valid email address.");
      return;
    }
    if (!isPasswordValid) {
      setError("Password must be at least 6 characters.");
      return;
    }

    setLoading(true);
    setError("");
    try {
      const formPayload = new URLSearchParams();
      formPayload.append("username", email.trim());
      formPayload.append("password", password);

      const response = await api.post("/auth/login", formPayload, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });
      const payload = response?.data?.data ?? response?.data ?? {};
      const accessToken = payload.access_token ?? payload.token;
      const userId = payload.user_id ?? payload.id;

      if (!accessToken) {
        throw new Error("Missing access token in login response.");
      }

      localStorage.setItem("token", accessToken);
      if (userId !== undefined && userId !== null) {
        localStorage.setItem("user_id", String(userId));
      }
      navigate("/dashboard");
    } catch {
      setError("Login failed. Please check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-b from-gray-50 via-emerald-50/30 to-white px-4 text-slate-900">
      <div className="w-full max-w-md rounded-xl border border-gray-200 bg-white p-6 shadow-sm transition-all duration-200">
        <div className="mb-6">
          <p className="text-xs font-medium uppercase tracking-wide text-emerald-700">
            AVARTAN
          </p>
          <h1 className="mt-2 text-2xl font-semibold text-slate-900">Welcome back</h1>
          <p className="mt-1 text-sm text-gray-600">
            Sign in to continue your sustainability journey.
          </p>
        </div>

        <form className="space-y-4" onSubmit={handleLogin}>
          <div>
            <label className="mb-1 block text-sm text-gray-700">Email</label>
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@example.com"
              className="w-full rounded-lg border border-gray-200 bg-white px-3 py-2.5 text-sm text-slate-900 placeholder:text-gray-400 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm text-gray-700">Password</label>
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="••••••••"
              className="w-full rounded-lg border border-gray-200 bg-white px-3 py-2.5 text-sm text-slate-900 placeholder:text-gray-400 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>

          {error && <p className="text-sm text-red-400">{error}</p>}

          <button
            type="submit"
            disabled={!isFormValid || loading}
            className="w-full rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-medium text-white transition-all duration-200 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? "Signing in..." : "Login"}
          </button>
        </form>

        <p className="mt-5 text-center text-sm text-gray-600">
          New to AVARTAN?{" "}
          <Link
            to="/register"
            className="text-emerald-700 transition-all duration-200 hover:text-emerald-800 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          >
            Create account
          </Link>
        </p>
      </div>
    </div>
  );
};

export default Login;

import React, { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api/axios";

const Register = () => {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const isEmailValid = email.includes("@");
  const isPasswordValid = password.length >= 8;
  const isFormValid = useMemo(
    () =>
      name.trim() !== "" &&
      email.trim() !== "" &&
      password.trim() !== "" &&
      isEmailValid &&
      isPasswordValid,
    [name, email, password, isEmailValid, isPasswordValid],
  );

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!isFormValid) {
      setError("Please fill valid details before registering.");
      return;
    }

    setLoading(true);
    setError("");
    try {
      const response = await api.post("/auth/register", {
        name: name.trim(),
        email: email.trim(),
        password,
      });
      const payload = response?.data?.data ?? response?.data ?? {};
      const accessToken = payload.access_token ?? payload.token;
      const userId = payload.user_id ?? payload.id;

      if (accessToken) {
        localStorage.setItem("token", accessToken);
      }
      if (userId !== undefined && userId !== null) {
        localStorage.setItem("user_id", String(userId));
      }
      navigate(accessToken ? "/dashboard" : "/login");
    } catch {
      setError("Registration failed. Please try again.");
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
          <h1 className="mt-2 text-2xl font-semibold text-slate-900">Create account</h1>
          <p className="mt-1 text-sm text-gray-600">
            Join AVARTAN and start tracking your impact.
          </p>
        </div>

        <form className="space-y-4" onSubmit={handleSubmit}>
          <div>
            <label className="mb-1 block text-sm text-gray-700">Full Name</label>
            <input
              type="text"
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="Niket Patel"
              className="w-full rounded-lg border border-gray-200 bg-white px-3 py-2.5 text-sm text-slate-900 placeholder:text-gray-400 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>
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
              placeholder="Minimum 6 characters"
              className="w-full rounded-lg border border-gray-200 bg-white px-3 py-2.5 text-sm text-slate-900 placeholder:text-gray-400 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>

          {error && <p className="text-sm text-red-500">{error}</p>}

          <button
            type="submit"
            disabled={!isFormValid || loading}
            className="w-full rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-medium text-white transition-all duration-200 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? "Creating account..." : "Register"}
          </button>
        </form>

        <p className="mt-5 text-center text-sm text-gray-600">
          Already have an account?{" "}
          <Link
            to="/login"
            className="text-emerald-700 transition-all duration-200 hover:text-emerald-800 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          >
            Login
          </Link>
        </p>
      </div>
    </div>
  );
};

export default Register;

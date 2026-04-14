import React, { useEffect, useState } from "react";
import { ArrowRight, Brain, Leaf, Route, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";

const featureCardClass =
  "rounded-xl border border-gray-200 bg-white p-6 shadow-sm transition-all duration-200 hover:scale-[1.02] hover:border-emerald-500/30 hover:shadow-md";

const Landing = () => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  const token = localStorage.getItem("token");
  const isLoggedIn = Boolean(token);

  const primaryCtaPath = isLoggedIn ? "/dashboard" : "/login";

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 via-emerald-50/30 to-white text-slate-900">
      <div className="mx-auto max-w-6xl px-6 py-20">
        <header className="rounded-xl border border-gray-200 bg-white/90 px-5 py-4 shadow-sm backdrop-blur">
          <div className="flex items-center justify-between">
            <div className="inline-flex items-center gap-3">
              <span className="rounded-full bg-emerald-600 p-2 shadow-[0_0_25px_rgba(16,185,129,0.25)]">
                <Leaf className="h-4 w-4 text-white" />
              </span>
              <span className="text-sm font-semibold tracking-wide text-slate-900">AVARTAN</span>
            </div>
            <Link
              to={primaryCtaPath}
              className="rounded-lg border border-gray-200 px-4 py-2 text-sm text-gray-700 transition-all duration-200 hover:scale-105 hover:bg-gray-50 active:scale-95 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            >
              Login
            </Link>
          </div>
        </header>

        <main className="relative mt-16 space-y-16">
          <div className="pointer-events-none absolute left-1/2 top-0 h-80 w-80 -translate-x-1/2 rounded-full bg-emerald-500/20 blur-[110px]" />

          <section
            className={`relative text-center transition-all duration-700 ${
              isVisible ? "translate-y-0 opacity-100" : "translate-y-6 opacity-0"
            }`}
          >
            <p className="mb-5 inline-flex items-center rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-medium uppercase tracking-wide text-emerald-700">
              AI Waste Intelligence Platform
            </p>
            <h1 className="bg-gradient-to-b from-slate-900 to-gray-500 bg-clip-text text-5xl font-semibold tracking-tight text-transparent md:text-6xl">
              AI-Powered Waste Management
            </h1>
            <p className="mx-auto mt-5 max-w-2xl text-base text-gray-500">
              A premium sustainability suite for AI scanning, route intelligence, and
              measurable eco impact.
            </p>
            <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <Link
                to={primaryCtaPath}
                className="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-5 py-2.5 text-sm font-medium text-white transition-all duration-200 hover:scale-105 hover:bg-emerald-700 active:scale-95 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
                Start Recycling
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                to={primaryCtaPath}
                className="rounded-lg border border-gray-200 bg-white px-5 py-2.5 text-sm font-medium text-gray-700 transition-all duration-200 hover:scale-105 hover:bg-gray-50 active:scale-95 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
                Login
              </Link>
            </div>
          </section>

          <section
            className={`grid gap-6 md:grid-cols-3 transition-all duration-700 ${
              isVisible ? "translate-y-0 opacity-100" : "translate-y-6 opacity-0"
            }`}
          >
            <Link to={primaryCtaPath} className={featureCardClass}>
              <Brain className="h-5 w-5 text-emerald-500" />
              <h3 className="mt-3 text-base font-semibold text-slate-900">AI Scanner</h3>
              <p className="mt-2 text-sm text-gray-500">
                Instantly classify waste and estimate environmental impact with AI.
              </p>
            </Link>
            <Link to={primaryCtaPath} className={featureCardClass}>
              <Route className="h-5 w-5 text-emerald-500" />
              <h3 className="mt-3 text-base font-semibold text-slate-900">Smart Routing</h3>
              <p className="mt-2 text-sm text-gray-500">
                Discover optimized nearby facilities and reduce turnaround time.
              </p>
            </Link>
            <Link to={primaryCtaPath} className={featureCardClass}>
              <Leaf className="h-5 w-5 text-emerald-500" />
              <h3 className="mt-3 text-base font-semibold text-slate-900">Impact Tracking</h3>
              <p className="mt-2 text-sm text-gray-500">
                Visualize your CO2 savings and track long-term sustainability impact.
              </p>
            </Link>
          </section>

          <section className="grid items-center gap-6 rounded-xl border border-gray-200 bg-white p-6 shadow-sm md:grid-cols-2">
            <div>
              <p className="text-xs uppercase tracking-wide text-emerald-700">About</p>
              <h2 className="mt-2 text-3xl font-semibold tracking-tight text-slate-900">
                Built for cleaner cities and smarter recycling
              </h2>
              <p className="mt-4 text-sm leading-6 text-gray-600">
                AVARTAN helps users, communities, and organizations make responsible
                waste decisions with AI guidance and actionable logistics.
              </p>
            </div>
            <img
              src="https://images.unsplash.com/photo-1497436072909-60f360e1d4b1?auto=format&fit=crop&w=1200&q=80"
              alt="Sustainable city"
              className="h-64 w-full rounded-xl border border-gray-200 object-cover shadow-sm"
            />
          </section>

          <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <div className="mb-4 inline-flex items-center gap-2 text-emerald-700">
              <Sparkles className="h-4 w-4" />
              <span className="text-xs uppercase tracking-wide">Platform Visual</span>
            </div>
            <div className="grid gap-6 md:grid-cols-3">
              <div className="rounded-xl border border-gray-200 bg-gradient-to-br from-emerald-100 to-white p-5">
                <p className="text-sm text-gray-700">Real-time AI classification</p>
              </div>
              <div className="rounded-xl border border-gray-200 bg-gradient-to-br from-gray-100 to-white p-5">
                <p className="text-sm text-gray-700">Optimized route visualization</p>
              </div>
              <div className="rounded-xl border border-gray-200 bg-gradient-to-br from-emerald-50 to-white p-5">
                <p className="text-sm text-gray-700">Impact analytics dashboard</p>
              </div>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
};

export default Landing;

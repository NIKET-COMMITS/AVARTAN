import React, { useEffect, useMemo, useState } from "react";
import { Leaf, Loader2, LogOut, Recycle, Trophy, Wind } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api/axios";
import AddWaste from "../components/AddWaste";

const DEFAULT_ERROR = "Unable to load data right now.";

const toNumber = (value) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
};

const buttonBaseClass =
  "inline-flex items-center justify-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-medium text-white transition-all duration-200 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 disabled:cursor-not-allowed disabled:opacity-60";

const cardBaseClass =
  "rounded-xl border border-gray-200 bg-white shadow-sm transition-all duration-200 hover:bg-gray-50 hover:scale-105 transition-transform";

const Dashboard = () => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState({
    greeting: "Welcome Eco Hero",
    name: "",
    points: 0,
    ecoTitle: "Eco Hero",
  });
  const [profileLoading, setProfileLoading] = useState(true);
  const [profileError, setProfileError] = useState("");

  const [stats, setStats] = useState({
    co2Saved: 0,
    itemsRecycled: 0,
    communityPoints: 0,
  });
  const [statsLoading, setStatsLoading] = useState(true);
  const [statsError, setStatsError] = useState("");

  const [leaderboard, setLeaderboard] = useState([]);
  const [leaderboardLoading, setLeaderboardLoading] = useState(true);
  const [leaderboardError, setLeaderboardError] = useState("");

  useEffect(() => {
    fetchProfile();
    fetchStats();
    fetchLeaderboard();
  }, []);

  const getAuthHeaders = () => {
    const token = localStorage.getItem("token");
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  const fetchProfile = async () => {
    setProfileLoading(true);
    setProfileError("");
    try {
      const response = await api.get("/profile/me", {
        headers: getAuthHeaders(),
      });
      const data = response?.data?.data ?? response?.data ?? {};
      const statsData = data?.stats ?? {};
      const points = toNumber(
        statsData.points ??
          data.points ??
          data.total_points ??
          data.community_points ??
          0,
      );
      const name =
        data.full_name || data.name || data.user_name || data.username || "";
      const ecoTitle = statsData.rank || data.eco_title || data.badge || "Eco Hero";
      const greeting = name ? `Welcome, ${name}` : "Welcome Eco Hero";

      setProfile({ greeting, name, points, ecoTitle });
    } catch {
      setProfile({
        greeting: "Welcome Eco Hero",
        name: "",
        points: 0,
        ecoTitle: "Eco Hero",
      });
      setProfileError(DEFAULT_ERROR);
    } finally {
      setProfileLoading(false);
    }
  };

  const fetchStats = async () => {
    setStatsLoading(true);
    setStatsError("");
    try {
      const response = await api.get("/dashboard/metrics");
      const data = response?.data?.data ?? response?.data ?? {};

      setStats({
        co2Saved: toNumber(data.co2_saved_kg ?? data.co2_saved ?? data.co2 ?? 0),
        itemsRecycled: toNumber(
          data.total_items_recycled ?? data.items_recycled ?? data.items ?? 0,
        ),
        communityPoints: toNumber(data.total_points ?? data.community_points ?? data.points ?? 0),
      });

      if (!profile.name) {
        const dashboardName = data.full_name || data.name || data.username || data.user_name || "";
        if (dashboardName) {
          setProfile((prev) => ({
            ...prev,
            name: dashboardName,
            greeting: `Welcome, ${dashboardName}`,
          }));
        }
      }
    } catch {
      setStats({ co2Saved: 0, itemsRecycled: 0, communityPoints: 0 });
      setStatsError(DEFAULT_ERROR);
    } finally {
      setStatsLoading(false);
    }
  };

  const fetchLeaderboard = async () => {
    setLeaderboardLoading(true);
    setLeaderboardError("");
    try {
      const response = await api.get("/leaderboards/global");
      const data = response?.data?.data ?? response?.data ?? [];
      setLeaderboard(Array.isArray(data) ? data : []);
    } catch {
      setLeaderboard([]);
      setLeaderboardError(DEFAULT_ERROR);
    } finally {
      setLeaderboardLoading(false);
    }
  };

  const topPoints = useMemo(() => {
    if (profile.points > 0) return profile.points;
    return stats.communityPoints;
  }, [profile.points, stats.communityPoints]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user_id");
    navigate("/");
  };

  return (
    <div className="min-h-screen bg-gray-50 text-slate-900">
      <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <Header
          profile={profile}
          points={topPoints}
          loading={profileLoading}
          error={profileError}
          onLogout={handleLogout}
        />

        <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-[2fr_1fr]">
          <div className="space-y-6">
            {statsError && <ErrorBanner message={statsError} />}
            <section className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <StatCard
                title="CO2 Saved"
                value={`${toNumber(stats.co2Saved).toFixed(2)} kg`}
                icon={<Wind className="h-5 w-5 text-emerald-600" />}
                loading={statsLoading}
              />
              <StatCard
                title="Items Recycled"
                value={toNumber(stats.itemsRecycled)}
                icon={<Recycle className="h-5 w-5 text-emerald-600" />}
                loading={statsLoading}
              />
              <StatCard
                title="Community Points"
                value={toNumber(stats.communityPoints)}
                icon={<Leaf className="h-5 w-5 text-emerald-600" />}
                loading={statsLoading}
              />
            </section>

            <AddWaste
              onSubmitted={() => {
                fetchStats();
                fetchProfile();
              }}
            />
          </div>

          <Leaderboard
            users={leaderboard}
            loading={leaderboardLoading}
            error={leaderboardError}
          />
        </div>
      </div>
    </div>
  );
};

const Header = ({ profile, points, loading, error, onLogout }) => (
  <header className={`${cardBaseClass} p-5 sm:p-6`}>
    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex items-center gap-3">
        <div className="rounded-xl bg-emerald-600 p-2.5 text-white">
          <Leaf className="h-5 w-5" />
        </div>
        <div>
          <p className="text-lg font-semibold tracking-tight">AVARTAN</p>
          <p className="text-sm text-gray-600">
            {loading ? "Loading profile..." : profile.greeting}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <span className="rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700">
          {profile.ecoTitle}
        </span>
        <span className="rounded-full border border-gray-200 bg-white px-3 py-1 text-sm font-semibold text-slate-900">
          {toNumber(points)} pts
        </span>
        <Link
          to="/profile"
          className="inline-flex items-center gap-1.5 rounded-lg border border-gray-200 bg-white px-3 py-1.5 text-sm text-gray-600 transition-all duration-200 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-emerald-500"
        >
          My Profile
        </Link>
        <button
          onClick={onLogout}
          className="inline-flex items-center gap-1.5 rounded-lg border border-gray-200 bg-white px-3 py-1.5 text-sm text-gray-600 transition-all duration-200 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-emerald-500"
        >
          <LogOut className="h-4 w-4" />
          Logout
        </button>
      </div>
    </div>
    {error && <p className="mt-3 text-sm text-gray-600">{error}</p>}
  </header>
);

const StatCard = ({ title, value, icon, loading }) => (
  <article className={`${cardBaseClass} p-4`}>
    <div className="flex items-center justify-between">
      <p className="text-sm text-gray-600">{title}</p>
      <div className="rounded-lg border border-gray-200 bg-gray-50 p-2">{icon}</div>
    </div>
    <div className="mt-3 text-2xl font-semibold text-slate-900">
      {loading ? (
        <span className="inline-flex items-center text-sm text-gray-400">
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          Loading...
        </span>
      ) : (
        value
      )}
    </div>
  </article>
);


const Leaderboard = ({ users, loading, error }) => (
  <aside className={`${cardBaseClass} h-fit p-5`}>
    <div className="mb-4 flex items-center gap-2">
      <Trophy className="h-5 w-5 text-emerald-600" />
      <h2 className="text-base font-semibold">Leaderboard</h2>
    </div>

    {error && <p className="mb-3 text-sm text-gray-600">{error}</p>}

    {loading ? (
      <div className="inline-flex items-center text-sm text-gray-600">
        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
        Loading leaderboard...
      </div>
    ) : users.length === 0 ? (
      <p className="text-sm text-gray-400">No eco-warriors yet. Be the first!</p>
    ) : (
      <div className="divide-y divide-gray-200 rounded-lg border border-gray-200">
        {users.map((user, index) => {
          const rank = index + 1;
          const name =
            user.full_name || user.name || user.username || user.user_name || "Anonymous";
          const points = toNumber(user.total_points ?? user.points ?? 0);
          const isCurrentUser = Boolean(user.is_current_user);

          return (
            <div
              key={`${name}-${rank}`}
              className={`flex items-center justify-between px-3 py-2.5 ${
                isCurrentUser ? "bg-emerald-50" : ""
              }`}
            >
              <div className="flex items-center gap-2">
                <span className="w-6 text-sm font-medium text-gray-600">
                  {rank === 1 ? (
                    <Trophy className="h-4 w-4 text-emerald-600" />
                  ) : (
                    rank
                  )}
                </span>
                <span className="text-sm text-slate-900">{name}</span>
              </div>
              <span className="text-sm font-semibold text-slate-900">{points}</span>
            </div>
          );
        })}
      </div>
    )}
  </aside>
);

const ErrorBanner = ({ message }) => (
  <div className="rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm text-gray-600 shadow-sm">
    {message}
  </div>
);

export default Dashboard;

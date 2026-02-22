import { useState, useEffect } from "react";
import {
  Users,
  BarChart3,
  Shield,
  TrendingUp,
  UserCheck,
  UserX,
  Clock,
  Loader2,
} from "lucide-react";
import { getAdminStats, getAdminUsers, getAdminPredictions, toggleUserActive } from "../services/api";

function StatCard({ icon: Icon, label, value, color, bg }) {
  return (
    <div className="glass rounded-xl p-5 animate-slide-up">
      <div className={`w-10 h-10 rounded-lg ${bg} flex items-center justify-center mb-3`}>
        <Icon className={`w-5 h-5 ${color}`} />
      </div>
      <p className="text-xs text-slate-500 font-medium uppercase tracking-wider">{label}</p>
      <p className="text-2xl font-bold text-white mt-1">{value}</p>
    </div>
  );
}

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [activeTab, setActiveTab] = useState("overview");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    setLoading(true);
    try {
      const [s, u, p] = await Promise.all([
        getAdminStats(),
        getAdminUsers(),
        getAdminPredictions(),
      ]);
      setStats(s);
      setUsers(u.users);
      setPredictions(p.predictions);
    } catch (err) {
      console.error("Admin load error:", err);
    } finally {
      setLoading(false);
    }
  }

  async function handleToggleUser(userId) {
    try {
      const result = await toggleUserActive(userId);
      setUsers((prev) =>
        prev.map((u) => (u.id === userId ? { ...u, is_active: result.is_active } : u))
      );
    } catch (err) {
      console.error("Toggle user error:", err);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
      </div>
    );
  }

  const tabs = [
    { id: "overview", label: "Overview", icon: BarChart3 },
    { id: "users", label: "Users", icon: Users },
    { id: "predictions", label: "Predictions", icon: TrendingUp },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white">Admin Dashboard</h2>
        <p className="text-slate-400 text-sm mt-1">
          Manage users and monitor platform activity
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 p-1 rounded-lg bg-slate-800/50 w-fit">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all cursor-pointer ${
              activeTab === id
                ? "bg-blue-500/20 text-blue-400"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <Icon className="w-4 h-4" />
            {label}
          </button>
        ))}
      </div>

      {/* Overview */}
      {activeTab === "overview" && stats && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard
              icon={Users}
              label="Total Users"
              value={stats.total_users}
              color="text-blue-400"
              bg="bg-blue-500/10"
            />
            <StatCard
              icon={Shield}
              label="Admins"
              value={stats.total_admins}
              color="text-violet-400"
              bg="bg-violet-500/10"
            />
            <StatCard
              icon={TrendingUp}
              label="Total Predictions"
              value={stats.total_predictions}
              color="text-emerald-400"
              bg="bg-emerald-500/10"
            />
            <StatCard
              icon={BarChart3}
              label="Bundle Types"
              value={stats.bundle_distribution?.length || 0}
              color="text-amber-400"
              bg="bg-amber-500/10"
            />
          </div>

          {/* Bundle distribution */}
          {stats.bundle_distribution?.length > 0 && (
            <div className="glass rounded-xl p-6">
              <h3 className="text-lg font-bold text-white mb-4">
                Most Recommended Bundles
              </h3>
              <div className="space-y-3">
                {stats.bundle_distribution.map((item) => {
                  const maxCount = stats.bundle_distribution[0]?.count || 1;
                  const pct = (item.count / maxCount) * 100;
                  return (
                    <div key={item.predicted_bundle_name} className="flex items-center gap-3">
                      <span className="text-xs text-slate-400 w-40 truncate">
                        {item.predicted_bundle_name?.replace(/_/g, " ")}
                      </span>
                      <div className="flex-1 h-2.5 bg-slate-800 rounded-full overflow-hidden">
                        <div
                          className="h-full rounded-full bg-gradient-to-r from-blue-500 to-violet-500"
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                      <span className="text-xs text-slate-400 w-10 text-right font-mono">
                        {item.count}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Users */}
      {activeTab === "users" && (
        <div className="glass rounded-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700/50">
                  <th className="text-left px-5 py-3 text-xs font-medium text-slate-500 uppercase">
                    User
                  </th>
                  <th className="text-left px-5 py-3 text-xs font-medium text-slate-500 uppercase">
                    Role
                  </th>
                  <th className="text-left px-5 py-3 text-xs font-medium text-slate-500 uppercase">
                    Predictions
                  </th>
                  <th className="text-left px-5 py-3 text-xs font-medium text-slate-500 uppercase">
                    Joined
                  </th>
                  <th className="text-left px-5 py-3 text-xs font-medium text-slate-500 uppercase">
                    Status
                  </th>
                  <th className="text-right px-5 py-3 text-xs font-medium text-slate-500 uppercase">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id} className="border-b border-slate-800/50 hover:bg-slate-800/30">
                    <td className="px-5 py-3">
                      <div>
                        <p className="text-white font-medium">{u.full_name}</p>
                        <p className="text-slate-500 text-xs">{u.email}</p>
                      </div>
                    </td>
                    <td className="px-5 py-3">
                      <span
                        className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                          u.role === "admin"
                            ? "bg-violet-500/20 text-violet-400"
                            : "bg-slate-500/20 text-slate-400"
                        }`}
                      >
                        {u.role}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-slate-300">{u.prediction_count}</td>
                    <td className="px-5 py-3 text-slate-400 text-xs">
                      {u.created_at ? new Date(u.created_at).toLocaleDateString() : "—"}
                    </td>
                    <td className="px-5 py-3">
                      {u.is_active ? (
                        <span className="flex items-center gap-1 text-emerald-400 text-xs">
                          <UserCheck className="w-3 h-3" /> Active
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 text-red-400 text-xs">
                          <UserX className="w-3 h-3" /> Disabled
                        </span>
                      )}
                    </td>
                    <td className="px-5 py-3 text-right">
                      <button
                        onClick={() => handleToggleUser(u.id)}
                        className={`px-3 py-1 rounded-md text-xs font-medium cursor-pointer transition-colors ${
                          u.is_active
                            ? "bg-red-500/10 text-red-400 hover:bg-red-500/20"
                            : "bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20"
                        }`}
                      >
                        {u.is_active ? "Disable" : "Enable"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Predictions */}
      {activeTab === "predictions" && (
        <div className="glass rounded-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700/50">
                  <th className="text-left px-5 py-3 text-xs font-medium text-slate-500 uppercase">
                    User
                  </th>
                  <th className="text-left px-5 py-3 text-xs font-medium text-slate-500 uppercase">
                    Recommended Bundle
                  </th>
                  <th className="text-left px-5 py-3 text-xs font-medium text-slate-500 uppercase">
                    Date
                  </th>
                </tr>
              </thead>
              <tbody>
                {predictions.map((p) => (
                  <tr key={p.id} className="border-b border-slate-800/50 hover:bg-slate-800/30">
                    <td className="px-5 py-3">
                      <div>
                        <p className="text-white font-medium">{p.full_name}</p>
                        <p className="text-slate-500 text-xs">{p.email}</p>
                      </div>
                    </td>
                    <td className="px-5 py-3">
                      <span className="px-2 py-1 rounded-lg bg-blue-500/10 text-blue-400 text-xs font-medium">
                        {p.predicted_bundle_name?.replace(/_/g, " ")}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-slate-400 text-xs flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {p.created_at ? new Date(p.created_at).toLocaleString() : "—"}
                    </td>
                  </tr>
                ))}
                {predictions.length === 0 && (
                  <tr>
                    <td colSpan={3} className="px-5 py-8 text-center text-slate-500">
                      No predictions yet
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

import { useState, useEffect } from "react";
import {
  Sparkles,
  Shield,
  ArrowRight,
  Heart,
  Users,
  CheckCircle2,
  Star,
} from "lucide-react";
import { getBundles } from "../services/api";
import { getBundleIcon, getCategoryGradient } from "../utils/helpers";

export default function Dashboard({ onNavigate, user }) {
  const [bundles, setBundles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const bundleData = await getBundles();
        setBundles(bundleData.bundles);
      } catch (err) {
        console.error("Failed to load dashboard data:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-full border-2 border-blue-500 border-t-transparent animate-spin" />
          <p className="text-slate-400 text-sm">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-blue-600/20 via-violet-600/20 to-cyan-600/20 border border-slate-700/50 p-8 md:p-12">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48cGF0dGVybiBpZD0iZ3JpZCIgd2lkdGg9IjQwIiBoZWlnaHQ9IjQwIiBwYXR0ZXJuVW5pdHM9InVzZXJTcGFjZU9uVXNlIj48cGF0aCBkPSJNIDQwIDAgTCAwIDAgMCA0MCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJyZ2JhKDI1NSwyNTUsMjU1LDAuMDMpIiBzdHJva2Utd2lkdGg9IjEiLz48L3BhdHRlcm4+PC9kZWZzPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9InVybCgjZ3JpZCkiLz48L3N2Zz4=')] opacity-50" />
        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="space-y-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-medium">
              <Star className="w-3 h-3" />
              Smart Insurance Recommendations
            </div>
            <h2 className="text-3xl md:text-4xl font-bold text-white">
              {user ? `Welcome back, ${user.full_name.split(" ")[0]}` : "Find Your Perfect"}
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-violet-400">
                {user ? "Ready to explore?" : "Insurance Coverage"}
              </span>
            </h2>
            <p className="text-slate-400 max-w-lg leading-relaxed">
              Answer a few simple questions about yourself and we&apos;ll recommend
              the best insurance coverage bundle tailored to your needs. It&apos;s
              quick, easy, and personalized.
            </p>
            <button
              onClick={() => onNavigate("predict")}
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-blue-500 to-violet-500 text-white font-semibold hover:from-blue-600 hover:to-violet-600 transition-all shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40 cursor-pointer"
            >
              <Shield className="w-5 h-5" />
              Get My Recommendation
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
          <div className="hidden md:flex flex-col items-center gap-4">
            <div className="relative">
              <div className="w-32 h-32 rounded-2xl bg-gradient-to-br from-blue-500/20 to-violet-500/20 border border-slate-600/50 flex items-center justify-center">
                <Sparkles className="w-16 h-16 text-blue-400 pulse-ring" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Why Choose Us */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          {
            icon: Shield,
            title: "Personalized Coverage",
            desc: "Get a recommendation that matches your unique profile and needs.",
            color: "text-blue-400",
            bg: "bg-blue-500/10",
          },
          {
            icon: Heart,
            title: "Comprehensive Options",
            desc: "10 carefully designed bundles covering auto, health, home, and family.",
            color: "text-emerald-400",
            bg: "bg-emerald-500/10",
          },
          {
            icon: Users,
            title: "Trusted by Many",
            desc: "Join thousands of customers who found their ideal insurance plan.",
            color: "text-violet-400",
            bg: "bg-violet-500/10",
          },
        ].map(({ icon: Icon, title, desc, color, bg }, i) => (
          <div
            key={title}
            className="glass rounded-xl p-6 hover:border-slate-600/50 transition-all animate-slide-up"
            style={{ animationDelay: `${i * 0.1}s` }}
          >
            <div className={`w-11 h-11 rounded-lg ${bg} flex items-center justify-center mb-4`}>
              <Icon className={`w-5 h-5 ${color}`} />
            </div>
            <h4 className="text-white font-semibold">{title}</h4>
            <p className="text-slate-400 text-sm mt-2 leading-relaxed">{desc}</p>
          </div>
        ))}
      </div>

      {/* Bundles Grid */}
      <div>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-xl font-bold text-white">Available Coverage Bundles</h3>
            <p className="text-slate-400 text-sm mt-1">
              Explore our range of insurance plans designed for every need
            </p>
          </div>
          <button
            onClick={() => onNavigate("bundles")}
            className="text-sm text-blue-400 hover:text-blue-300 font-medium flex items-center gap-1 cursor-pointer"
          >
            View all <ArrowRight className="w-4 h-4" />
          </button>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
          {bundles.map((bundle, i) => (
            <div
              key={bundle.id}
              className="glass rounded-xl p-4 hover:border-slate-600/50 transition-all group cursor-default animate-slide-up"
              style={{ animationDelay: `${i * 0.05}s` }}
            >
              <div
                className={`w-10 h-10 rounded-lg bg-gradient-to-br ${getCategoryGradient(bundle.category)} flex items-center justify-center mb-3 group-hover:scale-110 transition-transform`}
              >
                {getBundleIcon(bundle.icon, {
                  className: "w-5 h-5 text-white",
                })}
              </div>
              <p className="text-xs text-slate-500 font-medium">{bundle.category}</p>
              <p className="text-sm font-semibold text-white mt-0.5 leading-tight">
                {bundle.name.replace(/_/g, " ")}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* CTA */}
      <div className="glass rounded-2xl p-8 text-center border border-slate-700/50">
        <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto mb-4" />
        <h3 className="text-xl font-bold text-white">
          Ready to find your ideal coverage?
        </h3>
        <p className="text-slate-400 text-sm mt-2 max-w-md mx-auto">
          It only takes a minute. Fill in your details and let us match you with
          the best insurance bundle.
        </p>
        <button
          onClick={() => onNavigate("predict")}
          className="mt-5 inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-semibold hover:from-emerald-600 hover:to-teal-600 transition-all shadow-lg shadow-emerald-500/25 cursor-pointer"
        >
          Get Started
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

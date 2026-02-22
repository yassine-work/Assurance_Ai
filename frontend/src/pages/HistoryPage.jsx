import { useState, useEffect } from "react";
import { Clock, Shield, Loader2 } from "lucide-react";
import { getPredictionHistory } from "../services/api";
import { getBundleIcon, getCategoryGradient } from "../utils/helpers";

export default function HistoryPage() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await getPredictionHistory();
        setHistory(data.history);
      } catch (err) {
        console.error("Failed to load history:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white">My Predictions</h2>
        <p className="text-slate-400 text-sm mt-1">
          Your recent insurance coverage recommendations
        </p>
      </div>

      {history.length === 0 ? (
        <div className="glass rounded-xl p-12 flex flex-col items-center text-center">
          <Shield className="w-12 h-12 text-slate-600 mb-4" />
          <h3 className="text-white font-semibold text-lg">No predictions yet</h3>
          <p className="text-slate-500 text-sm mt-2 max-w-md">
            Once you get an insurance recommendation, it will appear here so you can review
            your results anytime.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {history.map((item, i) => {
            const topScore = item.confidence_scores
              ? Math.max(...Object.values(item.confidence_scores))
              : null;
            return (
              <div
                key={item.id}
                className="glass rounded-xl p-5 flex items-center gap-4 animate-slide-up hover:border-slate-600/50 transition-all"
                style={{ animationDelay: `${i * 0.05}s` }}
              >
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center flex-shrink-0">
                  <Shield className="w-6 h-6 text-white" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-white font-semibold">
                    {item.predicted_bundle_name?.replace(/_/g, " ")}
                  </p>
                  <div className="flex items-center gap-3 mt-1">
                    {topScore != null && (
                      <span className="text-xs text-emerald-400 font-medium">
                        {topScore.toFixed(1)}% match
                      </span>
                    )}
                    <span className="text-xs text-slate-500 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {item.created_at
                        ? new Date(item.created_at).toLocaleString()
                        : "—"}
                    </span>
                  </div>
                </div>
                <span className="px-3 py-1 rounded-lg bg-blue-500/10 text-blue-400 text-xs font-medium flex-shrink-0">
                  Bundle {item.predicted_bundle_id}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

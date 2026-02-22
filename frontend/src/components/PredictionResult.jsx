import {
  getBundleIcon,
  getCategoryGradient,
  formatPercent,
  BUNDLE_COLORS,
} from "../utils/helpers";
import { Trophy, BarChart3, TrendingUp, Star } from "lucide-react";

function ConfidenceBar({ label, value, color, isTop }) {
  return (
    <div className="flex items-center gap-3">
      <span
        className={`text-xs w-32 truncate ${isTop ? "text-white font-semibold" : "text-slate-400"}`}
      >
        {label}
      </span>
      <div className="flex-1 h-2.5 bg-slate-800 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700 ease-out"
          style={{ width: `${Math.min(value, 100)}%`, backgroundColor: color }}
        />
      </div>
      <span
        className={`text-xs w-14 text-right font-mono ${isTop ? "text-white font-bold" : "text-slate-500"}`}
      >
        {formatPercent(value)}
      </span>
    </div>
  );
}

export default function PredictionResult({ result }) {
  if (!result) return null;

  const {
    predicted_bundle_id,
    predicted_bundle_name,
    confidence_scores,
    bundle_meta,
  } = result;

  // Sort confidence scores descending
  const sortedScores = Object.entries(confidence_scores).sort(
    ([, a], [, b]) => b - a
  );

  const topScore = sortedScores[0]?.[1] || 0;

  return (
    <div className="space-y-4 animate-slide-up">
      {/* Main prediction card */}
      <div className="relative overflow-hidden rounded-xl border border-slate-700/50">
        {/* Gradient header */}
        <div
          className={`bg-gradient-to-r ${getCategoryGradient(bundle_meta?.category)} p-6`}
        >
          <div className="flex items-center gap-2 mb-3">
            <Trophy className="w-4 h-4 text-yellow-300" />
            <span className="text-xs font-bold text-white/80 uppercase tracking-wider">
              Recommended Coverage
            </span>
          </div>
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-xl bg-white/20 backdrop-blur-sm flex items-center justify-center">
              {getBundleIcon(bundle_meta?.icon, {
                className: "w-7 h-7 text-white",
              })}
            </div>
            <div>
              <h3 className="text-2xl font-bold text-white">
                {predicted_bundle_name?.replace(/_/g, " ")}
              </h3>
              <div className="flex items-center gap-3 mt-1">
                <span className="text-sm text-white/70">
                  {bundle_meta?.category} Coverage
                </span>
                <span className="px-2 py-0.5 rounded-full bg-white/20 text-xs text-white font-medium">
                  ID: {predicted_bundle_id}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Confidence */}
        <div className="p-5 bg-slate-900/50 backdrop-blur">
          <div className="flex items-center gap-2 mb-1">
            <Star className="w-4 h-4 text-amber-400" />
            <span className="text-sm font-semibold text-white">
              Confidence Score
            </span>
          </div>
          <div className="flex items-end gap-2">
            <span className="text-4xl font-bold text-white">
              {formatPercent(topScore)}
            </span>
            <span className="text-xs text-slate-500 mb-1.5">match strength</span>
          </div>
        </div>
      </div>

      {/* All scores breakdown */}
      <div className="glass rounded-xl p-5">
        <div className="flex items-center gap-2 mb-4">
          <BarChart3 className="w-4 h-4 text-blue-400" />
          <span className="text-sm font-semibold text-white">
            Confidence Breakdown
          </span>
        </div>
        <div className="space-y-2.5">
          {sortedScores.map(([label, score], i) => (
            <ConfidenceBar
              key={label}
              label={label.replace(/_/g, " ")}
              value={score}
              color={BUNDLE_COLORS[i] || "#64748b"}
              isTop={i === 0}
            />
          ))}
        </div>
      </div>

      {/* Quick insights */}
      <div className="glass rounded-xl p-5">
        <div className="flex items-center gap-2 mb-3">
          <TrendingUp className="w-4 h-4 text-emerald-400" />
          <span className="text-sm font-semibold text-white">
            Quick Insights
          </span>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-slate-800/50 rounded-lg p-3">
            <p className="text-[10px] text-slate-500 uppercase font-medium">
              Category
            </p>
            <p className="text-sm font-semibold text-white mt-0.5">
              {bundle_meta?.category || "N/A"}
            </p>
          </div>
          <div className="bg-slate-800/50 rounded-lg p-3">
            <p className="text-[10px] text-slate-500 uppercase font-medium">
              Margin
            </p>
            <p className="text-sm font-semibold text-white mt-0.5">
              {sortedScores.length >= 2
                ? `+${formatPercent(sortedScores[0][1] - sortedScores[1][1])}`
                : "N/A"}
            </p>
          </div>
          <div className="bg-slate-800/50 rounded-lg p-3">
            <p className="text-[10px] text-slate-500 uppercase font-medium">
              Runner-up
            </p>
            <p className="text-sm font-semibold text-white mt-0.5 truncate">
              {sortedScores[1]?.[0]?.replace(/_/g, " ") || "N/A"}
            </p>
          </div>
          <div className="bg-slate-800/50 rounded-lg p-3">
            <p className="text-[10px] text-slate-500 uppercase font-medium">
              Best Match
            </p>
            <p className="text-sm font-semibold text-emerald-400 mt-0.5">
              {sortedScores[0]?.[0]?.replace(/_/g, " ") || "N/A"}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

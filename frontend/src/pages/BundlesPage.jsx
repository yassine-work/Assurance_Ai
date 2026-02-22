import { useState, useEffect } from "react";
import { getBundles } from "../services/api";
import { getBundleIcon, getCategoryGradient } from "../utils/helpers";
import { Info, CheckCircle2, Star, ArrowRight } from "lucide-react";

/** User-friendly descriptions for each bundle category */
const CATEGORY_DETAILS = {
  Auto: {
    bestFor: "Vehicle owners seeking comprehensive car coverage",
    includes: ["Collision protection", "Liability coverage", "Roadside assistance"],
  },
  Health: {
    bestFor: "Individuals and families prioritizing medical care",
    includes: ["Doctor visits", "Prescription coverage", "Emergency care"],
  },
  Family: {
    bestFor: "Families looking for multi-member protection",
    includes: ["Life insurance", "Dependent coverage", "Income protection"],
  },
  Home: {
    bestFor: "Homeowners wanting full property protection",
    includes: ["Property damage", "Theft protection", "Natural disaster coverage"],
  },
  Renter: {
    bestFor: "Renters needing affordable personal coverage",
    includes: ["Personal belongings", "Liability protection", "Temporary housing"],
  },
};

export default function BundlesPage() {
  const [bundles, setBundles] = useState([]);
  const [selectedBundle, setSelectedBundle] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const bundleData = await getBundles();
        setBundles(bundleData.bundles);
      } catch (err) {
        console.error("Failed to load bundles:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-12 h-12 rounded-full border-2 border-blue-500 border-t-transparent animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white">Insurance Coverage Bundles</h2>
        <p className="text-slate-400 mt-1">
          Explore our range of insurance plans — click any bundle to learn more.
        </p>
      </div>

      {/* Bundle grid */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
        {bundles.map((bundle, i) => {
          const isSelected = selectedBundle?.id === bundle.id;
          return (
            <button
              key={bundle.id}
              onClick={() => setSelectedBundle(isSelected ? null : bundle)}
              className={`
                glass rounded-xl p-5 text-left transition-all cursor-pointer animate-slide-up
                ${isSelected ? "ring-2 ring-blue-500 border-blue-500/50" : "hover:border-slate-600/50"}
              `}
              style={{ animationDelay: `${i * 0.04}s` }}
            >
              <div
                className={`w-12 h-12 rounded-xl bg-gradient-to-br ${getCategoryGradient(bundle.category)} flex items-center justify-center mb-4 transition-transform ${isSelected ? "scale-110" : ""}`}
              >
                {getBundleIcon(bundle.icon, {
                  className: "w-6 h-6 text-white",
                })}
              </div>

              <p className="text-xs text-slate-500 font-medium uppercase tracking-wider">
                {bundle.category}
              </p>
              <p className="text-base font-bold text-white mt-1">
                {bundle.name.replace(/_/g, " ")}
              </p>

              <div className="flex items-center gap-2 mt-3">
                <span
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: bundle.color }}
                />
                <span className="text-xs text-slate-500">
                  {bundle.category} Insurance
                </span>
              </div>
            </button>
          );
        })}
      </div>

      {/* Selected bundle detail */}
      {selectedBundle && (
        <div className="glass rounded-2xl p-6 animate-slide-up border border-blue-500/20">
          <div className="flex items-start gap-5">
            <div
              className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${getCategoryGradient(selectedBundle.category)} flex items-center justify-center flex-shrink-0`}
            >
              {getBundleIcon(selectedBundle.icon, {
                className: "w-8 h-8 text-white",
              })}
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-bold text-white">
                {selectedBundle.name.replace(/_/g, " ")}
              </h3>
              <p className="text-slate-400 text-sm mt-1">
                {selectedBundle.category} Insurance Coverage
              </p>

              <div className="grid sm:grid-cols-2 gap-4 mt-5">
                {/* Best For */}
                <div className="bg-slate-800/50 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Star className="w-4 h-4 text-amber-400" />
                    <span className="text-xs text-slate-400 font-medium uppercase">
                      Best For
                    </span>
                  </div>
                  <p className="text-sm text-white leading-relaxed">
                    {CATEGORY_DETAILS[selectedBundle.category]?.bestFor ||
                      "Customers looking for reliable insurance coverage"}
                  </p>
                </div>

                {/* What's Included */}
                <div className="bg-slate-800/50 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Info className="w-4 h-4 text-blue-400" />
                    <span className="text-xs text-slate-400 font-medium uppercase">
                      What&apos;s Included
                    </span>
                  </div>
                  <ul className="space-y-1.5">
                    {(
                      CATEGORY_DETAILS[selectedBundle.category]?.includes || [
                        "Comprehensive coverage",
                        "24/7 support",
                        "Custom options",
                      ]
                    ).map((item) => (
                      <li
                        key={item}
                        className="flex items-center gap-2 text-sm text-white"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Help section */}
      <div className="glass rounded-2xl p-6 text-center">
        <h3 className="text-lg font-bold text-white mb-2">
          Not sure which bundle is right for you?
        </h3>
        <p className="text-sm text-slate-400 max-w-lg mx-auto">
          Let us help! Answer a few questions about your situation and we&apos;ll
          recommend the ideal coverage bundle for your needs.
        </p>
        <div className="mt-4 flex justify-center">
          <a
            href="#"
            onClick={(e) => {
              e.preventDefault();
              window.scrollTo(0, 0);
            }}
            className="inline-flex items-center gap-2 text-sm text-blue-400 hover:text-blue-300 font-medium"
          >
            Get a recommendation <ArrowRight className="w-4 h-4" />
          </a>
        </div>
      </div>
    </div>
  );
}

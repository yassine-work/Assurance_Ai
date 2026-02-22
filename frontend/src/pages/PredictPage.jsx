import { useState, useEffect } from "react";
import {
  Brain,
  Loader2,
  ChevronDown,
  ChevronRight,
  RotateCcw,
  Sparkles,
  AlertCircle,
} from "lucide-react";
import { getFormSchema, predictBundle } from "../services/api";
import PredictionResult from "../components/PredictionResult";

/** Default form values matching the schema */
const DEFAULTS = {
  Adult_Dependents: 0,
  Child_Dependents: 0,
  Infant_Dependents: 0,
  Estimated_Annual_Income: 50000,
  Employment_Status: "Employed",
  Region_Code: 1,
  Existing_Policyholder: "No",
  Previous_Claims_Filed: 0,
  Years_Without_Claims: 0,
  Previous_Policy_Duration_Months: 0,
  Policy_Cancelled_Post_Purchase: "No",
  Deductible_Tier: 3,
  Payment_Schedule: "Monthly",
  Vehicles_on_Policy: 1,
  Custom_Riders_Requested: 0,
  Grace_Period_Extensions: 0,
  Days_Since_Quote: 7,
  Underwriting_Processing_Days: 5,
  Policy_Amendments_Count: 0,
  Acquisition_Channel: "Online",
  Broker_Agency_Type: "Large",
  Broker_ID: 9,
  Employer_ID: 174,
  Policy_Start_Year: 2024,
  Policy_Start_Month: "January",
  Policy_Start_Week: 1,
  Policy_Start_Day: 15,
};

/** Section icons */
const SECTION_ICONS = {
  demographics: "�",
  history: "📋",
  policy: "🛡️",
  sales: "🔍",
  timeline: "📅",
};

function FormField({ field, value, onChange }) {
  if (field.type === "select") {
    return (
      <div>
        <label className="block text-xs font-medium text-slate-400 mb-1.5">
          {field.label}
        </label>
        <select
          value={value}
          onChange={(e) => onChange(field.name, e.target.value)}
          className="w-full px-3 py-2.5 rounded-lg bg-slate-800/80 border border-slate-600/50 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all appearance-none cursor-pointer"
        >
          {field.options.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
      </div>
    );
  }

  return (
    <div>
      <label className="block text-xs font-medium text-slate-400 mb-1.5">
        {field.label}
      </label>
      <input
        type="number"
        value={value}
        onChange={(e) => {
          const v = e.target.value === "" ? "" : Number(e.target.value);
          onChange(field.name, v);
        }}
        min={field.min}
        max={field.max}
        className="w-full px-3 py-2.5 rounded-lg bg-slate-800/80 border border-slate-600/50 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
      />
    </div>
  );
}

export default function PredictPage() {
  const [schema, setSchema] = useState(null);
  const [formData, setFormData] = useState(DEFAULTS);
  const [expandedSections, setExpandedSections] = useState({
    demographics: true,
    history: true,
    policy: false,
    sales: false,
    timeline: false,
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [schemaLoading, setSchemaLoading] = useState(true);

  useEffect(() => {
    async function loadSchema() {
      try {
        const data = await getFormSchema();
        setSchema(data.sections);
      } catch (err) {
        console.error("Failed to load form schema:", err);
      } finally {
        setSchemaLoading(false);
      }
    }
    loadSchema();
  }, []);

  function handleFieldChange(name, value) {
    setFormData((prev) => ({ ...prev, [name]: value }));
  }

  function toggleSection(key) {
    setExpandedSections((prev) => ({ ...prev, [key]: !prev[key] }));
  }

  function handleReset() {
    setFormData(DEFAULTS);
    setResult(null);
    setError(null);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const prediction = await predictBundle(formData);
      setResult(prediction);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Prediction failed");
    } finally {
      setLoading(false);
    }
  }

  if (schemaLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-full border-2 border-blue-500 border-t-transparent animate-spin" />
          <p className="text-slate-400 text-sm">Loading form...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-white">Get Your Recommendation</h2>
        <p className="text-slate-400 mt-1">
          Fill in your details below and we&apos;ll find the best insurance
          coverage bundle for you.
        </p>
      </div>

      <div className="grid lg:grid-cols-5 gap-8">
        {/* Form - 3 cols */}
        <form onSubmit={handleSubmit} className="lg:col-span-3 space-y-4">
          {schema &&
            Object.entries(schema).map(([sectionKey, section]) => (
              <div
                key={sectionKey}
                className="glass rounded-xl overflow-hidden transition-all"
              >
                <button
                  type="button"
                  onClick={() => toggleSection(sectionKey)}
                  className="w-full flex items-center justify-between px-5 py-4 hover:bg-slate-800/30 transition-colors cursor-pointer"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-lg">{SECTION_ICONS[sectionKey] || "📋"}</span>
                    <span className="font-semibold text-white text-sm">
                      {section.label}
                    </span>
                    <span className="text-xs text-slate-500">
                      {section.fields.length} fields
                    </span>
                  </div>
                  {expandedSections[sectionKey] ? (
                    <ChevronDown className="w-4 h-4 text-slate-400" />
                  ) : (
                    <ChevronRight className="w-4 h-4 text-slate-400" />
                  )}
                </button>

                {expandedSections[sectionKey] && (
                  <div className="px-5 pb-5 grid grid-cols-1 sm:grid-cols-2 gap-4 animate-fade-in">
                    {section.fields.map((field) => (
                      <FormField
                        key={field.name}
                        field={field}
                        value={formData[field.name] ?? field.default ?? ""}
                        onChange={handleFieldChange}
                      />
                    ))}
                  </div>
                )}
              </div>
            ))}

          {/* Action buttons */}
          <div className="flex items-center gap-3 pt-2">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl bg-gradient-to-r from-blue-500 to-violet-500 text-white font-semibold hover:from-blue-600 hover:to-violet-600 transition-all shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Brain className="w-5 h-5" />
                  Find My Coverage
                  <Sparkles className="w-4 h-4" />
                </>
              )}
            </button>
            <button
              type="button"
              onClick={handleReset}
              className="px-4 py-3.5 rounded-xl border border-slate-600/50 text-slate-400 hover:text-white hover:border-slate-500 transition-all cursor-pointer"
            >
              <RotateCcw className="w-5 h-5" />
            </button>
          </div>
        </form>

        {/* Results - 2 cols */}
        <div className="lg:col-span-2">
          {error && (
            <div className="glass rounded-xl p-5 border border-red-500/30 mb-4 animate-slide-up">
              <div className="flex items-center gap-3 text-red-400">
                <AlertCircle className="w-5 h-5 flex-shrink-0" />
                <div>
                  <p className="font-semibold text-sm">Prediction Error</p>
                  <p className="text-xs text-red-400/70 mt-1">{error}</p>
                </div>
              </div>
            </div>
          )}

          {result ? (
            <PredictionResult result={result} />
          ) : (
            <div className="glass rounded-xl p-8 flex flex-col items-center justify-center text-center min-h-[300px]">
              <div className="w-16 h-16 rounded-2xl bg-slate-800/80 flex items-center justify-center mb-4">
                <Brain className="w-8 h-8 text-slate-600" />
              </div>
              <h4 className="text-white font-semibold">Your Result Will Appear Here</h4>
              <p className="text-slate-500 text-sm mt-2 max-w-xs">
                Fill in your details and click &quot;Find My Coverage&quot; to see
                your personalized recommendation.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

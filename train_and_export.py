"""
train_and_export_v4.py — Single strong model + full-data retrain

Strategy:
  1. Train on 80% split with early stopping → find best iteration + get val proba
  2. Tune thresholds jointly on val proba
  3. Retrain on 100% of data for best_iter * 1.25 iterations (no early stopping)
  4. Save single model — small, fast, no ensemble bloat
"""

import os
import json
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, classification_report
from catboost import CatBoostClassifier, Pool

TARGET_COL = "Purchased_Coverage_Bundle"
ID_COL     = "User_ID"
MODEL_PATH = "model.pkl"
SOLUTION_PATH = "solution.py"
REQS_PATH  = "requirements.txt"
N_CLASSES  = 10
FREQ_ENCODE_COLS = ["Broker_ID", "Employer_ID"]


def compute_freq_maps(df, cols):
    """Compute value-frequency maps for high-cardinality columns (post-preprocessing)."""
    freq_maps = {}
    for c in cols:
        if c in df.columns:
            freq_maps[c] = df[c].value_counts(normalize=True).to_dict()
    return freq_maps


def apply_freq_encoding(df, freq_maps):
    """Apply frequency encoding from precomputed maps."""
    for c, fmap in freq_maps.items():
        if c in df.columns:
            df[f"{c}_freq"] = df[c].map(fmap).fillna(0).astype(np.float32)
    return df


# ── Feature engineering ────────────────────────────────────────────────────

def _to_bool01(series: pd.Series) -> pd.Series:
    s = series.astype("string").str.lower().str.strip()
    yes = {"1", "true", "yes", "y", "t"}
    no  = {"0", "false", "no", "n", "f"}
    out = pd.Series(np.zeros(len(s), dtype=np.float32), index=series.index)
    out[s.isin(yes)] = 1.0
    out[s.isin(no)]  = 0.0
    num = pd.to_numeric(series, errors="coerce")
    out[num.notna()] = (num[num.notna()] != 0).astype(np.float32)
    return out


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    dep_cols = [c for c in ["Adult_Dependents", "Child_Dependents", "Infant_Dependents"] if c in out.columns]
    if dep_cols:
        out["Total_Dependents"] = out[dep_cols].sum(axis=1)
        if "Estimated_Annual_Income" in out.columns:
            income = pd.to_numeric(out["Estimated_Annual_Income"], errors="coerce").clip(lower=0).fillna(0)
            out["Dependents_per_Income"] = out["Total_Dependents"] / (income / 10000 + 1.0)
            out["Income_per_Dependent"]  = income / (out["Total_Dependents"] + 1.0)  # NEW

    if "Adult_Dependents" in out.columns and "Child_Dependents" in out.columns:
        adult = pd.to_numeric(out["Adult_Dependents"], errors="coerce").fillna(0)
        child = pd.to_numeric(out["Child_Dependents"], errors="coerce").fillna(0)
        out["Adult_Child_Ratio"] = adult / (child + 1.0)                             # NEW
        if "Vehicles_on_Policy" in out.columns:
            veh = pd.to_numeric(out["Vehicles_on_Policy"], errors="coerce").fillna(0)
            out["Vehicles_per_Adult"] = veh / (adult + 1.0)                          # NEW

    # ── Family composition ────────────────────────────────────────────────  NEW
    if "Infant_Dependents" in out.columns:
        infant_n = pd.to_numeric(out["Infant_Dependents"], errors="coerce").fillna(0)
        out["Has_Infants"] = (infant_n > 0).astype("float")
    if "Child_Dependents" in out.columns:
        child_n = pd.to_numeric(out["Child_Dependents"], errors="coerce").fillna(0)
        out["Has_Children"] = (child_n > 0).astype("float")
    if "Employer_ID" in out.columns:
        out["Has_Employer"] = out["Employer_ID"].notna().astype("float")              # 94% are NaN

    # ── Income ───────────────────────────────────────────────────────────
    if "Estimated_Annual_Income" in out.columns:
        income = pd.to_numeric(out["Estimated_Annual_Income"], errors="coerce").clip(lower=0).fillna(0)
        out["Log_Income"]    = np.log1p(income)
        out["Income_Bucket"] = pd.cut(income, bins=[-1, 10000, 25000, 50000, 100000, 200000, np.inf], labels=False).astype("float")

    # ── Claims & history ─────────────────────────────────────────────────
    claims = pd.to_numeric(out.get("Previous_Claims_Filed", pd.Series(0, index=out.index)), errors="coerce").fillna(0)
    ncy    = pd.to_numeric(out.get("Years_Without_Claims",  pd.Series(0, index=out.index)), errors="coerce").fillna(0)
    dur    = pd.to_numeric(out.get("Previous_Policy_Duration_Months", pd.Series(0, index=out.index)), errors="coerce").fillna(0)

    if "Previous_Claims_Filed" in out.columns and "Years_Without_Claims" in out.columns:
        out["Claims_per_NoClaimYears"] = claims / (ncy + 1.0)

    if "Previous_Policy_Duration_Months" in out.columns and "Previous_Claims_Filed" in out.columns:
        out["Duration_per_Claim"]  = dur / (claims + 1.0)
        out["Claims_per_Month"]    = claims / (dur + 1.0)
        out["Loyalty_Score"]       = ncy * dur / (claims + 1.0)                      # NEW: loyal low-risk customers
        out["High_Claims_Flag"]    = (claims >= 3).astype("float")                   # NEW
    out["Is_New_Policy"]       = (dur == 0).astype("float")                            # NEW: no prior policy

    # ── Risk composite score ─────────────────────────────────────────────  NEW
    cancelled = _to_bool01(out["Policy_Cancelled_Post_Purchase"]) if "Policy_Cancelled_Post_Purchase" in out.columns else pd.Series(0.0, index=out.index)
    grace     = pd.to_numeric(out.get("Grace_Period_Extensions", pd.Series(0, index=out.index)), errors="coerce").fillna(0)
    out["Risk_Score"] = claims + cancelled + grace                                    # higher = riskier client
    out["Cancelled_x_Claims"] = cancelled * claims                                    # NEW: interaction
    out["Grace_x_Claims"]     = grace * claims                                        # NEW: interaction

    # ── Existing policyholder ────────────────────────────────────────────
    if "Existing_Policyholder" in out.columns:
        out["Existing_Policyholder_01"] = _to_bool01(out["Existing_Policyholder"])
        out["Claims_if_existing"]       = claims * out["Existing_Policyholder_01"]

    if "Policy_Cancelled_Post_Purchase" in out.columns:
        out["Cancelled_01"] = cancelled

    # ── Deductible / riders ──────────────────────────────────────────────
    if "Deductible_Tier" in out.columns and "Custom_Riders_Requested" in out.columns:
        ded = pd.to_numeric(out["Deductible_Tier"], errors="coerce").fillna(0)
        rid = pd.to_numeric(out["Custom_Riders_Requested"], errors="coerce").fillna(0)
        out["Deductible_x_Riders"] = ded * rid
        out["High_Coverage_Flag"]  = ((ded == ded.min()) & (rid > 0)).astype("float") # NEW: low deductible + riders

    # ── Grace / amendments ───────────────────────────────────────────────
    amend = pd.to_numeric(out.get("Policy_Amendments_Count", pd.Series(0, index=out.index)), errors="coerce").fillna(0)
    if "Grace_Period_Extensions" in out.columns and "Policy_Amendments_Count" in out.columns:
        out["Grace_plus_Amendments"] = grace + amend
    if "Policy_Amendments_Count" in out.columns and "Previous_Policy_Duration_Months" in out.columns:
        out["Amendments_per_Month"] = amend / (dur + 1.0)

    # ── Temporal ─────────────────────────────────────────────────────────
    if "Policy_Start_Month" in out.columns:
        _month_map = {"january":1,"february":2,"march":3,"april":4,"may":5,"june":6,
                      "july":7,"august":8,"september":9,"october":10,"november":11,"december":12}
        m = out["Policy_Start_Month"].astype(str).str.lower().str.strip().map(_month_map)
        m = m.fillna(pd.to_numeric(out["Policy_Start_Month"], errors="coerce"))  # fallback if already numeric
        out["Policy_Start_Quarter"] = ((m - 1) // 3 + 1).clip(1, 4)
        out["Is_Year_End"]  = m.isin([11, 12]).astype("float")
        out["Is_Summer"]    = m.isin([6, 7, 8]).astype("float")
        out["Month_sin"]    = np.sin(2 * np.pi * m / 12)                            # NEW: cyclical
        out["Month_cos"]    = np.cos(2 * np.pi * m / 12)                            # NEW: cyclical

    if "Policy_Start_Year" in out.columns:                                            # NEW
        yr = pd.to_numeric(out["Policy_Start_Year"], errors="coerce")
        out["Policy_Year_Normalized"] = yr - yr.min()

    if "Policy_Start_Week" in out.columns:
        w = pd.to_numeric(out["Policy_Start_Week"], errors="coerce")
        out["Policy_Start_Week_Bucket"] = pd.cut(w, bins=[-1, 13, 26, 39, 53], labels=False).astype("float")
        out["Week_sin"] = np.sin(2 * np.pi * w / 52)                                # NEW: cyclical
        out["Week_cos"] = np.cos(2 * np.pi * w / 52)                                # NEW: cyclical

    if "Policy_Start_Day" in out.columns:
        d = pd.to_numeric(out["Policy_Start_Day"], errors="coerce")
        out["Is_Month_Start"] = (d <= 5).astype("float")
        out["Is_Month_End"]   = (d >= 25).astype("float")

    # ── Operational ──────────────────────────────────────────────────────
    if "Days_Since_Quote" in out.columns and "Underwriting_Processing_Days" in out.columns:
        dsq = pd.to_numeric(out["Days_Since_Quote"], errors="coerce")
        uw  = pd.to_numeric(out["Underwriting_Processing_Days"], errors="coerce")
        out["Quote_to_UW_Ratio"] = dsq / (uw + 1.0)
        out["Quote_plus_UW"]     = (dsq.fillna(0) + uw.fillna(0)).astype("float")
        out["Long_UW_Flag"]      = (uw > uw.quantile(0.75)).astype("float")
        out["Quote_Urgency"]     = dsq / (dsq + uw + 1.0)                            # NEW: how much of total time was quote phase
        out["Log_DSQ"]           = np.log1p(dsq.fillna(0).clip(lower=0))             # NEW

    # ── Vehicles / riders ────────────────────────────────────────────────
    if "Vehicles_on_Policy" in out.columns and "Custom_Riders_Requested" in out.columns:
        veh = pd.to_numeric(out["Vehicles_on_Policy"], errors="coerce").fillna(0)
        rid = pd.to_numeric(out["Custom_Riders_Requested"], errors="coerce").fillna(0)
        out["Vehicles_x_Riders"]  = veh * rid
        out["Riders_per_Vehicle"] = rid / (veh + 1.0)

    # ── Complexity & need proxies ────────────────────────────────────────
    total_dep = pd.to_numeric(out.get("Total_Dependents", pd.Series(0, index=out.index)), errors="coerce").fillna(0)
    veh_n = pd.to_numeric(out.get("Vehicles_on_Policy", pd.Series(0, index=out.index)), errors="coerce").fillna(0)
    rid_n = pd.to_numeric(out.get("Custom_Riders_Requested", pd.Series(0, index=out.index)), errors="coerce").fillna(0)
    out["Policy_Complexity"] = total_dep + veh_n + rid_n

    if "Estimated_Annual_Income" in out.columns:
        income_n = pd.to_numeric(out["Estimated_Annual_Income"], errors="coerce").clip(lower=0).fillna(0)
        out["Coverage_Need"]       = np.log1p(income_n) * (total_dep + 1)
        out["Affordability"]       = income_n / (out["Policy_Complexity"] + 1)
        out["Income_x_Dependents"] = income_n * total_dep

    # ── Extra claims intensity ───────────────────────────────────────────
    if "Previous_Claims_Filed" in out.columns:
        out["Claims_Squared"]      = claims ** 2                                       # burstiness
        out["Claims_Acceleration"] = (claims ** 2) / (dur + 1.0)                      # claims² per duration month
        out["No_Claims_Ratio"]     = ncy / (ncy + claims + 1.0)                       # fraction of time claim-free
    if "Previous_Claims_Filed" in out.columns and "Previous_Policy_Duration_Months" in out.columns:
        out["Claim_Gap"]           = ncy - dur                                         # negative → gap > policy life
    if "Previous_Claims_Filed" in out.columns and "Years_Without_Claims" in out.columns:
        out["Claims_NCY_Interact"] = claims * ncy                                      # high claims + long clean tail

    # ── Extra income transforms ──────────────────────────────────────────
    if "Estimated_Annual_Income" in out.columns:
        income_n = pd.to_numeric(out["Estimated_Annual_Income"], errors="coerce").clip(lower=0).fillna(0)
        out["Sqrt_Income"]         = np.sqrt(income_n)
        out["Income_Risk_Ratio"]   = income_n / (out["Risk_Score"] + 1.0)             # how wealthy relative to risk
        log_inc = out["Log_Income"] if "Log_Income" in out.columns else np.log1p(income_n)
        ibucket = pd.cut(income_n, bins=[-1, 10000, 25000, 50000, 100000, 200000, np.inf],
                         labels=False).fillna(0).astype("float")
        out["Income_Volatility_Proxy"] = log_inc / (ibucket + 1.0)                    # dispersion within bucket

    # ── Extended temporal features ───────────────────────────────────────
    if "Policy_Start_Month" in out.columns:
        # Re-derive numeric month (already computed above but not stored as numeric col)
        _month_map_ext = {"january": 1, "february": 2, "march": 3, "april": 4,
                          "may": 5, "june": 6, "july": 7, "august": 8,
                          "september": 9, "october": 10, "november": 11, "december": 12}
        m_ext = out["Policy_Start_Month"].astype(str).str.lower().str.strip().map(_month_map_ext)
        m_ext = m_ext.fillna(pd.to_numeric(out["Policy_Start_Month"], errors="coerce"))
        out["Is_Spring"]   = m_ext.isin([3, 4, 5]).astype("float")
        out["Is_Fall"]     = m_ext.isin([9, 10, 11]).astype("float")
        out["Is_Winter"]   = m_ext.isin([12, 1, 2]).astype("float")
        out["Is_Q1"]       = m_ext.isin([1, 2, 3]).astype("float")
        out["Is_Q4"]       = m_ext.isin([10, 11, 12]).astype("float")

    if "Policy_Start_Day" in out.columns:
        d = pd.to_numeric(out["Policy_Start_Day"], errors="coerce").fillna(15)
        out["Day_sin"]          = np.sin(2 * np.pi * d / 31)                          # cyclical day-of-month
        out["Day_cos"]          = np.cos(2 * np.pi * d / 31)
        out["Day_of_Month_Bucket"] = pd.cut(d, bins=[-1, 10, 20, 31],
                                            labels=False).astype("float")             # early/mid/late

    if "Policy_Start_Week" in out.columns:
        w = pd.to_numeric(out["Policy_Start_Week"], errors="coerce").fillna(26)
        out["Is_Year_Start_Week"] = (w <= 4).astype("float")                          # first month of year
        out["Is_Year_End_Week"]   = (w >= 49).astype("float")                         # last month of year

    # ── Operational depth ────────────────────────────────────────────────
    if "Days_Since_Quote" in out.columns and "Underwriting_Processing_Days" in out.columns:
        dsq = pd.to_numeric(out["Days_Since_Quote"], errors="coerce").fillna(0).clip(lower=0)
        uw  = pd.to_numeric(out["Underwriting_Processing_Days"], errors="coerce").fillna(0).clip(lower=0)
        out["Log_UW"]             = np.log1p(uw)
        out["UW_Efficiency"]      = uw / (dsq + 1.0)                                  # uw relative to quote time
        out["DSQ_Bucket"]         = pd.cut(dsq, bins=[-1, 0, 7, 30, 90, 365, np.inf],
                                           labels=False).astype("float")              # quote recency tier
        total_wait = dsq + uw
        out["Avg_Process_Step"]   = total_wait / 2.0                                  # mean of both steps

    # ── Coverage interactions ────────────────────────────────────────────
    if "Custom_Riders_Requested" in out.columns:
        rid = pd.to_numeric(out["Custom_Riders_Requested"], errors="coerce").fillna(0)
        if "Total_Dependents" in out.columns:
            out["Riders_x_Dependents"] = rid * total_dep                              # more dependents + more riders
        if "Estimated_Annual_Income" in out.columns:
            income_n = pd.to_numeric(out["Estimated_Annual_Income"], errors="coerce").clip(lower=0).fillna(0)
            out["Policy_Load"]     = out["Policy_Complexity"] / (income_n / 50000.0 + 1.0)  # complexity relative to income
        out["Dep_Coverage_Density"] = (total_dep + veh_n) / (rid + 1.0)              # coverage spread per rider

    # ── Cancellation / grace cross-interactions ──────────────────────────
    if "Grace_Period_Extensions" in out.columns and "Policy_Amendments_Count" in out.columns:
        out["Grace_x_Amended"]       = grace * amend
    if "Policy_Cancelled_Post_Purchase" in out.columns:
        out["Cancelled_x_Duration"]  = cancelled * dur
        out["Cancelled_x_Amended"]   = cancelled * amend
        if "Estimated_Annual_Income" in out.columns:
            income_n = pd.to_numeric(out["Estimated_Annual_Income"], errors="coerce").clip(lower=0).fillna(0)
            log_inc  = np.log1p(income_n)
            out["Risk_x_Income"]     = out["Risk_Score"] / (log_inc + 1.0)

    # ── Broker dominance flags ────────────────────────────────────────────
    if "Broker_ID" in out.columns:
        # Top-5 most common broker IDs from training data (9, 14, 240, 7, 250)
        top5_brokers = {9.0, 14.0, 240.0, 7.0, 250.0}
        bid = pd.to_numeric(out["Broker_ID"], errors="coerce")
        out["Is_Top_Broker"]   = bid.isin(top5_brokers).astype("float")               # dominant brokers
        out["Is_Rare_Broker"]  = (~bid.isin(top5_brokers) & bid.notna()).astype("float")

    # ── Employer-related ─────────────────────────────────────────────────
    if "Employer_ID" in out.columns and "Estimated_Annual_Income" in out.columns:
        income_n = pd.to_numeric(out["Estimated_Annual_Income"], errors="coerce").clip(lower=0).fillna(0)
        has_emp  = out["Has_Employer"] if "Has_Employer" in out.columns else out["Employer_ID"].notna().astype("float")
        out["Employer_x_Income"] = has_emp * income_n                                 # income only if employed

    # ── Policy age / tenure features ─────────────────────────────────────
    if "Policy_Start_Year" in out.columns:
        yr = pd.to_numeric(out["Policy_Start_Year"], errors="coerce").fillna(2016)
        out["Policy_Age_2025"] = (2025 - yr).clip(lower=0)                            # years old relative to now
        out["Is_Recent_Policy"] = (yr >= 2017).astype("float")

    # ── Amendment intensity ──────────────────────────────────────────────
    if "Policy_Amendments_Count" in out.columns:
        out["High_Amendment_Flag"] = (amend >= 2).astype("float")
        out["Amend_x_Claims"]      = amend * claims
        out["Amend_x_Grace"]       = amend * grace

    return out


def infer_column_types(df: pd.DataFrame):
    cols = [c for c in df.columns if c not in [TARGET_COL, ID_COL]]
    cat_cols, num_cols = [], []
    for c in cols:
        if pd.api.types.is_numeric_dtype(df[c]):
            num_cols.append(c)
        else:
            cat_cols.append(c)
    return cat_cols, num_cols


def compute_class_weights(y: pd.Series, power: float = 0.65) -> dict:
    counts = y.value_counts().sort_index()
    total  = len(y)
    return {int(cls): float((total / cnt) ** power) for cls, cnt in counts.items()}


# ── Threshold tuning (joint random search) ─────────────────────────────────

def tune_thresholds(proba: np.ndarray, y_val: np.ndarray, n_classes: int,
                    n_iter: int = 1500, random_state: int = 42):
    rng = np.random.RandomState(random_state)
    base_pred = np.argmax(proba, axis=1)
    best_f1   = f1_score(y_val, base_pred, average="macro")
    best_mult = np.ones(n_classes)

    low  = np.array([0.7, 0.8, 0.9, 0.8, 0.9, 0.7, 0.7, 0.8, 0.8, 0.8])
    high = np.array([1.4, 1.3, 1.3, 1.4, 1.4, 1.8, 1.8, 1.5, 1.5, 1.5])

    for _ in range(n_iter):
        mult     = rng.uniform(low, high)
        adjusted = proba * mult[np.newaxis, :]
        preds    = np.argmax(adjusted, axis=1)
        f1       = f1_score(y_val, preds, average="macro")
        if f1 > best_f1:
            best_f1   = f1
            best_mult = mult.copy()

    print(f"  Best joint multipliers: {np.round(best_mult, 2)}")
    print(f"  Joint tuning F1: {best_f1:.5f}")
    adjusted = proba * best_mult[np.newaxis, :]
    return best_mult, np.argmax(adjusted, axis=1)


# ── Train helper ───────────────────────────────────────────────────────────

def train_catboost(pool_train, pool_val, params, use_best_model=True):
    # GPU-safe params: remove CPU-only options
    gpu_params = {k: v for k, v in params.items()
                  if k not in ("colsample_bylevel", "thread_count")}
    # CatBoost GPU needs Bernoulli bootstrap for subsample
    if "subsample" in gpu_params and "bootstrap_type" not in gpu_params:
        gpu_params["bootstrap_type"] = "Bernoulli"

    try:
        model = CatBoostClassifier(task_type="GPU", devices="0", **gpu_params)
        eval_set = pool_val if pool_val is not None else None
        model.fit(pool_train, eval_set=eval_set, use_best_model=use_best_model)
        print("  [GPU training]")
    except Exception as e:
        print(f"  [GPU failed: {e}] — falling back to CPU (this will be slow!)")
        cpu_params = dict(**params)
        cpu_params.pop("bootstrap_type", None)
        cpu_params.pop("subsample", None)
        cpu_params.pop("colsample_bylevel", None)
        model = CatBoostClassifier(thread_count=-1, **cpu_params)
        eval_set = pool_val if pool_val is not None else None
        model.fit(pool_train, eval_set=eval_set, use_best_model=use_best_model)
    return model


# ── Write solution.py ──────────────────────────────────────────────────────

def write_requirements_txt():
    open(REQS_PATH, "w").close()


def write_solution_py(feature_cols_model, cat_cols, num_cols, thresholds, freq_maps):
    # Serialize freq_maps: convert numeric keys to strings for JSON, reconvert in generated code
    freq_maps_safe = {}
    for col, fmap in freq_maps.items():
        freq_maps_safe[col] = {repr(k): v for k, v in fmap.items()}
    freq_maps_json = json.dumps(freq_maps_safe)

    content = f'''# Auto-generated — do not edit function signatures
import json as _json
import joblib, numpy as np, pandas as pd

ID_COL       = "{ID_COL}"
FEATURE_COLS = {json.dumps(feature_cols_model)}
CAT_COLS     = {json.dumps(cat_cols)}
NUM_COLS     = {json.dumps(num_cols)}
THRESHOLDS   = {json.dumps(thresholds.tolist())}

# Frequency maps for high-cardinality ID columns (computed from training data)
_FREQ_MAPS_RAW = '{freq_maps_json}'
FREQ_MAPS = {{col: {{eval(k): v for k, v in fmap.items()}} for col, fmap in _json.loads(_FREQ_MAPS_RAW).items()}}


def _to_bool01(series):
    s = series.astype("string").str.lower().str.strip()
    yes, no = {{"1","true","yes","y","t"}}, {{"0","false","no","n","f"}}
    out = pd.Series(np.zeros(len(s), dtype=np.float32), index=series.index)
    out[s.isin(yes)] = 1.0; out[s.isin(no)] = 0.0
    num = pd.to_numeric(series, errors="coerce")
    out[num.notna()] = (num[num.notna()] != 0).astype(np.float32)
    return out


def _build_features(df):
    out = df.copy()
    dep_cols = [c for c in ["Adult_Dependents","Child_Dependents","Infant_Dependents"] if c in out.columns]
    if dep_cols:
        out["Total_Dependents"] = out[dep_cols].sum(axis=1)
        if "Estimated_Annual_Income" in out.columns:
            inc = pd.to_numeric(out["Estimated_Annual_Income"], errors="coerce").clip(lower=0).fillna(0)
            out["Dependents_per_Income"] = out["Total_Dependents"] / (inc / 10000 + 1.0)
            out["Income_per_Dependent"]  = inc / (out["Total_Dependents"] + 1.0)
    if "Adult_Dependents" in out.columns and "Child_Dependents" in out.columns:
        adult = pd.to_numeric(out["Adult_Dependents"], errors="coerce").fillna(0)
        child = pd.to_numeric(out["Child_Dependents"], errors="coerce").fillna(0)
        out["Adult_Child_Ratio"] = adult / (child + 1.0)
        if "Vehicles_on_Policy" in out.columns:
            veh = pd.to_numeric(out["Vehicles_on_Policy"], errors="coerce").fillna(0)
            out["Vehicles_per_Adult"] = veh / (adult + 1.0)
    # Family composition
    if "Infant_Dependents" in out.columns:
        infant_n = pd.to_numeric(out["Infant_Dependents"], errors="coerce").fillna(0)
        out["Has_Infants"] = (infant_n > 0).astype("float")
    if "Child_Dependents" in out.columns:
        child_n = pd.to_numeric(out["Child_Dependents"], errors="coerce").fillna(0)
        out["Has_Children"] = (child_n > 0).astype("float")
    if "Employer_ID" in out.columns:
        out["Has_Employer"] = out["Employer_ID"].notna().astype("float")
    # Income
    if "Estimated_Annual_Income" in out.columns:
        inc = pd.to_numeric(out["Estimated_Annual_Income"], errors="coerce").clip(lower=0).fillna(0)
        out["Log_Income"] = np.log1p(inc)
        out["Income_Bucket"] = pd.cut(inc, bins=[-1,10000,25000,50000,100000,200000,np.inf], labels=False).astype("float")
    claims = pd.to_numeric(out.get("Previous_Claims_Filed", pd.Series(0, index=out.index)), errors="coerce").fillna(0)
    ncy    = pd.to_numeric(out.get("Years_Without_Claims",  pd.Series(0, index=out.index)), errors="coerce").fillna(0)
    dur    = pd.to_numeric(out.get("Previous_Policy_Duration_Months", pd.Series(0, index=out.index)), errors="coerce").fillna(0)
    if "Previous_Claims_Filed" in out.columns and "Years_Without_Claims" in out.columns:
        out["Claims_per_NoClaimYears"] = claims / (ncy + 1.0)
    if "Previous_Policy_Duration_Months" in out.columns and "Previous_Claims_Filed" in out.columns:
        out["Duration_per_Claim"] = dur / (claims + 1.0)
        out["Claims_per_Month"]   = claims / (dur + 1.0)
        out["Loyalty_Score"]      = ncy * dur / (claims + 1.0)
        out["High_Claims_Flag"]   = (claims >= 3).astype("float")
    out["Is_New_Policy"] = (dur == 0).astype("float")
    cancelled = _to_bool01(out["Policy_Cancelled_Post_Purchase"]) if "Policy_Cancelled_Post_Purchase" in out.columns else pd.Series(0.0, index=out.index)
    grace     = pd.to_numeric(out.get("Grace_Period_Extensions", pd.Series(0, index=out.index)), errors="coerce").fillna(0)
    out["Risk_Score"] = claims + cancelled + grace
    out["Cancelled_x_Claims"] = cancelled * claims
    out["Grace_x_Claims"]     = grace * claims
    if "Existing_Policyholder" in out.columns:
        out["Existing_Policyholder_01"] = _to_bool01(out["Existing_Policyholder"])
        out["Claims_if_existing"] = claims * out["Existing_Policyholder_01"]
    if "Policy_Cancelled_Post_Purchase" in out.columns:
        out["Cancelled_01"] = cancelled
    if "Deductible_Tier" in out.columns and "Custom_Riders_Requested" in out.columns:
        ded = pd.to_numeric(out["Deductible_Tier"], errors="coerce").fillna(0)
        rid = pd.to_numeric(out["Custom_Riders_Requested"], errors="coerce").fillna(0)
        out["Deductible_x_Riders"] = ded * rid
        out["High_Coverage_Flag"]  = ((ded == ded.min()) & (rid > 0)).astype("float")
    amend = pd.to_numeric(out.get("Policy_Amendments_Count", pd.Series(0, index=out.index)), errors="coerce").fillna(0)
    if "Grace_Period_Extensions" in out.columns and "Policy_Amendments_Count" in out.columns:
        out["Grace_plus_Amendments"] = grace + amend
    if "Policy_Amendments_Count" in out.columns and "Previous_Policy_Duration_Months" in out.columns:
        out["Amendments_per_Month"] = amend / (dur + 1.0)
    if "Policy_Start_Month" in out.columns:
        _month_map = {{"january":1,"february":2,"march":3,"april":4,"may":5,"june":6,
                      "july":7,"august":8,"september":9,"october":10,"november":11,"december":12}}
        m = out["Policy_Start_Month"].astype(str).str.lower().str.strip().map(_month_map)
        m = m.fillna(pd.to_numeric(out["Policy_Start_Month"], errors="coerce"))
        out["Policy_Start_Quarter"] = ((m - 1) // 3 + 1).clip(1, 4)
        out["Is_Year_End"] = m.isin([11,12]).astype("float")
        out["Is_Summer"]   = m.isin([6,7,8]).astype("float")
        out["Month_sin"]   = np.sin(2 * np.pi * m / 12)
        out["Month_cos"]   = np.cos(2 * np.pi * m / 12)
        out["Is_Spring"]   = m.isin([3,4,5]).astype("float")
        out["Is_Fall"]     = m.isin([9,10,11]).astype("float")
        out["Is_Winter"]   = m.isin([12,1,2]).astype("float")
        out["Is_Q1"]       = m.isin([1,2,3]).astype("float")
        out["Is_Q4"]       = m.isin([10,11,12]).astype("float")
    if "Policy_Start_Year" in out.columns:
        yr = pd.to_numeric(out["Policy_Start_Year"], errors="coerce")
        out["Policy_Year_Normalized"] = yr - yr.min()
        out["Policy_Age_2025"]  = (2025 - yr).clip(lower=0)
        out["Is_Recent_Policy"] = (yr >= 2017).astype("float")
    if "Policy_Start_Week" in out.columns:
        w = pd.to_numeric(out["Policy_Start_Week"], errors="coerce")
        out["Policy_Start_Week_Bucket"] = pd.cut(w, bins=[-1,13,26,39,53], labels=False).astype("float")
        out["Week_sin"] = np.sin(2 * np.pi * w / 52)
        out["Week_cos"] = np.cos(2 * np.pi * w / 52)
        out["Is_Year_Start_Week"] = (w <= 4).astype("float")
        out["Is_Year_End_Week"]   = (w >= 49).astype("float")
    if "Policy_Start_Day" in out.columns:
        d = pd.to_numeric(out["Policy_Start_Day"], errors="coerce").fillna(15)
        out["Is_Month_Start"]      = (d <= 5).astype("float")
        out["Is_Month_End"]        = (d >= 25).astype("float")
        out["Day_sin"]             = np.sin(2 * np.pi * d / 31)
        out["Day_cos"]             = np.cos(2 * np.pi * d / 31)
        out["Day_of_Month_Bucket"] = pd.cut(d, bins=[-1,10,20,31], labels=False).astype("float")
    if "Days_Since_Quote" in out.columns and "Underwriting_Processing_Days" in out.columns:
        dsq = pd.to_numeric(out["Days_Since_Quote"], errors="coerce").fillna(0).clip(lower=0)
        uw  = pd.to_numeric(out["Underwriting_Processing_Days"], errors="coerce").fillna(0).clip(lower=0)
        out["Quote_to_UW_Ratio"] = dsq / (uw + 1.0)
        out["Quote_plus_UW"]     = (dsq + uw).astype("float")
        out["Long_UW_Flag"]      = (uw > uw.quantile(0.75)).astype("float")
        out["Quote_Urgency"]     = dsq / (dsq + uw + 1.0)
        out["Log_DSQ"]           = np.log1p(dsq)
        out["Log_UW"]            = np.log1p(uw)
        out["UW_Efficiency"]     = uw / (dsq + 1.0)
        out["DSQ_Bucket"]        = pd.cut(dsq, bins=[-1,0,7,30,90,365,np.inf], labels=False).astype("float")
        out["Avg_Process_Step"]  = (dsq + uw) / 2.0
    if "Vehicles_on_Policy" in out.columns and "Custom_Riders_Requested" in out.columns:
        veh = pd.to_numeric(out["Vehicles_on_Policy"], errors="coerce").fillna(0)
        rid = pd.to_numeric(out["Custom_Riders_Requested"], errors="coerce").fillna(0)
        out["Vehicles_x_Riders"]  = veh * rid
        out["Riders_per_Vehicle"] = rid / (veh + 1.0)
    # Complexity & need proxies
    total_dep = pd.to_numeric(out.get("Total_Dependents", pd.Series(0, index=out.index)), errors="coerce").fillna(0)
    veh_n = pd.to_numeric(out.get("Vehicles_on_Policy", pd.Series(0, index=out.index)), errors="coerce").fillna(0)
    rid_n = pd.to_numeric(out.get("Custom_Riders_Requested", pd.Series(0, index=out.index)), errors="coerce").fillna(0)
    out["Policy_Complexity"] = total_dep + veh_n + rid_n
    if "Estimated_Annual_Income" in out.columns:
        income_n = pd.to_numeric(out["Estimated_Annual_Income"], errors="coerce").clip(lower=0).fillna(0)
        out["Coverage_Need"]       = np.log1p(income_n) * (total_dep + 1)
        out["Affordability"]       = income_n / (out["Policy_Complexity"] + 1)
        out["Income_x_Dependents"] = income_n * total_dep
        out["Sqrt_Income"]         = np.sqrt(income_n)
        out["Income_Risk_Ratio"]   = income_n / (out["Risk_Score"] + 1.0)
        ibucket = pd.cut(income_n, bins=[-1,10000,25000,50000,100000,200000,np.inf], labels=False).fillna(0).astype("float")
        out["Income_Volatility_Proxy"] = np.log1p(income_n) / (ibucket + 1.0)
        out["Income_Risk_Ratio"]   = income_n / (out["Risk_Score"] + 1.0)
        if "Has_Employer" in out.columns:
            out["Employer_x_Income"] = out["Has_Employer"] * income_n
        if "Custom_Riders_Requested" in out.columns:
            out["Policy_Load"] = out["Policy_Complexity"] / (income_n / 50000.0 + 1.0)
    # Extra claims intensity
    if "Previous_Claims_Filed" in out.columns:
        out["Claims_Squared"]      = claims ** 2
        out["Claims_Acceleration"] = (claims ** 2) / (dur + 1.0)
        out["No_Claims_Ratio"]     = ncy / (ncy + claims + 1.0)
    if "Previous_Claims_Filed" in out.columns and "Previous_Policy_Duration_Months" in out.columns:
        out["Claim_Gap"]           = ncy - dur
    if "Previous_Claims_Filed" in out.columns and "Years_Without_Claims" in out.columns:
        out["Claims_NCY_Interact"] = claims * ncy
    # Coverage interactions
    if "Custom_Riders_Requested" in out.columns:
        rid = pd.to_numeric(out["Custom_Riders_Requested"], errors="coerce").fillna(0)
        out["Riders_x_Dependents"]  = rid * total_dep
        out["Dep_Coverage_Density"] = (total_dep + veh_n) / (rid + 1.0)
    # Cross-interactions
    if "Grace_Period_Extensions" in out.columns and "Policy_Amendments_Count" in out.columns:
        out["Grace_x_Amended"]      = grace * amend
    if "Policy_Cancelled_Post_Purchase" in out.columns:
        out["Cancelled_x_Duration"] = cancelled * dur
        out["Cancelled_x_Amended"]  = cancelled * amend
        if "Estimated_Annual_Income" in out.columns:
            income_n = pd.to_numeric(out["Estimated_Annual_Income"], errors="coerce").clip(lower=0).fillna(0)
            out["Risk_x_Income"]    = out["Risk_Score"] / (np.log1p(income_n) + 1.0)
    # Broker dominance
    if "Broker_ID" in out.columns:
        top5_brokers = {{9.0, 14.0, 240.0, 7.0, 250.0}}
        bid = pd.to_numeric(out["Broker_ID"], errors="coerce")
        out["Is_Top_Broker"]  = bid.isin(top5_brokers).astype("float")
        out["Is_Rare_Broker"] = (~bid.isin(top5_brokers) & bid.notna()).astype("float")
    # Amendment intensity
    if "Policy_Amendments_Count" in out.columns:
        out["High_Amendment_Flag"] = (amend >= 2).astype("float")
        out["Amend_x_Claims"]      = amend * claims
        out["Amend_x_Grace"]       = amend * grace
    return out


def preprocess(df):
    out = _build_features(df)
    for c in FEATURE_COLS:
        if c not in out.columns: out[c] = np.nan
    for c in CAT_COLS:
        if c in out.columns: out[c] = out[c].astype("string").fillna("__MISSING__")
    for c in NUM_COLS:
        if c in out.columns: out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0.0)
    return out


def load_model():
    return joblib.load("model.pkl")


def predict(df, model):
    clf        = model["model"]
    thresholds = np.array(model["thresholds"])
    # Apply frequency encoding from training-time maps
    freq_maps  = model.get("freq_maps", {{}})
    for c, fmap in freq_maps.items():
        if c in df.columns:
            df[f"{{c}}_freq"] = df[c].map(fmap).fillna(0).astype(np.float32)
    X          = df[FEATURE_COLS]
    proba      = clf.predict_proba(X)
    adjusted   = proba * thresholds[np.newaxis, :]
    preds      = np.argmax(adjusted, axis=1).astype(int)
    return pd.DataFrame({{
        "User_ID": df[ID_COL].values,
        "Purchased_Coverage_Bundle": preds
    }})
'''
    with open(SOLUTION_PATH, "w", encoding="utf-8") as f:
        f.write(content)


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    if not os.path.exists("train.csv"):
        raise FileNotFoundError("train.csv not found.")

    print("Loading & engineering features…")
    df = pd.read_csv("train.csv")
    df = build_features(df)

    cat_cols, num_cols = infer_column_types(df)
    for c in cat_cols:
        df[c] = df[c].astype("string").fillna("__MISSING__")
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(df[c].median())

    # Frequency encoding for high-cardinality IDs (computed after type normalization)
    freq_maps = compute_freq_maps(df, FREQ_ENCODE_COLS)
    df = apply_freq_encoding(df, freq_maps)
    print(f"Frequency-encoded columns: {[f'{c}_freq' for c in freq_maps]}")

    feature_cols = [c for c in df.columns if c not in [TARGET_COL, ID_COL]]
    X = df[feature_cols]
    y = df[TARGET_COL].astype(int)
    cat_indices = [i for i, c in enumerate(feature_cols) if c in cat_cols]

    print("\nClass distribution:")
    print(y.value_counts().sort_index())

    class_weights = compute_class_weights(y, power=0.65)
    print("\nClass weights:", {k: round(v, 2) for k, v in class_weights.items()})

    # 80/20 split for val
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    train_pool = Pool(X_train, y_train, cat_features=cat_indices)
    val_pool   = Pool(X_val,   y_val,   cat_features=cat_indices)

    params_val = dict(
        loss_function="MultiClass",
        eval_metric="TotalF1",
        class_weights=class_weights,
        depth=9,
        learning_rate=0.05,
        l2_leaf_reg=6.0,
        subsample=0.85,           # row subsampling — adds variance reduction
        colsample_bylevel=0.85,   # feature subsampling per split — reduces overfitting
        iterations=2500,
        od_type="Iter",
        od_wait=150,
        allow_writing_files=False,
        verbose=200,
        bootstrap_type="Bernoulli",  # required for subsample to work on CPU
    )

    # ── Step 1: Train 3 seeds on 80%, pick best ──────────────────────────
    print("\nStep 1: Training 3 seeds on 80% split…\n")
    seeds = [42, 7, 2025]
    best_val_f1, best_iter, best_val_proba = -1.0, 0, None

    for seed in seeds:
        p = dict(**params_val, random_seed=seed)
        m = train_catboost(train_pool, val_pool, p, use_best_model=True)
        proba = m.predict_proba(X_val)
        f1    = f1_score(y_val, np.argmax(proba, axis=1), average="macro")
        iters = m.tree_count_
        print(f"  seed={seed}: Val F1={f1:.5f}  best_iter={iters}")
        if f1 > best_val_f1:
            best_val_f1, best_iter, best_val_proba = f1, iters, proba
            best_seed = seed

    val_proba = best_val_proba
    val_f1    = best_val_f1
    val_preds = np.argmax(val_proba, axis=1)
    print(f"\nBest seed={best_seed}  Val Macro F1={val_f1:.5f}  best_iter={best_iter}")
    print(classification_report(y_val, val_preds, zero_division=0))
    # Update params_val with winning seed for full retrain
    params_val["random_seed"] = best_seed

    # ── Step 2: Tune thresholds ───────────────────────────────────────────
    print("\nStep 2: Tuning per-class thresholds…")
    threshold_multipliers, tuned_preds = tune_thresholds(val_proba, y_val.values, N_CLASSES)
    tuned_f1 = f1_score(y_val, tuned_preds, average="macro")
    print(classification_report(y_val, tuned_preds, zero_division=0))

    if tuned_f1 >= val_f1:
        final_thresholds = threshold_multipliers
        final_f1 = tuned_f1
        print(f"  → Using tuned thresholds ({tuned_f1:.5f} vs {val_f1:.5f})")
    else:
        final_thresholds = np.ones(N_CLASSES)
        final_f1 = val_f1
        print(f"  → Reverting (tuning hurt: {tuned_f1:.5f} < {val_f1:.5f})")

    # ── Step 3: Retrain on 100% data, fixed iterations ───────────────────
    full_iter = int(best_iter * 1.30)
    print(f"\nStep 3: Retraining on 100% data for {full_iter} iterations…")
    full_pool   = Pool(X, y, cat_features=cat_indices)
    params_full = {k: v for k, v in params_val.items()
                   if k not in ("od_type", "od_wait", "iterations")}
    params_full["iterations"] = full_iter

    final_model = train_catboost(full_pool, None, params_full, use_best_model=False)

    # ── Save ──────────────────────────────────────────────────────────────
    artifact = {
        "model":              final_model,          # single model (not list)
        "thresholds":         final_thresholds.tolist(),
        "feature_cols_model": feature_cols,
        "cat_cols":           cat_cols,
        "num_cols":           num_cols,
        "freq_maps":          freq_maps,             # for inference-time freq encoding
    }
    joblib.dump(artifact, MODEL_PATH, compress=3)
    size_mb = os.path.getsize(MODEL_PATH) / 1e6
    print(f"Saved → {MODEL_PATH}  ({size_mb:.1f} MB)")

    write_solution_py(feature_cols, cat_cols, num_cols, final_thresholds, freq_maps)
    write_requirements_txt()
    print(f"Wrote {SOLUTION_PATH} and {REQS_PATH}")

    # ── Sanity check ──────────────────────────────────────────────────────
    if os.path.exists("test.csv"):
        import importlib.util
        spec = importlib.util.spec_from_file_location("solution", SOLUTION_PATH)
        sol  = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sol)

        df_test = pd.read_csv("test.csv")
        df_proc = sol.preprocess(df_test)
        art2    = sol.load_model()
        preds   = sol.predict(df_proc, art2)

        print("\nTest prediction distribution:")
        print(preds["Purchased_Coverage_Bundle"].value_counts(normalize=True).sort_index())
        preds.to_csv("submission.csv", index=False)
        print("Saved submission.csv")

        size_penalty = max(0.5, 1 - size_mb / 200)
        print(f"\nModel: {size_mb:.1f} MB  →  penalty: {size_penalty:.3f}")
        print(f"Val F1 (best): {final_f1:.5f}")
        print(f"Estimated leaderboard score: {final_f1 * size_penalty:.4f}")


if __name__ == "__main__":
    main()
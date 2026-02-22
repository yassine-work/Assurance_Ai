"""
Retraining Pipeline for AssuranceAI
====================================

WHAT THIS DOES:
  This script retrains the CatBoost model when new training data is available.
  It follows these safety steps:

    1. Load new training data (CSV)
    2. Train a new model using the SAME pipeline as train_and_export.py
    3. Evaluate the new model on a held-out validation set
    4. Compare new model's F1 score against the current model
    5. Only replace model.pkl if the new model is BETTER (safety guard)
    6. Optionally clear the prediction cache (since model changed)

HOW TO USE:
  Locally:
    python scripts/retrain.py --data path/to/new_train.csv

  Via GitHub Actions (see .github/workflows/retrain.yml):
    - Triggered manually or on a schedule
    - Uploads the new model as an artifact

SAFETY:
  - Old model is backed up as model_backup.pkl before replacement
  - If new model is worse, it is NOT saved (you get a warning)
  - All metrics are logged to retrain_log.json for audit trail
"""

import os
import sys
import json
import shutil
import argparse
from datetime import datetime

import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, classification_report

# Add project root to path so we can import from model/ directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(PROJECT_ROOT, "model")
sys.path.insert(0, PROJECT_ROOT)

TARGET_COL = "Purchased_Coverage_Bundle"
ID_COL = "User_ID"
N_CLASSES = 10
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
BACKUP_PATH = os.path.join(MODEL_DIR, "model_backup.pkl")
LOG_PATH = os.path.join(PROJECT_ROOT, "retrain_log.json")


def load_current_model():
    """Load the currently deployed model."""
    if not os.path.exists(MODEL_PATH):
        print("  ⚠ No existing model.pkl found — this will be the first model.")
        return None
    return joblib.load(MODEL_PATH)


def evaluate_model(artifact, X_val, y_val):
    """
    Evaluate a model artifact on validation data.
    Returns (macro_f1, predictions).
    Uses the threshold-adjusted prediction logic from the original pipeline.
    """
    clf = artifact["model"]
    thresholds = np.array(artifact["thresholds"])

    proba = clf.predict_proba(X_val)
    adjusted = proba * thresholds[np.newaxis, :]
    preds = np.argmax(adjusted, axis=1)

    f1 = f1_score(y_val, preds, average="macro")
    return f1, preds


def retrain(data_path: str, force: bool = False):
    """
    Full retraining pipeline — mirrors train_and_export.py exactly.

    Args:
        data_path: Path to new training CSV (same format as train.csv)
        force: If True, replace model even if new one scores lower
    """
    print("=" * 60)
    print("  AssuranceAI — Model Retraining Pipeline")
    print("=" * 60)

    # ── Step 1: Load data ──────────────────────────────────────────────
    print(f"\n📂 Loading data from: {data_path}")
    df = pd.read_csv(data_path)
    print(f"   Rows: {len(df):,}  Columns: {len(df.columns)}")

    if TARGET_COL not in df.columns:
        print(f"❌ ERROR: Column '{TARGET_COL}' not found in data!")
        sys.exit(1)

    # ── Step 2: Import training pipeline ───────────────────────────────
    #   We dynamically import train_and_export.py to reuse the exact same
    #   feature engineering, threshold tuning, and training helpers.
    print("\n🔧 Importing training pipeline from train_and_export.py...")
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "trainer", os.path.join(MODEL_DIR, "train_and_export.py")
    )
    trainer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(trainer)

    # ── Step 3: Feature engineering ────────────────────────────────────
    print("\n⚙️  Running feature engineering (build_features)...")
    df = trainer.build_features(df)

    # Infer column types (same as original)
    cat_cols, num_cols = trainer.infer_column_types(df)

    # Clean columns (same as original main())
    for c in cat_cols:
        df[c] = df[c].astype("string").fillna("__MISSING__")
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(df[c].median())

    # Frequency encoding for high-cardinality IDs
    freq_maps = trainer.compute_freq_maps(df, trainer.FREQ_ENCODE_COLS)
    df = trainer.apply_freq_encoding(df, freq_maps)
    print(f"   Frequency-encoded: {[f'{c}_freq' for c in freq_maps]}")

    feature_cols = [c for c in df.columns if c not in [TARGET_COL, ID_COL]]
    X = df[feature_cols]
    y = df[TARGET_COL].astype(int)
    cat_indices = [i for i, c in enumerate(feature_cols) if c in cat_cols]

    print(f"   Features: {len(feature_cols)}  Cat indices: {len(cat_indices)}")
    print(f"\n   Class distribution:\n{y.value_counts().sort_index().to_string()}")

    # ── Step 4: Compute class weights ──────────────────────────────────
    class_weights = trainer.compute_class_weights(y, power=0.65)
    print(f"\n   Class weights: {dict((k, round(v,2)) for k,v in class_weights.items())}")

    # ── Step 5: Train/val split ────────────────────────────────────────
    print("\n📊 Splitting data 80/20...")
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"   Train: {len(X_train):,}  Val: {len(X_val):,}")

    from catboost import Pool

    train_pool = Pool(X_train, y_train, cat_features=cat_indices)
    val_pool = Pool(X_val, y_val, cat_features=cat_indices)

    # ── Step 6: Train 3 seeds, pick best (same as original) ───────────
    print("\n🚀 Training 3 seeds on 80% split...")
    params_val = dict(
        loss_function="MultiClass",
        eval_metric="TotalF1",
        class_weights=class_weights,
        depth=9,
        learning_rate=0.05,
        l2_leaf_reg=6.0,
        subsample=0.85,
        colsample_bylevel=0.85,
        iterations=2500,
        od_type="Iter",
        od_wait=150,
        allow_writing_files=False,
        verbose=200,
        bootstrap_type="Bernoulli",
    )

    seeds = [42, 7, 2025]
    best_val_f1, best_iter, best_val_proba, best_seed = -1.0, 0, None, 42

    for seed in seeds:
        p = dict(**params_val, random_seed=seed)
        m = trainer.train_catboost(train_pool, val_pool, p, use_best_model=True)
        proba = m.predict_proba(X_val)
        f1 = f1_score(y_val, np.argmax(proba, axis=1), average="macro")
        iters = m.tree_count_
        print(f"   seed={seed}: Val F1={f1:.5f}  best_iter={iters}")
        if f1 > best_val_f1:
            best_val_f1, best_iter, best_val_proba = f1, iters, proba
            best_seed = seed

    print(f"\n   Best seed={best_seed}  Val Macro F1={best_val_f1:.5f}  iters={best_iter}")
    params_val["random_seed"] = best_seed

    # ── Step 7: Tune thresholds ────────────────────────────────────────
    print("\n🎯 Tuning per-class thresholds...")
    threshold_multipliers, tuned_preds = trainer.tune_thresholds(
        best_val_proba, y_val.values, N_CLASSES
    )
    tuned_f1 = f1_score(y_val, tuned_preds, average="macro")
    print(f"   Tuned F1: {tuned_f1:.5f}  vs  Base F1: {best_val_f1:.5f}")

    if tuned_f1 >= best_val_f1:
        final_thresholds = threshold_multipliers
        new_f1 = tuned_f1
        print("   → Using tuned thresholds")
    else:
        final_thresholds = np.ones(N_CLASSES)
        new_f1 = best_val_f1
        print("   → Tuning hurt — reverting to uniform thresholds")

    # ── Step 8: Retrain on 100% data (same as original) ───────────────
    full_iter = int(best_iter * 1.30)
    print(f"\n🔄 Retraining on 100% data for {full_iter} iterations...")
    full_pool = Pool(X, y, cat_features=cat_indices)
    params_full = {k: v for k, v in params_val.items()
                   if k not in ("od_type", "od_wait", "iterations")}
    params_full["iterations"] = full_iter

    final_model = trainer.train_catboost(full_pool, None, params_full, use_best_model=False)

    # Build the artifact (same structure as original)
    new_artifact = {
        "model":              final_model,
        "thresholds":         final_thresholds.tolist(),
        "feature_cols_model": feature_cols,
        "cat_cols":           cat_cols,
        "num_cols":           num_cols,
        "freq_maps":          freq_maps,
    }

    # ── Step 9: Compare with current deployed model ────────────────────
    current_artifact = load_current_model()
    old_f1 = None

    if current_artifact:
        print("\n🔍 Comparing with current deployed model...")
        try:
            old_f1, _ = evaluate_model(current_artifact, X_val, y_val)
            print(f"   Current model F1: {old_f1:.4f}")
            print(f"   New model F1:     {new_f1:.4f}")
            improvement = new_f1 - old_f1
            print(f"   Improvement:      {improvement:+.4f}")
        except Exception as e:
            print(f"   ⚠ Could not evaluate current model: {e}")
            old_f1 = 0.0

    # ── Step 10: Decision — replace or keep ────────────────────────────
    should_replace = force or (old_f1 is None) or (new_f1 >= old_f1)

    if should_replace:
        print("\n✅ New model accepted. Saving...")
        if os.path.exists(MODEL_PATH):
            shutil.copy2(MODEL_PATH, BACKUP_PATH)
            print(f"   Backup saved to {BACKUP_PATH}")
        joblib.dump(new_artifact, MODEL_PATH, compress=3)
        size_mb = os.path.getsize(MODEL_PATH) / 1e6
        print(f"   New model saved to {MODEL_PATH}  ({size_mb:.1f} MB)")
    else:
        print("\n⚠ New model is WORSE. Keeping current model.")
        print("   Use --force to override this safety check.")

    # ── Step 11: Log results for audit trail ───────────────────────────
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "data_path": os.path.abspath(data_path),
        "data_rows": int(len(df)),
        "n_features": len(feature_cols),
        "best_seed": int(best_seed),
        "best_iter": int(best_iter),
        "full_iter": full_iter,
        "old_f1": round(float(old_f1), 4) if old_f1 is not None else None,
        "new_f1": round(float(new_f1), 4),
        "improvement": round(float(new_f1 - (old_f1 or 0)), 4),
        "replaced": should_replace,
        "forced": force,
    }

    log = []
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH) as f:
            log = json.load(f)
    log.append(log_entry)
    with open(LOG_PATH, "w") as f:
        json.dump(log, f, indent=2)

    print(f"\n📝 Training log saved to {LOG_PATH}")
    print("=" * 60)

    return should_replace


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Retrain the AssuranceAI CatBoost model with new data"
    )
    parser.add_argument(
        "--data", required=True,
        help="Path to training CSV (same format as train.csv)"
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Replace model even if new one scores lower"
    )
    args = parser.parse_args()

    retrain(args.data, force=args.force)

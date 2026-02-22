"""Model service — loads the trained model and runs predictions."""

import sys
import os
import importlib.util
import numpy as np
import pandas as pd

from backend.config import BUNDLE_NAMES, BUNDLE_META

# Path to the project root where solution.py and model.pkl live
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_solution_module():
    """Dynamically import solution.py without modifying it."""
    solution_path = os.path.join(PROJECT_ROOT, "solution.py")
    spec = importlib.util.spec_from_file_location("solution", solution_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Load solution module and model at startup
_solution = _load_solution_module()

# Ensure model.pkl is loaded from project root
_original_cwd = os.getcwd()
os.chdir(PROJECT_ROOT)
_model_artifact = _solution.load_model()
os.chdir(_original_cwd)


def predict_single(customer_data: dict) -> dict:
    """
    Run prediction for a single customer.

    Args:
        customer_data: dict with all feature fields

    Returns:
        dict with prediction results including bundle id, name, and confidence scores
    """
    # Create a unique user ID for the request
    user_id = customer_data.pop("User_ID", "USR_API_001")

    # Build a DataFrame from the input (solution.py expects this format)
    row = {"User_ID": user_id, **customer_data}
    df = pd.DataFrame([row])

    # Run through the solution pipeline
    df_processed = _solution.preprocess(df)

    # Get model components
    clf = _model_artifact["model"]
    thresholds = np.array(_model_artifact["thresholds"])
    freq_maps = _model_artifact.get("freq_maps", {})

    # Apply frequency encoding
    for col, fmap in freq_maps.items():
        if col in df_processed.columns:
            df_processed[f"{col}_freq"] = (
                df_processed[col].map(fmap).fillna(0).astype(np.float32)
            )

    # Get feature columns from solution
    feature_cols = _solution.FEATURE_COLS
    X = df_processed[feature_cols]

    # Get raw probabilities
    proba = clf.predict_proba(X)[0]

    # Apply threshold adjustment (same as solution.py predict)
    adjusted = proba * thresholds
    predicted_class = int(np.argmax(adjusted))

    # Build confidence scores dict
    confidence_scores = {}
    for i, p in enumerate(proba):
        confidence_scores[BUNDLE_NAMES.get(i, f"Class {i}")] = round(float(p) * 100, 2)

    return {
        "user_id": user_id,
        "predicted_bundle_id": predicted_class,
        "predicted_bundle_name": BUNDLE_NAMES.get(predicted_class, "Unknown"),
        "confidence_scores": confidence_scores,
        "bundle_meta": BUNDLE_META.get(predicted_class, {}),
        "raw_probabilities": {str(i): round(float(p), 6) for i, p in enumerate(proba)},
        "adjusted_probabilities": {
            str(i): round(float(p), 6)
            for i, p in enumerate(adjusted / adjusted.sum())
        },
    }


def predict_batch(customers: list[dict]) -> list[dict]:
    """Run predictions for multiple customers."""
    return [predict_single(c) for c in customers]


def get_model_info() -> dict:
    """Return metadata about the loaded model."""
    clf = _model_artifact["model"]
    return {
        "model_type": type(clf).__name__,
        "n_classes": len(BUNDLE_NAMES),
        "n_features": len(_solution.FEATURE_COLS),
        "bundle_names": BUNDLE_NAMES,
        "bundle_meta": BUNDLE_META,
        "thresholds": {
            BUNDLE_NAMES[i]: round(float(t), 4)
            for i, t in enumerate(_model_artifact["thresholds"])
        },
    }

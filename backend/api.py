"""FastAPI application — AssuranceAI Insurance Platform."""

import uuid
import json
import os
from contextlib import asynccontextmanager
from datetime import datetime

# Load .env file (for local development)
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from backend.config import BUNDLE_NAMES, BUNDLE_META, INPUT_FIELDS
from backend.schemas import CustomerInput
from backend.model_service import predict_single, predict_batch, get_model_info
from backend.database import init_db, get_connection
from backend.cache import cache_get, cache_set, cache_stats, cache_clear
from backend.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    require_admin,
    get_user_by_email,
    create_user,
)


# ── Pydantic models for auth ──────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: str
    full_name: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    print("✓ Model loaded and API ready")
    yield
    print("Shutting down…")


app = FastAPI(
    title="AssuranceAI — Smart Insurance Platform",
    description="Find the perfect insurance coverage bundle for every customer.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health ─────────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "healthy", "service": "AssuranceAI"}


@app.get("/api/cache/stats")
async def get_cache_stats():
    """Return cache hit/miss statistics (useful for monitoring)."""
    return cache_stats()


@app.post("/api/cache/clear")
async def clear_cache(admin: dict = Depends(require_admin)):
    """Clear the prediction cache (admin only)."""
    removed = cache_clear()
    return {"cleared": removed}


# ── Auth ───────────────────────────────────────────────────────────────────

@app.post("/api/auth/register")
async def register(req: RegisterRequest):
    existing = get_user_by_email(req.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = create_user(req.email, req.full_name, req.password)
    token = create_access_token({"sub": str(user["id"]), "role": user["role"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],
        },
    }


@app.post("/api/auth/login")
async def login(req: LoginRequest):
    user = get_user_by_email(req.email)
    if not user or not verify_password(req.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="Account has been disabled")
    token = create_access_token({"sub": str(user["id"]), "role": user["role"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],
        },
    }


@app.get("/api/auth/me")
async def get_me(user: dict = Depends(get_current_user)):
    return {
        "id": user["id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "role": user["role"],
    }


# ── Public info ────────────────────────────────────────────────────────────

@app.get("/api/bundles")
async def list_bundles():
    bundles = []
    for bundle_id, name in BUNDLE_NAMES.items():
        meta = BUNDLE_META.get(bundle_id, {})
        bundles.append({"id": bundle_id, "name": name, **meta})
    return {"bundles": bundles}


@app.get("/api/form-schema")
async def form_schema():
    return {"sections": INPUT_FIELDS}


# ── Prediction (auth required) ────────────────────────────────────────────

@app.post("/api/predict")
async def predict_endpoint(customer: CustomerInput, user: dict = Depends(get_current_user)):
    try:
        input_dict = customer.model_dump()

        # Check cache first (same input → instant response)
        cached = cache_get(input_dict)
        if cached:
            return cached

        data = input_dict.copy()
        data["User_ID"] = f"USR_{uuid.uuid4().hex[:8].upper()}"
        result = predict_single(data)

        # Store in cache for future identical requests
        cache_set(input_dict, result)

        # Save to DB
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO predictions (user_id, input_data, predicted_bundle_id,
                predicted_bundle_name, confidence_scores)
               VALUES (%s, %s, %s, %s, %s)""",
            (
                user["id"],
                json.dumps(customer.model_dump()),
                result["predicted_bundle_id"],
                result["predicted_bundle_name"],
                json.dumps(result["confidence_scores"]),
            ),
        )
        conn.commit()
        cur.close()
        conn.close()

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── User prediction history ───────────────────────────────────────────────

@app.get("/api/predictions/history")
async def prediction_history(user: dict = Depends(get_current_user)):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT id, predicted_bundle_id, predicted_bundle_name,
                  confidence_scores, created_at
           FROM predictions WHERE user_id = %s
           ORDER BY created_at DESC LIMIT 50""",
        (user["id"],),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {"history": [dict(r) for r in rows]}


# ── Admin endpoints ────────────────────────────────────────────────────────

@app.get("/api/admin/stats")
async def admin_stats(admin: dict = Depends(require_admin)):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as count FROM users")
    total_users = cur.fetchone()["count"]
    cur.execute("SELECT COUNT(*) as count FROM users WHERE role = 'admin'")
    total_admins = cur.fetchone()["count"]
    cur.execute("SELECT COUNT(*) as count FROM predictions")
    total_predictions = cur.fetchone()["count"]
    cur.execute(
        """SELECT predicted_bundle_name, COUNT(*) as count
           FROM predictions GROUP BY predicted_bundle_name
           ORDER BY count DESC"""
    )
    bundle_dist = [dict(r) for r in cur.fetchall()]
    cur.execute(
        """SELECT DATE(created_at) as date, COUNT(*) as count
           FROM predictions
           WHERE created_at >= NOW() - INTERVAL '30 days'
           GROUP BY DATE(created_at) ORDER BY date"""
    )
    daily_preds = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return {
        "total_users": total_users,
        "total_admins": total_admins,
        "total_predictions": total_predictions,
        "bundle_distribution": bundle_dist,
        "daily_predictions": daily_preds,
    }


@app.get("/api/admin/users")
async def admin_list_users(admin: dict = Depends(require_admin)):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT u.id, u.email, u.full_name, u.role, u.is_active, u.created_at,
                  COUNT(p.id) as prediction_count
           FROM users u LEFT JOIN predictions p ON p.user_id = u.id
           GROUP BY u.id ORDER BY u.created_at DESC"""
    )
    users = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return {"users": users}


@app.get("/api/admin/predictions")
async def admin_list_predictions(admin: dict = Depends(require_admin)):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT p.id, p.predicted_bundle_id, p.predicted_bundle_name,
                  p.confidence_scores, p.created_at,
                  u.email, u.full_name
           FROM predictions p JOIN users u ON p.user_id = u.id
           ORDER BY p.created_at DESC LIMIT 100"""
    )
    preds = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return {"predictions": preds}


@app.patch("/api/admin/users/{user_id}/toggle")
async def admin_toggle_user(user_id: int, admin: dict = Depends(require_admin)):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET is_active = NOT is_active WHERE id = %s RETURNING id, is_active",
        (user_id,),
    )
    result = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": result["id"], "is_active": result["is_active"]}

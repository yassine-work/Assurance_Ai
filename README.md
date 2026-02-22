# AssuranceAI — Insurance Coverage Recommendation System

A full-stack web application that recommends insurance coverage bundles using a trained CatBoost ML model.

## Project Structure

```
Assurance_Ai/
├── model/                     # ML model files
│   ├── solution.py            # Inference pipeline (preprocess, predict)
│   ├── train_and_export.py    # Training pipeline (feature engineering, CatBoost)
│   └── model.pkl              # Trained model artifact (gitignored)
├── backend/                   # FastAPI REST API
│   ├── api.py                 # Main API — all endpoints
│   ├── auth.py                # JWT authentication + bcrypt passwords
│   ├── cache.py               # In-memory prediction cache (TTL, LRU)
│   ├── config.py              # Bundle definitions + form field labels
│   ├── database.py            # PostgreSQL connection (Neon)
│   ├── model_service.py       # Model loading + prediction service
│   └── schemas.py             # Pydantic request/response models
├── frontend/                  # React + Tailwind CSS UI
│   └── src/
│       ├── pages/             # Dashboard, Predict, Bundles, Login, Register, Admin, History
│       ├── components/        # Navbar, PredictionResult
│       └── services/          # Axios API client with auth interceptor
├── scripts/                   # MLOps scripts
│   └── retrain.py             # Safe model retraining pipeline
├── tests/                     # Automated test suite
│   └── test_api.py            # 14 pytest tests (auth, predict, cache, admin)
├── .github/workflows/         # CI/CD pipelines
│   ├── ci.yml                 # Auto test + build on push
│   └── retrain.yml            # Scheduled/manual model retraining
├── requirements.txt           # Python dependencies
└── .env                       # Secrets — DATABASE_URL, JWT_SECRET_KEY (gitignored)
```

## Quick Start

### 1. Backend

```bash
# Create and activate virtual environment
python -m venv env
source env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your secrets
echo 'DATABASE_URL=your_postgres_connection_string' > .env
echo 'JWT_SECRET_KEY=your_secret_key' >> .env

# Start the API server
python -m uvicorn backend.api:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

### 3. Open in browser

Go to **http://localhost:5173**

## Features

### Core Application
- **Insurance Bundle Recommendation** — fill a form, get a personalized coverage recommendation
- **10 Coverage Bundles** — from Basic to Platinum, each with confidence scores
- **User Authentication** — JWT-based login/register with bcrypt password hashing
- **Admin Dashboard** — user management, prediction history, system stats
- **Prediction History** — users can view their past recommendations

### MLOps (Bonus)
- **CI/CD Pipeline** — GitHub Actions runs 14 tests + frontend build on every push
- **In-Memory Cache** — SHA-256 key hashing, 1hr TTL, 1000 entry max, LRU eviction
- **Retraining Pipeline** — safe model replacement with F1 comparison + backup + audit log
- **Scheduled Retraining** — GitHub Actions workflow (weekly or manual trigger)
- **Environment Variables** — secrets in `.env` (gitignored) + GitHub Secrets in CI

## API Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/health` | GET | — | Health check |
| `/api/bundles` | GET | — | List all 10 coverage bundles |
| `/api/form-schema` | GET | — | Form field definitions with labels |
| `/api/auth/register` | POST | — | Register new user |
| `/api/auth/login` | POST | — | Login (returns JWT token) |
| `/api/auth/me` | GET | User | Current user info |
| `/api/predict` | POST | User | Get coverage recommendation |
| `/api/predictions/history` | GET | User | User's past predictions |
| `/api/cache/stats` | GET | — | Cache hit/miss statistics |
| `/api/cache/clear` | POST | Admin | Clear prediction cache |
| `/api/admin/stats` | GET | Admin | System statistics |
| `/api/admin/users` | GET | Admin | All users |
| `/api/admin/predictions` | GET | Admin | All predictions |

## Running Tests

```bash
source env/bin/activate
python -m pytest tests/ -v
```

## Retraining the Model

```bash
python scripts/retrain.py --data path/to/new_train.csv
```

## Tech Stack

- **Backend**: FastAPI, Uvicorn, Pydantic v2, PostgreSQL (Neon)
- **Frontend**: React, Vite, Tailwind CSS, Axios
- **ML**: CatBoost, scikit-learn, pandas, numpy
- **Auth**: JWT (python-jose), bcrypt
- **MLOps**: GitHub Actions, pytest, in-memory cache

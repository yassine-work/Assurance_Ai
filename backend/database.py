"""Database connection and table initialization using PostgreSQL (Neon)."""

import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Read from environment variable (set via .env locally, GitHub Secrets in CI)
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_daV3rhgRAv1f"
    "@ep-morning-cell-ai1952ef-pooler.c-4.us-east-1.aws.neon.tech"
    "/neondb?sslmode=require",
)


def get_connection():
    """Return a new database connection."""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            full_name VARCHAR(255) NOT NULL,
            hashed_password TEXT NOT NULL,
            role VARCHAR(20) DEFAULT 'user',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            input_data JSONB NOT NULL,
            predicted_bundle_id INTEGER NOT NULL,
            predicted_bundle_name VARCHAR(100) NOT NULL,
            confidence_scores JSONB,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)
    conn.commit()

    # Seed admin if not exists
    cur.execute("SELECT id FROM users WHERE email = 'admin@assuranceai.com'")
    if not cur.fetchone():
        from backend.auth import hash_password
        cur.execute(
            """INSERT INTO users (email, full_name, hashed_password, role)
               VALUES (%s, %s, %s, %s)""",
            ("admin@assuranceai.com", "Admin", hash_password("admin123"), "admin"),
        )
        conn.commit()
        print("✓ Seeded admin user: admin@assuranceai.com / admin123")

    cur.close()
    conn.close()
    print("✓ Database tables ready")

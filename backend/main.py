# backend/main.py

from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from passlib.hash import bcrypt
import requests
import urllib3

# Disable SSL warnings (college network issue fix)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ------------------------
# SUPABASE CONFIG
# ------------------------

SUPABASE_URL = "https://hzhmdysnpsddquiiubjq.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh6aG1keXNucHNkZHF1aWl1YmpxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MzUzODA3OCwiZXhwIjoyMDc5MTE0MDc4fQ.nLr78yPtkgfPoHOemETNNkaokFkqQ4UBzYemoaRzrNg"

REST_URL = f"{SUPABASE_URL}/rest/v1"

HEADERS = {
    "apikey": SUPABASE_SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# ------------------------
# FASTAPI INIT
# ------------------------

app = FastAPI(title="BodyOS Backend")

# ------------------------
# MODELS
# ------------------------

class RegisterModel(BaseModel):
    username: str
    email: EmailStr
    password: str
    gender: str
    dob: str   # YYYY-MM-DD


class ProfileModel(BaseModel):
    user_id: int
    height_cm: float
    weight_kg: float
    bmi: float
    activity_level: str
    goal: str

# ------------------------
# SUPABASE HELPERS
# ------------------------

def supabase_insert(table: str, payload: dict):
    """Insert row into Supabase table."""
    url = f"{REST_URL}/{table}"

    r = requests.post(
        url,
        json=payload,
        headers=HEADERS,
        verify=False  # SSL BYPASS
    )

    if not r.ok:
        raise HTTPException(500, f"Supabase Insert Error: {r.text}")

    return r.json()[0]  # Supabase returns list


def supabase_get_one(table: str, filters: dict):
    """Get 1 row from Supabase table."""
    query = "&".join([f"{k}=eq.{v}" for k, v in filters.items()])
    url = f"{REST_URL}/{table}?{query}&limit=1"

    r = requests.get(
        url,
        headers=HEADERS,
        verify=False  # SSL BYPASS
    )

    if not r.ok:
        raise HTTPException(500, f"Supabase Select Error: {r.text}")

    rows = r.json()
    return rows[0] if rows else None

# ------------------------
# REGISTER ENDPOINT
# ------------------------

@app.post("/register")
def register(data: RegisterModel):

    # Email check
    if supabase_get_one("users", {"email": data.email}):
        raise HTTPException(400, "Email already registered")

    # Username check
    if supabase_get_one("users", {"username": data.username}):
        raise HTTPException(400, "Username already taken")

    # Fix: bcrypt max length = 72 bytes
    hashed_pw = bcrypt.hash(data.password[:72])

    payload = {
        "username": data.username,
        "email": data.email,
        "password": hashed_pw,
        "gender": data.gender,
        "dob": data.dob,
        "created_at": datetime.utcnow().isoformat()
    }

    row = supabase_insert("users", payload)

    return {"status": "ok", "user": row}

# ------------------------
# PROFILE ENDPOINT
# ------------------------

@app.post("/profile")
def create_profile(data: ProfileModel):

    user = supabase_get_one("users", {"user_id": data.user_id})
    if not user:
        raise HTTPException(404, "User not found")

    # Ensure user has no previous profile
    if supabase_get_one("user_profile", {"user_id": data.user_id}):
        raise HTTPException(400, "Profile already exists")

    payload = {
        "user_id": data.user_id,
        "height_cm": data.height_cm,
        "weight_kg": data.weight_kg,
        "bmi": data.bmi,
        "activity_level": data.activity_level,
        "goal": data.goal,
    }

    row = supabase_insert("user_profile", payload)

    return {"status": 'ok', "profile": row}


@app.post("/login")
def login(data: LoginModel):
    user = supabase_get_one("users", {"email": data.email})
    if not user:
        raise HTTPException(400, "Email not found")

    if not bcrypt.verify(data.password, user["password"]):
        raise HTTPException(400, "Incorrect password")

    return {"status": "ok", "user": user}

class LoginModel(BaseModel):
    email: EmailStr
    password: str

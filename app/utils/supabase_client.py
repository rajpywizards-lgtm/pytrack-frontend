# app/utils/supabase_client.py
"""
supabase_client.py
------------------
Optional lightweight Supabase client for read-only or helper calls from frontend.
For secure operations (uploading screenshots, inserting DB rows),
always use the FastAPI backend endpoints instead.
"""

import os
from supabase import create_client, Client

# Load credentials (safe for frontend if you are only reading public data)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise RuntimeError(
        "❌ Supabase credentials missing. Set SUPABASE_URL and SUPABASE_ANON_KEY in environment or .env file."
    )

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    print("✅ Supabase frontend client initialized.")
except Exception as e:
    raise RuntimeError(f"⚠️ Failed to initialize Supabase client: {e}")

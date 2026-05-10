from supabase import create_client
from app.core.config import ( SUPABASE_URL, SUPABASE_KEY )

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("DATABASE_URL and SUPABASE_KEY must be set")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
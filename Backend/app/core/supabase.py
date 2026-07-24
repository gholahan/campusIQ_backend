from supabase import create_client
from app.core.config import ( SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_ROLE_KEY )

if not SUPABASE_URL or not SUPABASE_KEY or not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError("All database credentials must be set")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

supabase_admin = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
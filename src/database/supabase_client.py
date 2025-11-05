from supabase import create_client
from src.core.config import settings

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

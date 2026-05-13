import os

from dotenv import load_dotenv

from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE = os.getenv(
    "SUPABASE_SERVICE_ROLE"
)

supabase = None

if (
    SUPABASE_URL
    and SUPABASE_SERVICE_ROLE
):
    supabase = create_client(
        SUPABASE_URL,
        SUPABASE_SERVICE_ROLE
    )

def save_invoice(data):

    if not supabase:
        return {
            "error": "Supabase not configured"
        }

    response = supabase.table(
        "invoices"
    ).insert(data).execute()

    return response
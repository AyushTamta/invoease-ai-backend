import os

from dotenv import load_dotenv

from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE")
)

def save_invoice(data):

    response = supabase.table(
        "invoices"
    ).insert(data).execute()

    return response
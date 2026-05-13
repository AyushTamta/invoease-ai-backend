from fastapi import FastAPI, UploadFile, File

import shutil
import json

from services.gemini_service import (
    extract_invoice_data,
)

from services.supabase_service import (
    save_invoice,
)

app = FastAPI()

@app.get("/")
def home():
    return {
        "message": "InvoEase AI Backend Running"
    }

@app.post("/scan-invoice")
async def scan_invoice(
    file: UploadFile = File(...)
):

    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = extract_invoice_data(file_path)

    cleaned = (
        result
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    parsed = json.loads(cleaned)

    save_invoice(parsed)

    return {
        "success": True,
        "data": parsed,
    }
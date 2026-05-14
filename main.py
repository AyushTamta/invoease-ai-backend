from fastapi import FastAPI, UploadFile, File

import requests
import re

app = FastAPI()

OCR_API_KEY = "K82584264988957"

@app.get("/")

@app.post("/scan-invoice")
async def scan_invoice(
    file: UploadFile = File(...)
):

    image_bytes = await file.read()

    response = requests.post(
        "https://api.ocr.space/parse/image",
        files={
            "file": (
                file.filename,
                image_bytes,
                file.content_type,
            )
        },
        data={
            "apikey": OCR_API_KEY,
            "language": "eng",
        },
    )

    result = response.json()

    parsed_text = result[
        "ParsedResults"
    ][0]["ParsedText"]

    lines = [
        line.strip()
        for line in parsed_text.split("\n")
        if line.strip()
    ]

    store_name = (
        lines[0]
        if len(lines) > 0
        else "Unknown"
    )

    total_amount = "0"

    for line in lines:

        if "$" in line:
            total_amount = line

    invoice_date = "Unknown"

    for line in lines:

        if "/" in line:
            invoice_date = line
            break

    category = detect_category(
        parsed_text
    )

    items = extract_items(lines)

    return {
        "store_name": store_name,
        "total_amount": total_amount,
        "invoice_date": invoice_date,
        "category": category,
        "items": items,
        "raw_text": parsed_text,
    }
from fastapi import (
    FastAPI,
    UploadFile,
    File
)

import requests
import re

app = FastAPI()

OCR_API_KEY = "K82584264988957"


@app.get("/")
def home():

    return {
        "message":
        "InvoEase AI Backend Running"
    }


def detect_category(text):

    text = text.lower()

    if any(word in text for word in [
        "uber",
        "ola",
        "metro",
        "flight",
    ]):

        return "Travel"

    if any(word in text for word in [
        "pizza",
        "burger",
        "cafe",
        "restaurant",
        "starbucks",
    ]):

        return "Food"

    if any(word in text for word in [
        "dmart",
        "walmart",
        "store",
        "mart",
    ]):

        return "Shopping"

    return "General"


def extract_items(lines):

    items = []

    for line in lines:

        match = re.search(
            r"([A-Za-z ].*?)\s+(\d+\.\d{2})",
            line,
        )

        if match:

            items.append({
                "name":
                match.group(1),

                "price":
                match.group(2),
            })

    return items


@app.post("/scan-invoice")
async def scan_invoice(
    file: UploadFile = File(...)
):

    try:

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
                "apikey":
                OCR_API_KEY,

                "language":
                "eng"
            }
        )

        result = response.json()

        print(result)

        if (
            "ParsedResults"
            not in result
        ):

            return {
                "error":
                "OCR API failed",

                "full_response":
                result
            }

        parsed_text = result[
            "ParsedResults"
        ][0]["ParsedText"]

        lines = [
            line.strip()
            for line in parsed_text.split(
                "\n"
            )
            if line.strip()
        ]

        store_name = (
            lines[0]
            if len(lines) > 0
            else "Unknown Store"
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

        items = extract_items(
            lines
        )

        return {
            "store_name":
            store_name,

            "total_amount":
            total_amount,

            "invoice_date":
            invoice_date,

            "category":
            category,

            "items":
            items,

            "raw_text":
            parsed_text
        }

    except Exception as e:

        print(str(e))

        return {
            "error":
            "Backend crashed",

            "details":
            str(e)
        }
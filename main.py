from fastapi import FastAPI, UploadFile, File
import requests
import os
import json

from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

OCR_API_KEY = os.getenv(
    "OCR_API_KEY"
)

@app.get("/")
def home():

    return {
        "message":
        "InvoEase OCR Backend Running"
    }

@app.post("/scan-invoice")
async def scan_invoice(
    file: UploadFile = File(...)
):

    try:

        image_bytes = await file.read()

        response = requests.post(
            "https://api.ocr.space/parse/image",
            files={
                "filename": (
                    file.filename,
                    image_bytes,
                    file.content_type
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

        parsed_text = result[
            "ParsedResults"
        ][0]["ParsedText"]

        lines = parsed_text.split("\n")

        store_name = (
            lines[0]
            if len(lines) > 0
            else "Unknown Store"
        )

        return {
            "store_name":
            store_name,

            "raw_text":
            parsed_text
        }

    except Exception as e:

        return {
            "error":
            "OCR parsing failed",

            "details":
            str(e)
        }
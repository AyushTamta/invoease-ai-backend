from fastapi import FastAPI, UploadFile, File
import requests

app = FastAPI()

OCR_API_KEY = "K82584264988957"

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
                "file": (
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

        print(result)

        if "ParsedResults" not in result:

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
            for line in parsed_text.split("\n")
            if line.strip()
        ]

        store_name = (
            lines[1]
            if len(lines) > 1
            else "Unknown Store"
        )

        total_amount = "Not Found"

        for line in lines:

            if "$" in line:

                total_amount = line
                break

        invoice_date = "Not Found"

        for line in lines:

            if "/" in line:

                invoice_date = line
                break

        return {
            "store_name":
            store_name,

            "invoice_date":
            invoice_date,

            "total_amount":
            total_amount,

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
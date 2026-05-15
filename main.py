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
        "restaurant",
        "cafe",
        "coffee",
    ]):

        return "Food"

    if any(word in text for word in [
        "store",
        "mart",
        "mall",
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


def generate_ai_summary(
    store_name,
    category,
    total_amount,
):

    return (
        f"This invoice appears to be a "
        f"{category} expense from "
        f"{store_name} totaling "
        f"{total_amount}."
    )


def answer_invoice_question(
    invoice,
    question,
):

    q = question.lower()

    if "items" in q:

        names = [
            item["name"]
            for item in invoice["items"]
        ]

        return (
            "Purchased items include: "
            + ", ".join(names)
        )

    if "category" in q:

        return (
            f"This invoice belongs to "
            f"{invoice['category']}."
        )

    if "payment" in q:

        return (
            f"Payment method appears "
            f"to be "
            f"{invoice['payment_method']}."
        )

    if "business" in q:

        return (
            "This may qualify as "
            "business expense depending "
            "on how it was used."
        )

    return (
        "I analyzed the invoice "
        "but could not fully "
        "understand the question."
    )


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

        ai_summary = (
            generate_ai_summary(
                store_name,
                category,
                total_amount,
            )
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

            "payment_method":
            "Card",

            "tax":
            "GST Included",

            "items":
            items,

            "ai_summary":
            ai_summary,
        }

    except Exception as e:

        return {
            "error":
            str(e)
        }


@app.post("/ask-ai")
async def ask_ai(
    payload: dict
):

    try:

        invoice = payload["invoice"]

        question = payload["question"]

        answer = (
            answer_invoice_question(
                invoice,
                question,
            )
        )

        return {
            "answer":
            answer
        }

    except Exception as e:

        return {
            "error":
            str(e)
        }
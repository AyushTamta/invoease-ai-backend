from fastapi import (
    FastAPI,
    UploadFile,
    File
)

import requests
import re

app = FastAPI()

OCR_API_KEY = K82584264988957


@app.get("/")
def home():

    return {
        "message":
        "InvoEase AI Backend Running"
    }


# -------------------------
# CATEGORY DETECTION
# -------------------------

def detect_category(text):

    text = text.lower()

    if any(word in text for word in [
        "uber",
        "ola",
        "metro",
        "flight",
        "airport",
    ]):

        return "Travel"

    if any(word in text for word in [
        "pizza",
        "burger",
        "restaurant",
        "cafe",
        "starbucks",
        "coffee",
        "food",
    ]):

        return "Food"

    if any(word in text for word in [
        "dmart",
        "walmart",
        "mart",
        "store",
        "mall",
    ]):

        return "Shopping"

    if any(word in text for word in [
        "medical",
        "pharmacy",
        "hospital",
        "medicine",
    ]):

        return "Healthcare"

    return "General"


# -------------------------
# ITEM EXTRACTION
# -------------------------

def extract_items(lines):

    items = []

    for line in lines:

        match = re.search(
            r"([A-Za-z ].*?)\s+(\d+\.\d{2})",
            line,
        )

        if match:

            item_name = (
                match.group(1).strip()
            )

            item_price = (
                match.group(2)
            )

            items.append({
                "name":
                item_name,

                "price":
                item_price,
            })

    return items


# -------------------------
# TAX EXTRACTION
# -------------------------

def extract_tax(lines):

    for line in lines:

        lower = line.lower()

        if (
            "tax" in lower
            or "gst" in lower
            or "vat" in lower
        ):

            return line

    return "Not Found"


# -------------------------
# PAYMENT METHOD
# -------------------------

def extract_payment_method(text):

    text = text.lower()

    if "visa" in text:
        return "Visa Card"

    if "mastercard" in text:
        return "Mastercard"

    if "upi" in text:
        return "UPI"

    if "cash" in text:
        return "Cash"

    if "credit" in text:
        return "Credit Card"

    if "debit" in text:
        return "Debit Card"

    return "Unknown"


# -------------------------
# AI SUMMARY
# -------------------------

def generate_ai_summary(
    store_name,
    category,
    total_amount,
):

    return (
        f"This invoice appears to be a "
        f"{category} expense from "
        f"{store_name} totaling "
        f"{total_amount}. "
        f"The purchase has been "
        f"automatically analyzed and "
        f"categorized using AI."
    )


# -------------------------
# ASK AI ENGINE
# -------------------------

def answer_invoice_question(
    invoice,
    question,
):

    q = question.lower()

    if "what items" in q:

        item_names = [
            item["name"]
            for item in invoice["items"]
        ]

        return (
            "Purchased items include: "
            + ", ".join(item_names)
        )

    if "tax" in q:

        return (
            f"The detected tax is "
            f"{invoice['tax']}."
        )

    if "category" in q:

        return (
            f"This invoice belongs to "
            f"the {invoice['category']} "
            f"category."
        )

    if "payment" in q:

        return (
            f"The payment method appears "
            f"to be "
            f"{invoice['payment_method']}."
        )

    if "date" in q:

        return (
            f"The invoice date is "
            f"{invoice['invoice_date']}."
        )

    if "business" in q:

        if (
            invoice["category"]
            in [
                "Travel",
                "Food",
            ]
        ):

            return (
                "This may qualify as "
                "a business expense "
                "depending on usage."
            )

        return (
            "This appears more like "
            "a personal expense."
        )

    return (
        "I analyzed the invoice, but "
        "could not fully understand "
        "the question."
    )


# -------------------------
# SCAN INVOICE
# -------------------------

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

        tax = extract_tax(
            lines
        )

        payment_method = (
            extract_payment_method(
                parsed_text
            )
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
            payment_method,

            "tax":
            tax,

            "items":
            items,

            "ai_summary":
            ai_summary,

            "raw_text":
            parsed_text,
        }

    except Exception as e:

        print(str(e))

        return {
            "error":
            "Backend crashed",

            "details":
            str(e)
        }


# -------------------------
# ASK AI ROUTE
# -------------------------

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
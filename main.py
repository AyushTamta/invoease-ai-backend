from fastapi import FastAPI
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(
    api_key=os.getenv(AIzaSyBkpXQ76SxtK6rfIAQDvmchJw7F39L_jSU)
)

app = FastAPI()

@app.get("/")
def home():
    return {
        "message": "Gemini backend working"
    }
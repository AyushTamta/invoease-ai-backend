from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "InvoEase AI Backend Running"}
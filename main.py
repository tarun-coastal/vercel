import os
import requests
import google.generativeai as genai

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

app = FastAPI(title="AI News Digest API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# ---------------- HOME ----------------
@app.get("/")
async def home():
    return FileResponse("index.html")


# ---------------- HEALTH ----------------
@app.get("/api/health")
def health():
    return {
        "news_api": "ok" if NEWS_API_KEY else "missing",
        "gemini_api": "ok" if GEMINI_API_KEY else "missing",
    }


# ---------------- NEWS ----------------
@app.get("/api/news")
def fetch_news(topic: str = "technology", count: int = Query(5, ge=1, le=20)):

    url = "https://newsapi.org/v2/everything"

    params = {
        "q": topic,
        "pageSize": count,
        "language": "en",
        "sortBy": "publishedAt",
        "apiKey": NEWS_API_KEY,
    }

    try:
        r = requests.get(url, params=params)
        data = r.json()

        return data

    except Exception as e:
        return {"error": str(e)}


# ---------------- SUMMARIZE ----------------
@app.get("/api/summarize")
def summarize_news(title: str, description: str = ""):

    if not GEMINI_API_KEY:
        return {"error": "Gemini API key missing"}

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
Summarize in 2 short sentences:

Title: {title}
Description: {description}
"""

    try:
        response = model.generate_content(prompt)
        return {"summary": response.text}

    except Exception as e:
        return {"error": str(e)}

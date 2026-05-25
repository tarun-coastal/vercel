import os
import requests
import google.generativeai as genai

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv

# =========================================
# LOAD ENV
# =========================================
load_dotenv()

# =========================================
# FASTAPI APP
# =========================================
app = FastAPI(title="AI News Digest API")

# =========================================
# CORS
# =========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================
# API KEYS
# =========================================
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# =========================================
# GEMINI CONFIG
# =========================================
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

# =========================================
# HOME
# =========================================


@app.get("/")
async def home():
    return FileResponse("index.html")
# =========================================
# HEALTH CHECK
# =========================================
@app.get("/api/health")
def health():

    return {
        "news_api": "ok" if NEWS_API_KEY else "missing",
        "gemini_api": "ok" if GEMINI_API_KEY else "missing",
        "model": "gemini-2.5-flash"
    }


# =========================================
# FETCH NEWS
# =========================================
@app.get("/api/news")
def fetch_news(
    topic: str = "technology",
    count: int = Query(5, ge=1, le=20)
):

    url = "https://newsapi.org/v2/everything"

    params = {
        "q": topic,
        "pageSize": count,
        "language": "en",
        "sortBy": "publishedAt",
        "apiKey": NEWS_API_KEY,
    }

    try:

        response = requests.get(
            url,
            params=params
        )

        data = response.json()

        if data.get("status") != "ok":

            return {
                "error": data.get("message"),
                "articles": []
            }

        articles = []

        for article in data.get("articles", []):

            title = article.get("title") or "No title"

            if "[Removed]" in title:
                continue

            articles.append({
                "title": title,
                "description": article.get("description") or "",
                "source": (
                    article.get("source") or {}
                ).get("name") or "Unknown",
                "url": article.get("url") or "",
                "publishedAt": article.get("publishedAt") or "",
                "urlToImage": article.get("urlToImage") or "",
            })

        return {
            "articles": articles,
            "total": len(articles)
        }

    except Exception as e:

        return {
            "error": str(e),
            "articles": []
        }


# =========================================
# AI SUMMARY
# =========================================
@app.get("/api/summarize")
def summarize_news(
    title: str,
    description: str = ""
):

    try:

        prompt = f"""
Summarize this news in 2 short sentences.

Be direct and easy to understand.

Title:
{title}

Description:
{description or "Not available"}

Summary:
"""

        response = model.generate_content(
            prompt
        )

        return {
            "summary": response.text
        }

    except Exception as e:

        return {
            "error": str(e)
        }


# =========================================
# START SERVER
# =========================================
# Run:
# uvicorn app:app --reload
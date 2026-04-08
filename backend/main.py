import os
import json
import httpx
from google import genai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from bs4 import BeautifulSoup

app = FastAPI(title="Article-to-Video Generator", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

if not GEMINI_API_KEY:
    print("⚠️ GEMINI_API_KEY not set")

# Initialize new Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)


class ArticleRequest(BaseModel):
    url: str
    style: Optional[str] = "documentary"
    duration: Optional[int] = 60


async def fetch_article_content(url: str) -> dict:
    headers = {"User-Agent": "Mozilla/5.0"}

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client_http:
        try:
            response = await client_http.get(url, headers=headers)
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {str(e)}")

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    title = ""
    if soup.find("h1"):
        title = soup.find("h1").get_text(strip=True)
    elif soup.find("title"):
        title = soup.find("title").get_text(strip=True)

    main_content = ""
    for selector in ["article", "main", ".content", ".post-content", ".article-body"]:
        element = soup.select_one(selector)
        if element:
            main_content = element.get_text(separator=" ", strip=True)
            break

    if not main_content:
        main_content = soup.get_text(separator=" ", strip=True)

    main_content = main_content[:4000]

    return {"title": title, "content": main_content, "url": url}


def clean_json_output(raw: str) -> str:
    raw = raw.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    return raw.strip()


def generate_video_script_with_gemini(article: dict, style: str, duration: int) -> dict:
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured.")

    style_descriptions = {
        "documentary": "cinematic documentary style with serious tone, b-roll suggestions, and authoritative narration",
        "explainer": "engaging explainer video style with clear visuals and friendly tone",
        "social_media": "fast-paced viral social media style (TikTok/Reels)",
    }

    style_desc = style_descriptions.get(style, style_descriptions["documentary"])
    words_per_second = 2.5
    target_words = int(duration * words_per_second)

    prompt = f"""
You are an expert video script writer.

Analyze the article and generate a video script.

Respond ONLY with valid JSON. No markdown, no explanations.

Article Title: {article['title']}
Article URL: {article['url']}
Content:
{article['content']}

Create a {style_desc} video (~{duration}s, ~{target_words} words narration).

JSON format:
{{
  "title": "",
  "summary": "",
  "keywords": [],
  "estimated_duration": {duration},
  "style": "{style}",
  "narration": "",
  "scenes": []
}}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )

        if not response.text:
            raise ValueError("Empty response from Gemini")

        cleaned = clean_json_output(response.text)

        result = json.loads(cleaned)
        return result

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid JSON from Gemini:\n{cleaned[:500]}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")


@app.get("/")
async def root():
    return {"message": "Article-to-Video Generator API", "version": "2.0.0"}


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "gemini_configured": bool(GEMINI_API_KEY)
    }


@app.post("/generate")
async def generate_video(request: ArticleRequest):

    article = await fetch_article_content(request.url)

    if not article["content"] or len(article["content"]) < 100:
        raise HTTPException(
            status_code=400,
            detail="Could not extract meaningful content from the URL."
        )

    script = generate_video_script_with_gemini(
        article=article,
        style=request.style,
        duration=request.duration
    )

    return {
        "success": True,
        "article": {
            "title": article["title"],
            "url": article["url"],
            "content_length": len(article["content"])
        },
        "script": script
    }


@app.get("/styles")
async def get_styles():
    return {
        "styles": [
            {"id": "documentary", "name": "Documentary"},
            {"id": "explainer", "name": "Explainer"},
            {"id": "social_media", "name": "Social Media"},
        ]
    }

# 🎬 ArticleVid — AI Video Script Generator

Turn any article URL into a fully produced video script using **Google Gemini AI** — with scenes, narration, b-roll suggestions, and text overlays.

> **Note:** Google NotebookLM does not have a public API. This app uses the **Google Gemini API** (the same AI model family powering NotebookLM) to deliver equivalent article-to-video generation capabilities.

---

## ✨ Features

- 🔗 **Paste any article URL** — the app fetches and parses the content automatically
- 🎬 **3 video styles** — Documentary, Explainer, Social Media (TikTok/Reels)
- ⏱ **Custom duration** — generate scripts from 30 seconds to 3 minutes
- 🎙 **Full narration script** — written for text-to-speech, ready to record
- 🎞 **Scene-by-scene breakdown** — with timestamps, visuals, b-roll, and overlays
- 📤 **Export** — download as JSON or Markdown, or copy narration to clipboard
- 🐳 **Fully Dockerized** — one command to run

---

## 🚀 Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- A **Google Gemini API key** — get one free at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

### 1. Clone the repository

```bash
git clone https://github.com/suman99pro/notebooklm-video-app.git
cd notebooklm-video-app
```

### 2. Configure your API key

```bash
cp .env.example .env
# Edit .env and paste your Gemini API key
```

Your `.env` file should look like:
```
GEMINI_API_KEY=AIza...your_key_here
```

### 3. Start the app

```bash
docker compose up --build
```

### 4. Open the app

Visit **[http://localhost:3000](http://localhost:3000)** in your browser.

---

## 🏗 Architecture

```
articlevid/
├── docker-compose.yml       # Orchestrates both services
├── .env.example             # Environment variable template
├── .gitignore
│
├── backend/                 # FastAPI Python backend
│   ├── main.py              # API endpoints + Gemini integration
│   ├── requirements.txt
│   └── Dockerfile
│
└── frontend/                # Static HTML/CSS/JS served via Nginx
    ├── index.html           # Single-page app
    ├── nginx.conf           # Reverse proxy to backend
    └── Dockerfile
```

**Data flow:**
```
Browser → Nginx (port 3000)
           ├── /          → serves index.html
           └── /api/*     → proxy → FastAPI backend (port 8000)
                                      ├── fetches article (httpx)
                                      ├── parses HTML (BeautifulSoup)
                                      └── calls Gemini API → returns script
```

---

## 🔌 API Reference

The backend exposes these endpoints:

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check + API key status |
| `GET` | `/styles` | List available video styles |
| `POST` | `/generate` | Generate video script from URL |

### POST `/generate`

**Request body:**
```json
{
  "url": "https://example.com/some-article",
  "style": "documentary",
  "duration": 60
}
```

**Styles:** `documentary` · `explainer` · `social_media`  
**Duration:** 30–180 seconds

**Response:**
```json
{
  "success": true,
  "article": { "title": "...", "url": "...", "content_length": 3200 },
  "script": {
    "title": "Video title",
    "summary": "One-line summary",
    "keywords": ["ai", "tech", "..."],
    "estimated_duration": 60,
    "style": "documentary",
    "narration": "Full narration text...",
    "scenes": [
      {
        "scene_number": 1,
        "timestamp_start": "0:00",
        "timestamp_end": "0:10",
        "title": "Scene title",
        "visual_description": "What appears on screen",
        "narration_excerpt": "Spoken words for this scene",
        "b_roll_suggestions": ["aerial shot", "close-up"],
        "text_overlays": ["Overlay text"],
        "mood": "dramatic"
      }
    ]
  }
}
```

---

## ⚙️ Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | ✅ Yes | Google Gemini API key |

---

## 🛑 Stopping the App

```bash
docker compose down
```

To remove built images too:
```bash
docker compose down --rmi all
```

---

## 🧪 Development (without Docker)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
GEMINI_API_KEY=your_key uvicorn main:app --reload --port 8000
```

**Frontend:** Open `frontend/index.html` directly in your browser (the JS auto-detects `localhost` and hits `http://localhost:8000` directly).

---

## 📄 License

MIT — see [LICENSE](LICENSE)

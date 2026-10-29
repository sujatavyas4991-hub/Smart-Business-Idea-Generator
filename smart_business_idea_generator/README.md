# 💡 Smart Business Idea Generator

> **An Agentic AI web application powered by IBM Granite LLM** — a 7-agent multi-agent system that generates personalised, ethically-screened, and feasibility-scored business ideas from your profile.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask)
![IBM Granite](https://img.shields.io/badge/IBM%20Granite-3.3--8B-blue?logo=ibm)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📋 Table of Contents

- [Features](#-features)
- [Multi-Agent Architecture](#-multi-agent-architecture)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [Environment Variables](#-environment-variables)
- [API Reference](#-api-reference)
- [Deployment](#-deployment)
- [Ethics & Responsible AI](#-ethics--responsible-ai)
- [Contributing](#-contributing)

---

## ✨ Features

### 🎯 Core
| Feature | Description |
|---------|-------------|
| **Personalised Idea Generation** | 6 diverse, scored ideas based on your skills, budget & industry |
| **Feasibility Scoring** | Multi-dimensional scoring (0–100) across feasibility, impact, innovation & market potential |
| **Deep Refinement** | Full business plan: pricing, go-to-market strategy, competitive analysis |
| **Innovation Roadmap** | Phased 12-month action plan with milestones |
| **AI Chat Assistant** | Ask any business question powered by IBM Granite |

### 📊 Dashboard & Visualisations
- Idea cards with score bars and recommendation badges
- Radar / bar / doughnut / ranking charts via Chart.js
- Interactive idea mind map
- Market intelligence report
- Ethics & responsibility assessment

### 🎙️ Multimodal Input
- **Text** — Standard profile form
- **Image Upload** — Drag & drop; AI extracts business keywords
- **Voice Recording** — Browser microphone → text transcription
- **Audio Upload** — Upload pre-recorded audio files

### 🔧 Productivity
- Save ideas to persistent local storage
- Compare ideas side-by-side with radar charts
- Export as JSON or formatted text report

---

## 🤖 Multi-Agent Architecture

```
User Profile
     │
     ▼
┌─────────────────────────────────────────────────────┐
│                 Ethics Guardrail Agent               │  ← Input screening
└─────────────────────────────────────────────────────┘
     │
     ▼
┌──────────────┐    ┌───────────────────┐    ┌──────────────────┐
│   RAG Agent  │───▶│ Trend Analysis    │───▶│  Idea Generation │
│  (Knowledge) │    │     Agent         │    │     Agent        │
└──────────────┘    └───────────────────┘    └──────────────────┘
                                                       │
                                                       ▼
                                             ┌──────────────────┐
                                             │ Feasibility Agent│
                                             └──────────────────┘
                                                       │
                                                       ▼
                                             ┌──────────────────┐
                                             │  Ethics Guardrail│  ← Output screening
                                             └──────────────────┘
                                                       │
                                              ┌────────┴────────┐
                                              ▼                 ▼
                                     ┌────────────┐   ┌────────────────┐
                                     │ Refinement │   │ Roadmap Agent  │
                                     │   Agent    │   │  (on-demand)   │
                                     └────────────┘   └────────────────┘
```

| Agent | Role |
|-------|------|
| **RAG Agent** | Retrieves domain-specific knowledge and market intelligence |
| **Trend Analysis Agent** | Identifies hot trends, emerging technologies, and market gaps |
| **Idea Generation Agent** | Creates 6 personalised, innovative business ideas |
| **Feasibility Agent** | Scores each idea across 4 dimensions (0–100) |
| **Refinement Agent** | Deep-dives into any idea with full business plan details |
| **Roadmap Agent** | Generates a 12-month phased innovation roadmap |
| **Ethics Guardrail Agent** | Screens input/output for ethical compliance and responsible AI |

---

## 📁 Project Structure

```
smart_business_idea_generator/
├── app.py                    # Main Flask application (all routes)
├── run.py                    # Convenience startup script (auto-installs deps)
├── requirements.txt          # Python dependencies
├── env.example               # Environment config template → rename to .env
├── agents/
│   ├── __init__.py
│   ├── base_agent.py         # IBM Granite LLM base class
│   ├── rag_agent.py          # Knowledge retrieval agent
│   ├── trend_agent.py        # Market trend analysis agent
│   ├── idea_agent.py         # Idea generation agent
│   ├── feasibility_agent.py  # Feasibility scoring agent
│   ├── refinement_agent.py   # Deep refinement + Q&A agent
│   ├── roadmap_agent.py      # Innovation roadmap agent
│   └── ethics_agent.py       # Ethics guardrail agent
├── templates/
│   └── index.html            # Single-page application template
├── static/
│   ├── css/style.css         # Complete UI stylesheet
│   ├── js/app.js             # Frontend application logic
│   └── uploads/              # Uploaded media (auto-created, git-ignored)
└── data/
    └── saved_ideas.json      # Persisted saved ideas (auto-created, git-ignored)
```

---

## 🔧 Prerequisites

- **Python 3.9+**
- An **IBM watsonx.ai** account with:
  - A valid API key
  - A project ID
  - Access to `ibm/granite-3-3-8b-instruct`

> No IBM account? Sign up for a free trial at [ibm.com/watsonx](https://www.ibm.com/watsonx).

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/smart-business-idea-generator.git
cd smart-business-idea-generator/smart_business_idea_generator
```

### 2. Create and activate a virtual environment

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp env.example .env
# Open .env and fill in your IBM watsonx.ai credentials
```

### 5. Run the application

```bash
# Option A — direct
python app.py

# Option B — auto-installs deps and opens browser
python run.py

# Option C — Windows batch script
setup_and_run.bat

# Option D — production (gunicorn, Linux/macOS)
gunicorn -w 2 -b 0.0.0.0:5000 app:app
```

### 6. Open in your browser

```
http://localhost:5000
```

---

## 🔑 Environment Variables

Copy `env.example` to `.env` and populate the values:

| Variable | Required | Description |
|----------|----------|-------------|
| `IBM_API_KEY` | ✅ | Your IBM watsonx.ai API key |
| `IBM_PROJECT_ID` | ✅ | Your watsonx.ai project ID |
| `IBM_ENDPOINT` | ✅ | Regional endpoint (e.g. `https://au-syd.ml.cloud.ibm.com`) |
| `SECRET_KEY` | ✅ | Flask session secret key (change in production) |
| `FLASK_ENV` | ❌ | `development` or `production` (default: `production`) |
| `FLASK_DEBUG` | ❌ | `1` to enable debug mode (never in production) |
| `PORT` | ❌ | Port to listen on (default: `5000`) |

> **⚠️ Security:** Never commit your `.env` file. It is listed in `.gitignore`.

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serve the single-page application |
| `GET` | `/api/health` | Health check — returns model info |
| `POST` | `/api/generate` | Run full agent pipeline → returns ideas |
| `POST` | `/api/refine` | Deep-refine a specific idea |
| `POST` | `/api/ask` | Ask AI a question about a specific idea |
| `POST` | `/api/roadmap` | Generate a 12-month roadmap for an idea |
| `POST` | `/api/chat` | General business AI chat |
| `POST` | `/api/save` | Save an idea to disk |
| `GET` | `/api/saved` | List all saved ideas |
| `DELETE` | `/api/saved/<id>` | Delete a saved idea |
| `POST` | `/api/compare` | Compare multiple ideas (side-by-side) |
| `POST` | `/api/upload/image` | Upload & analyse an inspiration image |
| `POST` | `/api/upload/audio` | Upload & transcribe an audio file |
| `POST` | `/api/export/json` | Export ideas as JSON download |
| `POST` | `/api/export/txt` | Export ideas as formatted text report |
| `GET` | `/api/trends` | Get current trend data from last session |

### Example — Generate Ideas

```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "profile": {
      "name": "Alex",
      "skills": "software development, UX design",
      "budget": "10000",
      "industry": "EdTech",
      "location": "Sydney"
    }
  }'
```

---

## ☁️ Deployment

### Deploy to Render (free tier)

1. Push this repo to GitHub.
2. Create a new **Web Service** on [render.com](https://render.com).
3. Set **Build Command**: `pip install -r requirements.txt`
4. Set **Start Command**: `gunicorn -w 2 -b 0.0.0.0:$PORT app:app`
5. Add environment variables (`IBM_API_KEY`, `IBM_PROJECT_ID`, etc.) in the Render dashboard.

### Deploy to Railway

```bash
railway init
railway add
railway up
```
Set environment variables via `railway variables set IBM_API_KEY=...`

### Deploy with Docker

```bash
# Build
docker build -t smart-business-idea-generator .

# Run
docker run -p 5000:5000 \
  -e IBM_API_KEY=your_key \
  -e IBM_PROJECT_ID=your_project_id \
  smart-business-idea-generator
```

> A `Dockerfile` is not included by default — see the Flask + Gunicorn Docker documentation for a minimal template.

---

## 🛡️ Ethics & Responsible AI

This application is built with responsible AI principles at its core:

- **Input/Output Guardrails** — every user input and generated idea is screened for harmful content
- **Privacy Protection** — minimal PII collection; names are truncated to first name only
- **Inclusion** — ideas include accessibility and diversity recommendations
- **Compliance Notes** — GDPR/CCPA guidance surfaced in ethics reports
- **HAM Tone** — all AI responses follow Helpful, Accurate, and Motivating principles
- **Transparency** — ethics assessment report generated for every session

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "feat: add my feature"`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

*Built with ❤️ using IBM Granite · Responsible AI · Multi-Agent Architecture*

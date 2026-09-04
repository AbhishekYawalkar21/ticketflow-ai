# 🎫 TicketFlow AI - Intelligent Support Ticket Classification

TicketFlow AI is an intelligent support ticket management system that classifies, prioritizes, and routes incoming tickets using a local LLM — achieving a 70% automation rate with no external APIs or subscription costs. It ingests tickets via email (IMAP/SMTP) or API, runs them through AI-powered classification, multilingual (German & English) language handling, and automatic sentiment detection, then surfaces the results on a real-time analytics dashboard. Built on an async Celery task queue with WebSocket-based live updates, the entire system — including the Mistral 7B classification model — runs on local infrastructure via Ollama, so no ticket data ever leaves your servers.

## 🚀 Key Features

- 🤖 **AI-Powered Classification** — automatic ticket categorization using a local Ollama LLM, no external APIs required
- 🌍 **Multilingual Support** — handles German and English ticket processing out of the box
- 😊 **Sentiment Analysis** — automatic detection of customer sentiment on every incoming ticket
- ⚡ **Real-time Updates** — WebSocket-based live dashboard reflects ticket status instantly
- 🔌 **Email Integration** — IMAP/SMTP integration automatically ingests tickets from support inboxes
- 📊 **Analytics Dashboard** — real-time metrics and automation-rate tracking
- 🚀 **Async Processing** — Celery-based task queue keeps classification scalable and non-blocking
- 📦 **Docker-Ready** — fully containerized for one-command deployment
- 🔒 **Production Hardened** — rate limiting, error handling, and health checks built in

## 🏗 Architecture

- Backend: FastAPI + PostgreSQL + Redis + Celery
- Frontend: React 18 dashboard with real-time WebSocket updates
- AI: Local Ollama LLM (Mistral 7B) for classification, TextBlob for sentiment analysis
- Deployment: Docker + Docker Compose + Nginx

## 🛠 Tech Stack

**Backend**
- FastAPI 0.104.1 (REST + WebSocket API)
- SQLAlchemy 2.0 (ORM)
- Pydantic 2.5 (data validation)
- Celery 5.3 (distributed task queue)
- Redis 7 (message broker & cache)
- Ollama (local LLM inference)
- Mistral 7B (classification model, free & open source)
- TextBlob (NLP sentiment analysis)

**Frontend**
- React 18.2 (UI framework)
- Axios (HTTP client)
- Recharts (data visualization)

**Infrastructure**
- Docker + Docker Compose (containerization & orchestration)
- Nginx (reverse proxy)
- PostgreSQL 16 (relational database)
- Redis 7 (cache & broker)
- GitHub Actions (CI/CD)

## 🔄 How It Works

```
Ticket Received (Email via IMAP/SMTP, or API)
   ↓
Task Queued for Async Processing (Celery + Redis)
   ↓
AI Classification (Ollama - Mistral 7B):
   ├─ Category Detection
   ├─ Priority Assignment
   ├─ Language Detection (DE / EN)
   └─ Sentiment Analysis (TextBlob)
   ↓
Results Stored in PostgreSQL
   ↓
Live Update Pushed via WebSocket
   ↓
Analytics Dashboard (React)
```

Each classification runs as an independent async task, so the pipeline stays responsive under load and new processing steps can be added without touching the ingestion or dashboard layers.

## ⚙️ Getting Started

```
git clone <this-repo-url>
cd ticketflow-ai
```

### Option A — Docker (recommended, fastest)
Requires only Docker Desktop (4GB+ RAM, 15GB+ disk space) — no local Python, Node.js, PostgreSQL, Redis, or Ollama install needed; everything runs in containers.

```bash
docker-compose up -d
```

On the first run, pull the classification model (10-15 minutes):
```bash
docker-compose exec ollama ollama pull mistral:7b
```

Then verify everything is up:
```bash
docker-compose ps
curl http://localhost:8000/health
```

### Option B — Manual setup
Requires Python 3.11+, Node.js, PostgreSQL, Redis, and [Ollama](https://ollama.ai/) installed and running locally with a pulled model (`ollama pull mistral:7b`).

Configure environment:
```bash
cp .env.example .env       # then fill in your values
```

Backend:
```bash
cd app
python -m venv venv

# Windows
venv\Scripts\Activate.ps1

# Mac/Linux
source venv/bin/activate

pip install -r ../requirements.txt
uvicorn app.main:app --reload
```

Celery worker (separate terminal):
```bash
celery -A app.tasks worker --loglevel=info
```

Frontend:
```bash
cd frontend
npm install
npm start
```

## 🌍 Real-World Applications

- Customer support automation for SaaS companies
- Multilingual helpdesk operations (DACH + English-speaking markets)
- IT service desk ticket triage
- E-commerce customer service queues
- Internal HR/IT support ticket routing
- Automated first-response and sentiment-based escalation

## 🔒 Copyright & Licensing

> [!NOTE]
> © 2026 Abhishek Yawalkar. All rights reserved.
> This repository is a personal project created for skill-building and hands-on learning purposes. Viewing and forking the repository for personal review is permitted under GitHub's Terms of Service. However, no permission is granted to copy, modify, redistribute, or use this source code, in whole or in part, for any commercial or non-commercial projects.
> For inquiries regarding usage or collaboration, please contact the copyright holder directly.
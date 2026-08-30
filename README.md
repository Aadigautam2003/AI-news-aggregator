Here is a complete, production-ready `README.md` formatted to expand on your project overview with architecture, prerequisites, local installation, branch breakdown, and environment configuration.

---

# AI News Aggregator

An end-to-end AI-powered news aggregator built from scratch. This application scrapes and aggregates news articles across various feeds, leverages Large Language Models (LLMs) for automated summarization, topic tagging, and sentiment analysis, and serves the curated feed via a modern web interface.

---

## Architecture Overview

```
 ┌────────────────┐     ┌──────────────────┐     ┌──────────────────┐
 │  News Sources  │ ──> │ Ingestion Engine │ ──> │   LLM Pipeline   │
 │ (RSS / APIs)   │     │ (Fetcher/Parser) │     │ (Summary/Tags)   │
 └────────────────┘     └──────────────────┘     └────────┬─────────┘
                                                          │
 ┌────────────────┐     ┌──────────────────┐              │
 │  Web Frontend  │ <── │   Backend API    │ <────────────┘
 │ (React / UI)   │     │ (FastAPI/Node)   │
 └────────────────┘     └────────┬─────────┘
                                 │
                        ┌────────┴─────────┐
                        │ Database / Cache │
                        │ (Postgres/Redis) │
                        └──────────────────┘

```

* **Ingestion Pipeline:** Scheduled workers fetch raw articles from multiple RSS feeds and public APIs.
* **AI Processing Layer:** Deduplicates content, extracts clean article bodies, and queries an LLM to generate concise summaries, categorize topics, and assess sentiment.
* **Backend API:** Stores structured data and exposes REST/GraphQL endpoints for pagination, filtering, and search.
* **Frontend Dashboard:** A responsive user interface to browse categorized summaries, filter by sentiment or topic, and view real-time updates.

---

## Branch Breakdown & Checkpoints

This repository is structured across three progression branches:

| Branch | Phase | Scope & Milestones |
| --- | --- | --- |
| **`master`** | **Part 1: Core Setup** | Local development environment, RSS ingestion workers, raw data parsing, initial LLM summarization pipeline, and local SQLite/Postgres schemas. |
| **`deployment`** | **Part 2: Infrastructure** | Docker containerization (`Dockerfile`, `docker-compose.yml`), cloud database integration, background task scheduling (e.g., Celery/Cron), and reverse proxy setup. |
| **`deployment-final`** | **Part 3: Production Ready** | Caching layer (Redis), rate limiting, error monitoring (Sentry), CI/CD workflows, edge caching, and cost-optimized LLM batching. |

---

## Prerequisites

Ensure you have the following installed on your local machine:

* **Node.js** (v18+ or v20+) / **Python** (3.10+) *(depending on your backend setup)*
* **Docker** & **Docker Compose**
* **Git**
* API Keys:
* OpenAI / Anthropic API Key (or local Ollama instance)
* News API / RSS credentials (if applicable)



---

## Getting Started (Local Development)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai-news-aggregator

```

### 2. Configure Environment Variables

Copy the example environment file and add your credentials:

```bash
cp .env.example .env

```

Fill in the required fields:

```ini
# LLM Configuration
LLM_PROVIDER=openai # or anthropic / ollama
OPENAI_API_KEY=your_openai_api_key_here
LLM_MODEL=gpt-4o-mini

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/news_aggregator
REDIS_URL=redis://localhost:6379/0

# App Config
PORT=8000
NODE_ENV=development

```

### 3. Run with Docker Compose

To launch the database, cache, and ingestion services locally:

```bash
docker-compose up -d

```

### 4. Run Locally Without Docker

**Backend:**

```bash
# Example for Python/FastAPI
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

```

**Frontend:**

```bash
cd frontend
npm install
npm run dev

```

---

## How to Follow the Live Build

This repository is designed for active, iterative learning:

1. **Start on `master**` to build the initial scrapers and LLM integrations.
2. **Switch to `deployment**` when the video reaches cloud provisioning and container configuration:
```bash
git checkout deployment

```


3. **Inspect `deployment-final**` to review production hardening, edge-case fixes, and optimizations:
```bash
git checkout deployment-final

```



---

## Key Features

* **Automated Feed Polling:** Regularly syncs with tech, finance, and global news sources.
* **Smart Deduplication:** Identifies and groups duplicate reporting across outlets.
* **Semantic Tagging & Summarization:** Extracts 3-bullet executive summaries and high-level sentiment.
* **Search & Filter:** Filter by tag, read time, sentiment score, or publication date.

---

## License

This project is licensed under the MIT License — see the [LICENSE](https://www.google.com/search?q=LICENSE) file for details.

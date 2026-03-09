# 📈 AlphaDawn

**AI-powered pre-market intelligence platform for Indian stock markets.**

AlphaDawn uses a multi-agent pipeline to scan financial news, exchange announcements, and global signals every morning before market open — then generates actionable trade setups with entry, target, and stop-loss levels.

---

## Architecture

```
Ingestion Agents ──► Processing Agents ──► Intelligence Agents ──► Delivery
(Twitter, News,       (Cleaner, Ranker)     (Catalyst, Stock       (Telegram,
 Exchange, Global)                           Data, Trade Setup)     Email, API)
```

## Quick Start

### 1. Clone & configure
```bash
cp .env.example .env
# Fill in your API keys, DB credentials, etc.
```

### 2. Run with Docker
```bash
docker-compose up --build
```

### 3. Run locally (development)
```bash
# Backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend && npm install && npm run dev
```

### 4. Run the pipeline manually
```bash
python pipeline.py
```

## API Endpoints

| Method | Endpoint              | Description               |
|--------|-----------------------|---------------------------|
| GET    | `/api/v1/picks`       | Today's trade picks       |
| GET    | `/api/v1/picks/history` | Historical picks + outcomes |
| GET    | `/api/v1/news`        | Latest curated news feed  |
| POST   | `/api/v1/feedback`    | Submit feedback on a pick |

## Tech Stack

- **Backend**: Python 3.11, FastAPI, SQLAlchemy 2.0, APScheduler
- **AI/LLM**: OpenAI / Gemini for catalyst classification & trade setup
- **Data**: PostgreSQL, Redis, yfinance, httpx
- **Frontend**: React 18, Vite, Recharts
- **Delivery**: Telegram Bot, Email (SMTP)
- **Infra**: Docker, Docker Compose

## License

MIT

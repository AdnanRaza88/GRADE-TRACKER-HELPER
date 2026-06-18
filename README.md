GradePulse — Student Grade Tracker

> **Project  · Adnan raza
> Full-stack academic performance tracker with AI-powered study assistance.

---

## Architecture

```
gradepulse/
├── backend/    ← FastAPI + SQLModel + LangChain + Groq
└── frontend/   ← Streamlit Neumorphic UI
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI |
| Database | SQLModel + SQLite |
| Validation | Pydantic v2 |
| Data Processing | Pandas |
| AI | LangChain + Groq (LLaMA 3.3 70B) |
| Frontend | Streamlit |
| Deployment | Railway (2 services) |

## Features

- ✅ Full CRUD grade management
- ✅ Bulk CSV/Excel upload with Pandas validation
- ✅ AI study tips (LangChain + Groq)
- ✅ AI daily routine generator
- ✅ Custom grading scale (A+/A/B+... or user-defined)
- ✅ Student search by roll number
- ✅ Export to CSV / Excel / JSON
- ✅ Neumorphic light-mode Streamlit UI
- ✅ Plotly dashboard charts

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
copy .env.example .env   # then add GROQ_API_KEY
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
pip install -r requirements.txt
copy .env.example .env   # API_BASE_URL=http://localhost:8000
streamlit run app.py
```

## Deployment (Railway)

1. Create two Railway services — one for `backend/`, one for `frontend/`
2. Set env vars per service (see each service's README)
3. Add Railway Volume `/data` on backend for SQLite persistence
4. Both `nixpacks.toml` files lock Python 3.11

---
*Built with FastAPI, Streamlit, LangChain, and Groq AI*

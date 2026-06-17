# GradePulse Backend

FastAPI + SQLModel + LangChain + Groq AI — Student Grade Tracker API

## Quick Start (Local)

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt

# Copy and fill your .env
copy .env.example .env
# Edit .env: add your GROQ_API_KEY

uvicorn main:app --reload --port 8000
```

Visit **http://localhost:8000/docs** for the interactive API docs.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/grades` | Create grade |
| GET | `/grades` | List all grades |
| GET | `/grades/{id}` | Get grade by ID |
| PUT | `/grades/{id}` | Update grade |
| DELETE | `/grades/{id}` | Delete grade |
| POST | `/grades/{id}/study-tips` | AI study tips |
| POST | `/grades/{id}/routine` | AI daily routine |
| GET | `/grades/student/{roll}` | All grades for a student |
| POST | `/grades/bulk-upload` | CSV/Excel bulk upload |
| GET | `/grades/config` | List grading config |
| POST | `/grades/config` | Create grade threshold |
| DELETE | `/grades/config/{id}` | Delete config entry |
| GET | `/grades/export` | Export (CSV/Excel/JSON) |

## Sample JSON — Create Grade

```json
{
  "student_name": "Ali Hassan",
  "roll_number": "CS-0267",
  "subject": "Mathematics",
  "marks_obtained": 87,
  "total_marks": 100,
  "semester": "Spring 2024",
  "date": "2024-01-15"
}
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Groq API key for AI features |
| `SECRET_KEY` | App secret key |
| `DB_PATH` | SQLite DB path (Railway: `/data/gradepulse.db`) |

## Railway Deployment

1. Push `backend/` folder to a GitHub repo
2. Create a new Railway service → connect repo
3. Set environment variables in Railway dashboard
4. Add a Railway **Volume** mounted at `/data`
5. Set `DB_PATH=/data/gradepulse.db`
6. Deploy — Railway auto-detects `nixpacks.toml`

## Tech Stack

- **FastAPI** — Modern, fast Python web framework
- **SQLModel** — SQLite ORM with Pydantic integration
- **Pandas** — CSV/Excel parsing and validation
- **LangChain + Groq** — LLaMA 3.3 70B AI features
- **Uvicorn** — ASGI server

---
*Project student grade traker
— Adnan · Roll No. 0267*

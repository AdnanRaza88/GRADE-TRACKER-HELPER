# GradePulse Frontend

Streamlit UI — Neumorphic Light Mode | Academic Performance Tracker

## Quick Start (Local)

```bash
cd frontend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt

# Copy and fill your .env
copy .env.example .env
# Edit .env: set API_BASE_URL=http://localhost:8000

streamlit run app.py
```

Visit **http://localhost:8501**

## Pages

| Page | Description |
|------|-------------|
| 🏠 Home | Feature overview |
| 📊 Dashboard | Stats, KPIs, and Plotly charts |
| ✏️ Grades | Add, edit, delete, search grades |
| 📁 Bulk Upload | CSV/Excel drag-and-drop upload |
| 🤖 AI Tips | Personalised study tips via Groq AI |
| 📅 Routine | AI daily study routine generator |
| ⚙️ Config | Custom grading scale configuration |
| 📤 Export | Download CSV / Excel / JSON |

## Design

- **Theme:** Neumorphic 3D Light Mode
- **Colors:** Indigo (#4F46E5) + Sky Blue (#0EA5E9) on #E8EEF6 background
- **Font:** Inter (Google Fonts)
- **Charts:** Plotly (bar, pie, gauge)

## Environment Variables

| Variable | Description |
|----------|-------------|
| `API_BASE_URL` | Backend API URL (Railway backend service URL) |

## Railway Deployment

1. Push `frontend/` folder to a GitHub repo
2. Create a new Railway service → connect repo
3. Set `API_BASE_URL` to your deployed backend Railway URL
4. Deploy — Railway auto-detects `nixpacks.toml`

---
*Project 8 — Adnan · Roll No. 0267*

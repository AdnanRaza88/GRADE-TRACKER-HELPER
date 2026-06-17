"""
Daily Routine Page — AI-generated full daily study routine
"""
import streamlit as st
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.api_client import get_all_grades, get_routine

# ── CSS ────────────────────────────────────────────────────────────
css_path = Path(__file__).parent.parent / "styles" / "neumorphic.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("# 📅 Daily Routine Generator")
st.markdown(
    "<p style='color:#64748B;margin-top:-0.5rem;'>"
    "Get a personalised AI daily routine — study schedule, health tips, sleep & more</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ── LOAD GRADES ────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def _load():
    return get_all_grades()

try:
    grades = _load()
except Exception as e:
    st.error(f"❌ Could not load grades: {e}")
    st.stop()

if not grades:
    st.info("📭 No grade records found. Add grades first!")
    st.stop()

df = pd.DataFrame(grades)
df["label"] = df.apply(
    lambda r: f"ID {r['id']} — {r['student_name']} | {r['subject']} ({r['percentage']}%)",
    axis=1,
)

# ── FORM ──────────────────────────────────────────────────────────
st.markdown("### 1️⃣ Select Grade Record")
selected_label = st.selectbox("Which grade is this routine for?", df["label"].tolist(), key="routine_select")
selected_row   = df[df["label"] == selected_label].iloc[0]
grade_id       = int(selected_row["id"])

st.markdown("---")
st.markdown("### 2️⃣ Tell Us About Your Daily Life")

with st.form("routine_form"):
    col1, col2 = st.columns(2)

    with col1:
        free_hours = st.slider(
            "⏰ Free hours available per day",
            min_value=1.0, max_value=12.0, value=4.0, step=0.5,
            help="How many hours per day can you dedicate to studying?"
        )
        sleep_hours = st.slider(
            "😴 Sleep hours per night",
            min_value=4.0, max_value=12.0, value=7.0, step=0.5,
        )
        physical_activity = st.toggle(
            "🏃 Do you do physical activity?",
            value=True,
            help="Walking, jogging, gym, sports — any physical exercise"
        )

    with col2:
        weak_subject = st.text_input(
            "📚 Your weakest / priority subject",
            value=selected_row["subject"],
            placeholder="e.g. Mathematics",
        )
        water_intake = st.selectbox(
            "💧 Your daily water intake habit",
            [
                "Less than 4 glasses (low)",
                "4–6 glasses (moderate)",
                "7–8 glasses (good)",
                "8+ glasses (excellent)",
            ],
            index=1,
        )

    st.markdown("---")
    submitted = st.form_submit_button("🤖 Generate My Daily Routine", use_container_width=True)

# ── GENERATE & DISPLAY ─────────────────────────────────────────────
if submitted:
    if not weak_subject.strip():
        st.error("❌ Please enter your weakest subject.")
    else:
        with st.spinner("🤖 AI is building your personalised routine... (10–20 seconds)"):
            try:
                result = get_routine(grade_id, {
                    "free_hours":        free_hours,
                    "weak_subject":      weak_subject.strip(),
                    "physical_activity": physical_activity,
                    "sleep_hours":       sleep_hours,
                    "water_intake":      water_intake,
                })

                routine = result.get("routine", {})
                student = result.get("student_name", "Student")

                # Check if AI returned an error
                if "error" in routine:
                    st.warning("⚠️ AI returned an unexpected format. Raw output:")
                    st.code(routine.get("raw_output", str(routine)))
                    st.stop()

                st.markdown("---")
                st.markdown(
                    f"<h2 style='color:#4F46E5;'>📅 Daily Routine for {student}</h2>",
                    unsafe_allow_html=True,
                )

                # ── MORNING ────────────────────────────────────────
                if "morning" in routine:
                    m = routine["morning"]
                    acts = "".join(f"<li>{a}</li>" for a in m.get("activities", []))
                    st.markdown(
                        f"""<div class="routine-section">
                          <div class="routine-title">🌅 Morning</div>
                          <div class="routine-time">⏰ {m.get('time','')}</div>
                          <ul style="margin:0;padding-left:1.2rem;color:#475569;font-size:0.88rem;">{acts}</ul>
                        </div>""",
                        unsafe_allow_html=True,
                    )

                # ── STUDY BLOCKS ────────────────────────────────────
                if "study_blocks" in routine:
                    for i, block in enumerate(routine["study_blocks"], 1):
                        goals = "".join(f"<li>{g}</li>" for g in block.get("goals", []))
                        st.markdown(
                            f"""<div class="routine-section" style="border-left-color:#0EA5E9;">
                              <div class="routine-title">📖 Study Block {i} — {block.get('subject','')}</div>
                              <div class="routine-time">⏰ {block.get('time','')} · Technique: {block.get('technique','')}</div>
                              <ul style="margin:0;padding-left:1.2rem;color:#475569;font-size:0.88rem;">{goals}</ul>
                            </div>""",
                            unsafe_allow_html=True,
                        )

                # ── BREAKS ──────────────────────────────────────────
                if "breaks" in routine:
                    b = routine["breaks"]
                    acts = "".join(f"<li>{a}</li>" for a in b.get("activities", []))
                    st.markdown(
                        f"""<div class="routine-section" style="border-left-color:#10B981;">
                          <div class="routine-title">☕ Breaks</div>
                          <div class="routine-time">⏰ {b.get('duration','')}</div>
                          <ul style="margin:0;padding-left:1.2rem;color:#475569;font-size:0.88rem;">{acts}</ul>
                        </div>""",
                        unsafe_allow_html=True,
                    )

                # ── EVENING ─────────────────────────────────────────
                if "evening" in routine:
                    e = routine["evening"]
                    acts = "".join(f"<li>{a}</li>" for a in e.get("activities", []))
                    st.markdown(
                        f"""<div class="routine-section" style="border-left-color:#F59E0B;">
                          <div class="routine-title">🌆 Evening</div>
                          <div class="routine-time">⏰ {e.get('time','')}</div>
                          <ul style="margin:0;padding-left:1.2rem;color:#475569;font-size:0.88rem;">{acts}</ul>
                        </div>""",
                        unsafe_allow_html=True,
                    )

                # ── SLEEP ────────────────────────────────────────────
                if "sleep" in routine:
                    s = routine["sleep"]
                    tips = "".join(f"<li>{t}</li>" for t in s.get("tips", []))
                    st.markdown(
                        f"""<div class="routine-section" style="border-left-color:#8B5CF6;">
                          <div class="routine-title">🌙 Sleep</div>
                          <div class="routine-time">⏰ Bedtime: {s.get('bedtime','')} · Duration: {s.get('duration','')}</div>
                          <ul style="margin:0;padding-left:1.2rem;color:#475569;font-size:0.88rem;">{tips}</ul>
                        </div>""",
                        unsafe_allow_html=True,
                    )

                # ── HEALTH TIPS ──────────────────────────────────────
                if "health_tips" in routine:
                    ht = routine["health_tips"]
                    h_col1, h_col2, h_col3 = st.columns(3)

                    def _tip_list(items):
                        return "".join(f"<li style='font-size:0.82rem;color:#475569;'>{i}</li>" for i in items)

                    with h_col1:
                        st.markdown(
                            f"<div class='neu-card'><b>💧 Water</b><ul style='padding-left:1.2rem;margin-top:0.5rem;'>"
                            f"{_tip_list(ht.get('water', []))}</ul></div>",
                            unsafe_allow_html=True,
                        )
                    with h_col2:
                        st.markdown(
                            f"<div class='neu-card'><b>🥗 Nutrition</b><ul style='padding-left:1.2rem;margin-top:0.5rem;'>"
                            f"{_tip_list(ht.get('nutrition', []))}</ul></div>",
                            unsafe_allow_html=True,
                        )
                    with h_col3:
                        st.markdown(
                            f"<div class='neu-card'><b>🏃 Exercise</b><ul style='padding-left:1.2rem;margin-top:0.5rem;'>"
                            f"{_tip_list(ht.get('exercise', []))}</ul></div>",
                            unsafe_allow_html=True,
                        )

            except Exception as e:
                st.error(f"❌ AI service error: {e}")
                st.info("💡 Make sure your GROQ_API_KEY is set in the backend .env file.")


import streamlit as st
import os
from pathlib import Path


st.set_page_config(
    page_title="GradePulse",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "GradePulse — Student Grade Tracker | Built by Adnan (Roll No. 0267)",
    },
)


css_path = Path(__file__).parent / "styles" / "neumorphic.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding: 1rem 0 1.5rem 0;">
          <div style="font-size:3rem;">🎓</div>
          <div style="font-size:1.3rem; font-weight:800;
               background: linear-gradient(135deg, #4F46E5, #0EA5E9);
               -webkit-background-clip: text; -webkit-text-fill-color: transparent;
               background-clip: text;">GradePulse</div>
          <div style="font-size:0.75rem; color:#64748B; font-weight:500;
               margin-top:0.2rem;">Academic Performance Tracker</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown(
        "<p style='font-size:0.7rem;color:#94A3B8;text-transform:uppercase;"
        "letter-spacing:0.1em;font-weight:600;margin-bottom:0.5rem;'>Navigation</p>",
        unsafe_allow_html=True,
    )

    # Health check indicator
    try:
        from utils.api_client import health_check
        alive = health_check()
        status_color = "#10B981" if alive else "#EF4444"
        status_text  = "API Online" if alive else "API Offline"
        status_dot   = "●"
    except Exception:
        status_color = "#F59E0B"
        status_text  = "Checking..."
        status_dot   = "●"

    st.markdown(
        f"<div style='display:flex;align-items:center;gap:0.5rem;"
        f"background:rgba(79,70,229,0.06);border-radius:10px;padding:0.5rem 0.8rem;"
        f"margin-bottom:1rem;'>"
        f"<span style='color:{status_color};font-size:0.7rem;'>{status_dot}</span>"
        f"<span style='font-size:0.75rem;font-weight:600;color:#475569;'>{status_text}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown(
        """
        <div style="font-size:0.72rem; color:#94A3B8; text-align:center; padding:1rem 0 0 0;">
          <b>Project 8</b> · Adnan · Roll 0267<br>
          <span style="color:#CBD5E1;">FastAPI + Streamlit + Groq AI</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div style="text-align:center; padding: 3rem 0 2rem 0;">
      <div style="font-size:4rem; margin-bottom:1rem;">🎓</div>
      <h1 style="font-size:3rem !important;">GradePulse</h1>
      <p style="font-size:1.1rem; color:#64748B; max-width:600px; margin:0.5rem auto 2rem auto;
         font-weight:400; line-height:1.7;">
        Your intelligent academic performance tracker.<br>
        Manage grades, upload bulk data, and get AI-powered study advice.
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)


cols = st.columns(3)
features = [
    ("[DATA]", "Dashboard", "Real-time stats, charts, and grade distribution at a glance."),
    ("[EDIT]", "Grade Management", "Add, edit, and delete grade records with auto-computed percentages."),
    ("📁", "Bulk Upload", "Upload CSV or Excel files with Pandas validation and error reporting."),
    ("[AI]", "AI Study Tips", "Get 5 personalised study tips powered by Groq LLaMA 3.3."),
    ("[CALENDER]", "Daily Routine", "AI-generated full daily schedule based on your habits and goals."),
    ("[SETTING]", "Grade Config", "Define custom A/B/C thresholds and pass/fail rules."),
]

for i, (icon, title, desc) in enumerate(features):
    with cols[i % 3]:
        st.markdown(
            f"""
            <div class="metric-card" style="text-align:left; margin-bottom:1rem;">
              <div style="font-size:1.8rem; margin-bottom:0.5rem;">{icon}</div>
              <div style="font-weight:700; font-size:1rem; color:#1E293B; margin-bottom:0.3rem;">{title}</div>
              <div style="font-size:0.82rem; color:#64748B; line-height:1.5;">{desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("---")
st.markdown(
    """
    <p style="text-align:center; color:#94A3B8; font-size:0.8rem;">
       Use the sidebar to navigate between pages
    </p>
    """,
    unsafe_allow_html=True,
)

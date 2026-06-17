
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.api_client import get_all_grades


css_path = Path(__file__).parent.parent / "styles" / "neumorphic.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("#  Dashboard")
st.markdown(
    "<p style='color:#64748B;margin-top:-0.5rem;'>Live overview of all student grade records</p>",
    unsafe_allow_html=True,
)
st.markdown("---")


@st.cache_data(ttl=30)
def load_grades():
    try:
        return get_all_grades()
    except Exception as e:
        return []

with st.spinner("Loading grade data..."):
    grades = load_grades()

if st.button("🔄 Refresh Data", key="dash_refresh"):
    st.cache_data.clear()
    grades = load_grades()
    st.rerun()

if not grades:
    st.info("📭 No grade records yet. Go to **Add Grade** to get started!")
    st.stop()

df = pd.DataFrame(grades)


total_records  = len(df)
total_students = df["student_name"].nunique()
avg_percentage = round(df["percentage"].mean(), 1)
pass_count     = len(df[df["grade_letter"] != "F"])
fail_count     = total_records - pass_count
pass_rate      = round((pass_count / total_records) * 100, 1) if total_records else 0

col1, col2, col3, col4, col5 = st.columns(5)

kpis = [
    (col1, "[TOTAL_RECORS]", str(total_records),   "Total Records"),
    (col2, "[TOTAL_STUDENTS]", str(total_students),  "Students"),
    (col3, "[AVG_%]", f"{avg_percentage}%", "Avg Percentage"),
    (col4, "PASS", str(pass_count),      "Passing"),
    (col5, "FAIL", str(fail_count),      "Failing"),
]

for col, icon, value, label in kpis:
    with col:
        st.markdown(
            f"""
            <div class="metric-card">
              <div class="metric-icon">{icon}</div>
              <div class="metric-value">{value}</div>
              <div class="metric-label">{label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("---")


chart_col1, chart_col2 = st.columns(2)

CHART_COLORS = {
    "primary": "#4F46E5",
    "secondary": "#0EA5E9",
    "palette": ["#4F46E5", "#0EA5E9", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899"],
}

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#1E293B"),
    margin=dict(t=40, b=20, l=20, r=20),
)

with chart_col1:
    st.markdown(
        "<div class='neu-card'><h3 style='margin-top:0;color:#1E293B;font-size:1rem;'>📚 Avg % by Subject</h3>",
        unsafe_allow_html=True,
    )
    subj_avg = df.groupby("subject")["percentage"].mean().reset_index().sort_values("percentage", ascending=True)
    fig1 = px.bar(
        subj_avg,
        x="percentage",
        y="subject",
        orientation="h",
        color="percentage",
        color_continuous_scale=["#B8C4D4", "#4F46E5"],
        labels={"percentage": "Avg %", "subject": ""},
        text=subj_avg["percentage"].round(1).astype(str) + "%",
    )
    fig1.update_traces(textposition="outside", marker_line_width=0)
    fig1.update_layout(**PLOT_LAYOUT, coloraxis_showscale=False, height=320)
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with chart_col2:
    st.markdown(
        "<div class='neu-card'><h3 style='margin-top:0;color:#1E293B;font-size:1rem;'>🏅 Grade Distribution</h3>",
        unsafe_allow_html=True,
    )
    grade_counts = df["grade_letter"].value_counts().reset_index()
    grade_counts.columns = ["Grade", "Count"]
    fig2 = px.pie(
        grade_counts,
        names="Grade",
        values="Count",
        color_discrete_sequence=CHART_COLORS["palette"],
        hole=0.45,
    )
    fig2.update_traces(textposition="inside", textinfo="percent+label")
    fig2.update_layout(**PLOT_LAYOUT, height=320, showlegend=True)
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Row 2
chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    st.markdown(
        "<div class='neu-card'><h3 style='margin-top:0;color:#1E293B;font-size:1rem;'> Records by Semester</h3>",
        unsafe_allow_html=True,
    )
    sem_counts = df["semester"].value_counts().reset_index()
    sem_counts.columns = ["Semester", "Records"]
    fig3 = px.bar(
        sem_counts,
        x="Semester",
        y="Records",
        color="Records",
        color_continuous_scale=["#E8EEF6", "#0EA5E9"],
        text="Records",
    )
    fig3.update_traces(textposition="outside", marker_line_width=0)
    fig3.update_layout(**PLOT_LAYOUT, coloraxis_showscale=False, height=300)
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with chart_col4:
    st.markdown(
        "<div class='neu-card'><h3 style='margin-top:0;color:#1E293B;font-size:1rem;'>✅ Pass vs Fail</h3>",
        unsafe_allow_html=True,
    )
    fig4 = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=pass_rate,
        number={"suffix": "%", "font": {"size": 40, "color": "#4F46E5"}},
        delta={"reference": 75, "valueformat": ".1f"},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#64748B"},
            "bar":  {"color": "#4F46E5"},
            "bgcolor": "#E8EEF6",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 50],  "color": "rgba(239,68,68,0.15)"},
                {"range": [50, 75], "color": "rgba(245,158,11,0.15)"},
                {"range": [75, 100],"color": "rgba(16,185,129,0.15)"},
            ],
            "threshold": {
                "line": {"color": "#10B981", "width": 3},
                "thickness": 0.75,
                "value": 75,
            },
        },
        title={"text": "Pass Rate", "font": {"size": 14, "color": "#64748B"}},
    ))
    fig4.update_layout(**PLOT_LAYOUT, height=300)
    st.plotly_chart(fig4, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


st.markdown("---")
st.markdown("### 🏆 Top 5 Performers")
top5 = df.nlargest(5, "percentage")[
    ["student_name", "roll_number", "subject", "percentage", "grade_letter"]
].reset_index(drop=True)
top5.index += 1
st.dataframe(top5, use_container_width=True)

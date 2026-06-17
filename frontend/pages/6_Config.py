"""
Grade Config Page — Set custom A/B/C thresholds + pass/fail rules
"""
import streamlit as st
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.api_client import get_grading_config, create_grading_config, delete_grading_config

# ── CSS ────────────────────────────────────────────────────────────
css_path = Path(__file__).parent.parent / "styles" / "neumorphic.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("# ⚙️ Grade Configuration")
st.markdown(
    "<p style='color:#64748B;margin-top:-0.5rem;'>"
    "Define your custom grading scale — thresholds and pass/fail rules</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ── DEFAULT SCALE INFO ─────────────────────────────────────────────
with st.expander("ℹ️ Default Grading Scale (used when no config set)", expanded=False):
    default_df = pd.DataFrame([
        {"Grade": "A+", "Min %": 95, "Max %": 100, "Passing": "✅ Yes"},
        {"Grade": "A",  "Min %": 90, "Max %": 94,  "Passing": "✅ Yes"},
        {"Grade": "B+", "Min %": 85, "Max %": 89,  "Passing": "✅ Yes"},
        {"Grade": "B",  "Min %": 75, "Max %": 84,  "Passing": "✅ Yes"},
        {"Grade": "C+", "Min %": 65, "Max %": 74,  "Passing": "✅ Yes"},
        {"Grade": "C",  "Min %": 60, "Max %": 64,  "Passing": "✅ Yes"},
        {"Grade": "D",  "Min %": 50, "Max %": 59,  "Passing": "✅ Yes"},
        {"Grade": "F",  "Min %": 0,  "Max %": 49,  "Passing": "❌ No"},
    ])
    st.dataframe(default_df, hide_index=True, use_container_width=True)
    st.caption("These are used automatically if your config table is empty.")

st.markdown("---")

# ── CURRENT CONFIG ─────────────────────────────────────────────────
st.markdown("### 📋 Current Grading Config")

@st.cache_data(ttl=30)
def _load_config():
    return get_grading_config()

if st.button("🔄 Refresh Config", key="cfg_refresh"):
    st.cache_data.clear()

try:
    configs = _load_config()
except Exception as e:
    st.error(f"❌ Could not load config: {e}")
    configs = []

if configs:
    cfg_df = pd.DataFrame(configs)
    cfg_df["Passing"] = cfg_df["is_passing"].apply(lambda x: "✅ Yes" if x else "❌ No")

    # Display table with delete buttons
    header_cols = st.columns([1, 2, 2, 2, 2, 1])
    for col, head in zip(header_cols, ["ID", "Label", "Min %", "Max %", "Passing", "Delete"]):
        col.markdown(f"<b style='color:#64748B;font-size:0.8rem;'>{head}</b>", unsafe_allow_html=True)

    st.markdown("<hr style='margin:0.3rem 0;'>", unsafe_allow_html=True)

    for _, row in cfg_df.iterrows():
        c1, c2, c3, c4, c5, c6 = st.columns([1, 2, 2, 2, 2, 1])
        c1.markdown(f"<span style='color:#94A3B8;font-size:0.85rem;'>#{row['id']}</span>", unsafe_allow_html=True)
        c2.markdown(
            f"<span style='background:rgba(79,70,229,0.1);color:#4F46E5;font-weight:700;"
            f"padding:0.15rem 0.6rem;border-radius:12px;font-size:0.9rem;'>{row['label']}</span>",
            unsafe_allow_html=True,
        )
        c3.markdown(f"<span style='font-size:0.88rem;'>{row['min_percentage']}%</span>", unsafe_allow_html=True)
        c4.markdown(f"<span style='font-size:0.88rem;'>{row['max_percentage']}%</span>", unsafe_allow_html=True)
        c5.markdown(f"<span style='font-size:0.88rem;'>{row['Passing']}</span>", unsafe_allow_html=True)
        if c6.button("🗑️", key=f"del_cfg_{row['id']}", help=f"Delete {row['label']}"):
            try:
                delete_grading_config(int(row["id"]))
                st.success(f"✅ Deleted grade '{row['label']}'")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"❌ {e}")
else:
    st.info(
        "📭 No custom config set. The default grading scale (A+/A/B+/B/C+/C/D/F) is being used."
    )

st.markdown("---")

# ── ADD NEW CONFIG ─────────────────────────────────────────────────
st.markdown("### ➕ Add New Grade Threshold")
st.markdown(
    "<p style='color:#64748B;font-size:0.85rem;margin-top:-0.3rem;'>"
    "Adding any custom config disables the default scale for all future grades.</p>",
    unsafe_allow_html=True,
)

with st.form("add_config_form", clear_on_submit=True):
    cc1, cc2, cc3, cc4 = st.columns([2, 2, 2, 2])
    with cc1:
        label = st.text_input("Grade Label *", placeholder="e.g. A, B+, F")
    with cc2:
        min_pct = st.number_input("Min Percentage *", min_value=0.0, max_value=100.0, value=90.0, step=0.5)
    with cc3:
        max_pct = st.number_input("Max Percentage *", min_value=0.0, max_value=100.0, value=100.0, step=0.5)
    with cc4:
        is_passing = st.toggle("Is Passing?", value=True)

    if st.form_submit_button("💾 Add Grade Threshold", use_container_width=True):
        if not label.strip():
            st.error("❌ Label is required.")
        elif min_pct >= max_pct:
            st.error("❌ Min percentage must be less than Max percentage.")
        else:
            try:
                res = create_grading_config({
                    "label": label.strip().upper(),
                    "min_percentage": min_pct,
                    "max_percentage": max_pct,
                    "is_passing": is_passing,
                })
                st.success(
                    f"✅ Added: **{res['label']}** ({res['min_percentage']}% – {res['max_percentage']}%) "
                    f"| {'Passing' if res['is_passing'] else 'Failing'}"
                )
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"❌ {e}")

# ── QUICK SETUP PRESETS ────────────────────────────────────────────
st.markdown("---")
st.markdown("### ⚡ Quick Setup Presets")
st.markdown(
    "<p style='color:#64748B;font-size:0.85rem;'>Add a full standard grading scale in one click.</p>",
    unsafe_allow_html=True,
)

PRESETS = {
    "🎓 Standard (A+ to F)": [
        {"label": "A+", "min_percentage": 95.0,  "max_percentage": 100.0, "is_passing": True},
        {"label": "A",  "min_percentage": 90.0,  "max_percentage": 94.99, "is_passing": True},
        {"label": "B+", "min_percentage": 85.0,  "max_percentage": 89.99, "is_passing": True},
        {"label": "B",  "min_percentage": 75.0,  "max_percentage": 84.99, "is_passing": True},
        {"label": "C+", "min_percentage": 65.0,  "max_percentage": 74.99, "is_passing": True},
        {"label": "C",  "min_percentage": 60.0,  "max_percentage": 64.99, "is_passing": True},
        {"label": "D",  "min_percentage": 50.0,  "max_percentage": 59.99, "is_passing": True},
        {"label": "F",  "min_percentage": 0.0,   "max_percentage": 49.99, "is_passing": False},
    ],
    "📊 Simple (A/B/C/F)": [
        {"label": "A", "min_percentage": 80.0, "max_percentage": 100.0, "is_passing": True},
        {"label": "B", "min_percentage": 65.0, "max_percentage": 79.99, "is_passing": True},
        {"label": "C", "min_percentage": 50.0, "max_percentage": 64.99, "is_passing": True},
        {"label": "F", "min_percentage": 0.0,  "max_percentage": 49.99, "is_passing": False},
    ],
}

p1, p2 = st.columns(2)
for col, (preset_name, preset_entries) in zip([p1, p2], PRESETS.items()):
    with col:
        if st.button(preset_name, use_container_width=True, key=f"preset_{preset_name}"):
            success_count = 0
            for entry in preset_entries:
                try:
                    create_grading_config(entry)
                    success_count += 1
                except Exception:
                    pass
            st.success(f"✅ Added {success_count} grade thresholds!")
            st.cache_data.clear()
            st.rerun()

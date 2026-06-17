"""
Export Page — Download all grade data as CSV, Excel, or JSON
"""
import streamlit as st
import json
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.api_client import export_grades_csv, export_grades_excel, export_grades_json

# ── CSS ────────────────────────────────────────────────────────────
css_path = Path(__file__).parent.parent / "styles" / "neumorphic.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("# 📤 Export Data")
st.markdown(
    "<p style='color:#64748B;margin-top:-0.5rem;'>"
    "Download all grade records in your preferred format</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ── FORMAT CARDS ───────────────────────────────────────────────────
st.markdown("### Choose Export Format")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="metric-card" style="text-align:left;">
          <div style="font-size:2rem;">📄</div>
          <div style="font-weight:700;font-size:1rem;color:#1E293B;margin:0.3rem 0;">CSV</div>
          <div style="font-size:0.8rem;color:#64748B;">Universal format. Works in Excel, Google Sheets, and any data tool.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("⬇️ Download CSV", key="dl_csv", use_container_width=True):
        with st.spinner("Preparing CSV..."):
            try:
                csv_data = export_grades_csv()
                st.download_button(
                    label="📥 Click to Save CSV",
                    data=csv_data,
                    file_name="gradepulse_grades.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"❌ {e}")

with col2:
    st.markdown(
        """
        <div class="metric-card" style="text-align:left;">
          <div style="font-size:2rem;">📊</div>
          <div style="font-weight:700;font-size:1rem;color:#1E293B;margin:0.3rem 0;">Excel</div>
          <div style="font-size:0.8rem;color:#64748B;">Native .xlsx format for Microsoft Excel with full formatting support.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("⬇️ Download Excel", key="dl_excel", use_container_width=True):
        with st.spinner("Preparing Excel file..."):
            try:
                excel_data = export_grades_excel()
                st.download_button(
                    label="📥 Click to Save Excel",
                    data=excel_data,
                    file_name="gradepulse_grades.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"❌ {e}")

with col3:
    st.markdown(
        """
        <div class="metric-card" style="text-align:left;">
          <div style="font-size:2rem;">🔵</div>
          <div style="font-weight:700;font-size:1rem;color:#1E293B;margin:0.3rem 0;">JSON</div>
          <div style="font-size:0.8rem;color:#64748B;">Structured JSON for developers and API integrations.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("⬇️ Download JSON", key="dl_json", use_container_width=True):
        with st.spinner("Preparing JSON..."):
            try:
                json_data = export_grades_json()
                json_str  = json.dumps(json_data, indent=2).encode("utf-8")
                st.download_button(
                    label="📥 Click to Save JSON",
                    data=json_str,
                    file_name="gradepulse_grades.json",
                    mime="application/json",
                    use_container_width=True,
                )
                st.info(f"📊 {json_data.get('total', 0)} records ready for download.")
            except Exception as e:
                st.error(f"❌ {e}")

st.markdown("---")

# ── DATA PREVIEW ───────────────────────────────────────────────────
st.markdown("### 👁️ Data Preview")
st.markdown(
    "<p style='color:#64748B;font-size:0.85rem;'>Preview your data before downloading.</p>",
    unsafe_allow_html=True,
)

if st.button("🔍 Load Preview", key="preview_btn"):
    with st.spinner("Loading data..."):
        try:
            json_data = export_grades_json()
            records   = json_data.get("data", [])

            if not records:
                st.info("📭 No grade records to preview.")
            else:
                df = pd.DataFrame(records)
                st.markdown(
                    f"<div style='color:#64748B;font-size:0.85rem;margin-bottom:0.5rem;'>"
                    f"📊 <b>{len(df)}</b> records · <b>{len(df.columns)}</b> columns</div>",
                    unsafe_allow_html=True,
                )
                st.dataframe(df, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"❌ Could not load preview: {e}")

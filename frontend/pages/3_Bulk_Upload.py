"""
Bulk Upload Page — CSV/Excel drag-and-drop upload with Pandas validation
"""
import streamlit as st
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.api_client import bulk_upload

# CSS 
css_path = Path(__file__).parent.parent / "styles" / "neumorphic.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("# 📁 Bulk Upload")
st.markdown(
    "<p style='color:#64748B;margin-top:-0.5rem;'>Upload CSV or Excel files to add multiple grade records at once</p>",
    unsafe_allow_html=True,
)
st.markdown("---")


with st.expander("📋 Required File Format", expanded=False):
    st.markdown("""
    Your file **must** contain these columns (exact names, any order):

    | Column | Type | Notes |
    |--------|------|-------|
    | `student_name` | Text | Must not be empty |
    | `roll_number` | Text | Must not be empty |
    | `subject` | Text | |
    | `marks_obtained` | Number | Must be ≥ 0 |
    | `total_marks` | Number | Must be > 0 |
    | `semester` | Text | e.g. Spring 2024 |
    | `date` | Text/Date | e.g. 2024-01-15 |

    > `percentage` and `grade_letter` are **auto-computed** — do not include them.
    """)

    
    sample_data = pd.DataFrame([
        {"student_name": "Ali Hassan",    "roll_number": "CS-001", "subject": "Math",    "marks_obtained": 85, "total_marks": 100, "semester": "Spring 2024", "date": "2024-01-15"},
        {"student_name": "Sara Ahmed",    "roll_number": "CS-002", "subject": "Physics", "marks_obtained": 72, "total_marks": 100, "semester": "Spring 2024", "date": "2024-01-15"},
        {"student_name": "Usman Malik",   "roll_number": "CS-003", "subject": "CS",      "marks_obtained": 90, "total_marks": 100, "semester": "Spring 2024", "date": "2024-01-15"},
    ])
    st.dataframe(sample_data, hide_index=True, use_container_width=True)
    csv_sample = sample_data.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Sample CSV",
        data=csv_sample,
        file_name="gradepulse_sample.csv",
        mime="text/csv",
    )

st.markdown("---")

# ── FILE UPLOADER ──────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "📂 Drop your CSV or Excel file here",
    type=["csv", "xlsx", "xls"],
    help="Accepted: .csv, .xlsx, .xls",
)

if uploaded_file:
    file_bytes = uploaded_file.read()
    filename   = uploaded_file.name

    # Preview
    st.markdown("### 👁️ File Preview")
    try:
        if filename.endswith(".csv"):
            preview_df = pd.read_csv(pd.io.common.BytesIO(file_bytes))
        else:
            preview_df = pd.read_excel(pd.io.common.BytesIO(file_bytes))

        st.markdown(
            f"<div style='color:#64748B;font-size:0.85rem;margin-bottom:0.5rem;'>"
            f"📄 <b>{filename}</b> — {len(preview_df)} rows × {len(preview_df.columns)} columns</div>",
            unsafe_allow_html=True,
        )
        st.dataframe(preview_df.head(10), use_container_width=True, hide_index=True)
        if len(preview_df) > 10:
            st.caption(f"Showing first 10 of {len(preview_df)} rows.")
    except Exception as e:
        st.error(f"❌ Could not preview file: {e}")

    st.markdown("---")

    # Upload button
    if st.button("🚀 Upload & Process", use_container_width=True, type="primary"):
        with st.spinner("⏳ Validating and uploading data..."):
            try:
                result = bulk_upload(file_bytes, filename)

                # Summary cards
                r1, r2, r3 = st.columns(3)
                with r1:
                    st.markdown(
                        f"""<div class="metric-card">
                          <div class="metric-icon">✅</div>
                          <div class="metric-value" style="color:#10B981;">{result['rows_added']}</div>
                          <div class="metric-label">Rows Added</div>
                        </div>""",
                        unsafe_allow_html=True,
                    )
                with r2:
                    st.markdown(
                        f"""<div class="metric-card">
                          <div class="metric-icon">⏭️</div>
                          <div class="metric-value" style="color:#F59E0B;">{result['rows_skipped']}</div>
                          <div class="metric-label">Rows Skipped</div>
                        </div>""",
                        unsafe_allow_html=True,
                    )
                with r3:
                    st.markdown(
                        f"""<div class="metric-card">
                          <div class="metric-icon">📊</div>
                          <div class="metric-value" style="color:#4F46E5;">{result['total_rows']}</div>
                          <div class="metric-label">Total Rows</div>
                        </div>""",
                        unsafe_allow_html=True,
                    )

                if result["rows_added"] > 0:
                    st.success(f"✅ Successfully added {result['rows_added']} grade record(s)!")

                # Error details
                if result["error_details"]:
                    st.markdown("---")
                    st.markdown(
                        f"<div style='color:#EF4444;font-weight:600;font-size:0.9rem;'>"
                        f"⚠️ {len(result['error_details'])} row(s) had issues:</div>",
                        unsafe_allow_html=True,
                    )
                    for err in result["error_details"]:
                        st.markdown(
                            f"<div style='background:rgba(239,68,68,0.08);border-left:3px solid #EF4444;"
                            f"border-radius:6px;padding:0.4rem 0.8rem;margin:0.25rem 0;"
                            f"font-size:0.82rem;color:#7F1D1D;'>{err}</div>",
                            unsafe_allow_html=True,
                        )
                st.cache_data.clear()

            except Exception as e:
                st.error(f"❌ Upload failed: {e}")


import streamlit as st
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.api_client import (
    get_all_grades, get_student_grades, create_grade, update_grade, delete_grade
)

# CSS 
css_path = Path(__file__).parent.parent / "styles" / "neumorphic.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("# ✏️ Grade Management")
st.markdown(
    "<p style='color:#64748B;margin-top:-0.5rem;'>Add, search, edit, and delete student grade records</p>",
    unsafe_allow_html=True,
)
st.markdown("---")


tab1, tab2, tab3 = st.tabs(["➕ Add Grade", "📋 All Grades", "🔍 Student Search"])

# ══════════════════════════════════════════════════════════════════
# TAB 1 — ADD GRADE
# ══════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### Add New Grade Record")
    st.markdown(
        "<p style='color:#64748B;font-size:0.85rem;'>"
        "Percentage and grade letter are computed automatically on the server.</p>",
        unsafe_allow_html=True,
    )

    with st.form("add_grade_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            student_name = st.text_input("👤 Student Name *", placeholder="e.g. Ali Hassan")
            subject      = st.text_input("📚 Subject *",      placeholder="e.g. Mathematics")
            marks_obtained = st.number_input("✅ Marks Obtained *", min_value=0.0, step=0.5, format="%.1f")
            semester     = st.text_input("📅 Semester *",     placeholder="e.g. Spring 2024")
        with c2:
            roll_number  = st.text_input("🎫 Roll Number *",  placeholder="e.g. CS-0267")
            date         = st.date_input("📆 Date *")
            total_marks  = st.number_input("📊 Total Marks *", min_value=1.0, value=100.0, step=0.5, format="%.1f")

        submitted = st.form_submit_button("💾 Save Grade", use_container_width=True)

        if submitted:
            if not all([student_name.strip(), roll_number.strip(), subject.strip(), semester.strip()]):
                st.error("❌ Please fill all required fields.")
            elif marks_obtained > total_marks:
                st.error("❌ Marks obtained cannot exceed total marks.")
            else:
                try:
                    result = create_grade({
                        "student_name":    student_name.strip(),
                        "roll_number":     roll_number.strip(),
                        "subject":         subject.strip(),
                        "marks_obtained":  marks_obtained,
                        "total_marks":     total_marks,
                        "semester":        semester.strip(),
                        "date":            str(date),
                    })
                    st.success(
                        f"✅ Grade saved! **{result['student_name']}** — "
                        f"{result['subject']} | {result['percentage']}% | {result['grade_letter']}"
                    )
                    st.cache_data.clear()
                except Exception as e:
                    st.error(f"❌ {e}")

# ══════════════════════════════════════════════════════════════════
# TAB 2 — ALL GRADES
# ══════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### All Grade Records")

    # Filters
    fc1, fc2, fc3 = st.columns([2, 2, 1])
    with fc1:
        search_name = st.text_input("🔍 Filter by name", placeholder="Student name...", key="filter_name")
    with fc2:
        filter_sem  = st.text_input("📅 Filter by semester", placeholder="e.g. Spring 2024", key="filter_sem")
    with fc3:
        if st.button("🔄 Refresh", key="refresh_all"):
            st.cache_data.clear()

    @st.cache_data(ttl=30)
    def _load():
        return get_all_grades()

    try:
        grades = _load()
    except Exception as e:
        st.error(f"❌ Could not load grades: {e}")
        grades = []

    if grades:
        df = pd.DataFrame(grades)

        # Apply filters
        if search_name:
            df = df[df["student_name"].str.contains(search_name, case=False, na=False)]
        if filter_sem:
            df = df[df["semester"].str.contains(filter_sem, case=False, na=False)]

        if df.empty:
            st.warning("No records match the filter.")
        else:
            st.markdown(f"Showing **{len(df)}** record(s)")

            # Display table
            display_df = df[["id", "student_name", "roll_number", "subject",
                             "marks_obtained", "total_marks", "percentage",
                             "grade_letter", "semester", "date"]].copy()
            st.dataframe(display_df, use_container_width=True, hide_index=True)

            # Edit / Delete Section
            st.markdown("---")
            st.markdown("#### ✏️ Edit or Delete a Record")
            ids = df["id"].tolist()
            selected_id = st.selectbox("Select Grade ID", ids, key="select_edit_id")

            if selected_id:
                row = df[df["id"] == selected_id].iloc[0]
                action = st.radio("Action", ["✏️ Edit", "🗑️ Delete"], horizontal=True, key="edit_action")

                if action == "✏️ Edit":
                    with st.form("edit_form"):
                        ec1, ec2 = st.columns(2)
                        with ec1:
                            e_name    = st.text_input("Student Name", value=row["student_name"])
                            e_subject = st.text_input("Subject",      value=row["subject"])
                            e_marks   = st.number_input("Marks Obtained", value=float(row["marks_obtained"]), min_value=0.0, format="%.1f")
                            e_sem     = st.text_input("Semester",     value=row["semester"])
                        with ec2:
                            e_roll    = st.text_input("Roll Number",  value=row["roll_number"])
                            e_date    = st.text_input("Date",         value=row["date"])
                            e_total   = st.number_input("Total Marks", value=float(row["total_marks"]), min_value=1.0, format="%.1f")

                        if st.form_submit_button("💾 Update Grade", use_container_width=True):
                            try:
                                res = update_grade(selected_id, {
                                    "student_name":   e_name,
                                    "roll_number":    e_roll,
                                    "subject":        e_subject,
                                    "marks_obtained": e_marks,
                                    "total_marks":    e_total,
                                    "semester":       e_sem,
                                    "date":           e_date,
                                })
                                st.success(
                                    f"✅ Updated! New percentage: {res['percentage']}% | {res['grade_letter']}"
                                )
                                st.cache_data.clear()
                            except Exception as e:
                                st.error(f"❌ {e}")

                elif action == "🗑️ Delete":
                    st.warning(
                        f"⚠️ You are about to delete: **{row['student_name']}** — "
                        f"{row['subject']} ({row['semester']})"
                    )
                    if st.button("🗑️ Confirm Delete", key="confirm_delete", type="primary"):
                        try:
                            delete_grade(selected_id)
                            st.success("✅ Grade deleted successfully.")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ {e}")
    else:
        st.info("📭 No grade records found. Add some grades first!")

# ══════════════════════════════════════════════════════════════════
# TAB 3 — STUDENT SEARCH BY ROLL NUMBER
# ══════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 🔍 Student Detail — Search by Roll Number")

    roll_input = st.text_input(
        "Enter Roll Number",
        placeholder="e.g. CS-0267",
        key="roll_search",
    )

    if st.button("🔎 Search Student", key="search_btn"):
        if not roll_input.strip():
            st.warning("Please enter a roll number.")
        else:
            try:
                student_grades = get_student_grades(roll_input.strip())
                sdf = pd.DataFrame(student_grades)

                student_name = sdf["student_name"].iloc[0]
                avg_pct      = round(sdf["percentage"].mean(), 1)
                best_subject = sdf.loc[sdf["percentage"].idxmax(), "subject"]

                # Student summary card
                st.markdown(
                    f"""
                    <div class="neu-card" style="border-left:4px solid #4F46E5;">
                      <div style="font-size:1.5rem;font-weight:800;color:#1E293B;">{student_name}</div>
                      <div style="color:#64748B;font-size:0.85rem;margin-top:0.2rem;">
                        Roll: <b>{roll_input.strip()}</b>
                      </div>
                      <div style="display:flex;gap:2rem;margin-top:1rem;">
                        <div>
                          <div style="font-size:1.4rem;font-weight:800;color:#4F46E5;">{avg_pct}%</div>
                          <div style="font-size:0.75rem;color:#94A3B8;text-transform:uppercase;letter-spacing:0.08em;">Avg Percentage</div>
                        </div>
                        <div>
                          <div style="font-size:1.4rem;font-weight:800;color:#10B981;">{len(sdf)}</div>
                          <div style="font-size:0.75rem;color:#94A3B8;text-transform:uppercase;letter-spacing:0.08em;">Subjects</div>
                        </div>
                        <div>
                          <div style="font-size:1.1rem;font-weight:700;color:#0EA5E9;">{best_subject}</div>
                          <div style="font-size:0.75rem;color:#94A3B8;text-transform:uppercase;letter-spacing:0.08em;">Best Subject</div>
                        </div>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown("#### 📋 All Grades")
                st.dataframe(
                    sdf[["subject", "marks_obtained", "total_marks",
                          "percentage", "grade_letter", "semester", "date"]],
                    use_container_width=True,
                    hide_index=True,
                )

            except Exception as e:
                st.error(f"❌ {e}")

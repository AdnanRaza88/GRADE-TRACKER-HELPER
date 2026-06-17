from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
from typing import Optional, List
import pandas as pd
import io

from database import create_db_and_tables, get_session
from models import Grade, GradingConfig
from schemas import (
    GradeCreate, GradeResponse, GradeUpdate, BulkUploadResult,
    GradingConfigCreate, GradingConfigResponse,
    StudyTipsResponse, RoutineRequest,
)
from grade_utils import compute_percentage, compute_grade_letter
from ai_features import get_study_tips, get_daily_routine


app = FastAPI(
    title="GradePulse API",
    description=(
        "## 🎓 GradePulse — Student Grade Tracker\n\n"
        "Full-stack academic performance tracker with:\n"
        "- CRUD grade management\n"
        "- CSV/Excel bulk upload\n"
        "- AI study tips (LangChain + Groq)\n"
        "- AI daily routine generation\n"
        "- Configurable grading scale\n"
        "- Export (CSV / Excel / JSON)"
    ),
    version="1.0.0",
    contact={"name": "Adnan", "email": "adnan@gradepulse.dev"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/", tags=["Health"])
def root():
    return {
        "message": "🎓 GradePulse API is live!",
        "docs": "/docs",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}



@app.get(
    "/grades/export",
    tags=["Export"],
    summary="Export all grade records as CSV, Excel, or JSON",
)
def export_grades(
    format: str = Query("csv", enum=["csv", "excel", "json"]),
    session: Session = Depends(get_session),
):
    grades = session.exec(select(Grade)).all()
    data = [g.model_dump() for g in grades]
    df = pd.DataFrame(data) if data else pd.DataFrame(
        columns=[
            "id", "student_name", "roll_number", "subject",
            "marks_obtained", "total_marks", "semester", "date",
            "percentage", "grade_letter",
        ]
    )

    if format == "json":
        return {"total": len(data), "data": data}

    elif format == "csv":
        buf = io.StringIO()
        df.to_csv(buf, index=False)
        buf.seek(0)
        return StreamingResponse(
            iter([buf.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=gradepulse_export.csv"},
        )

    else:  # excel
        buf = io.BytesIO()
        df.to_excel(buf, index=False)
        buf.seek(0)
        return StreamingResponse(
            iter([buf.getvalue()]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=gradepulse_export.xlsx"},
        )




@app.get(
    "/grades/student/{roll_number}",
    response_model=List[GradeResponse],
    tags=["Students"],
    summary="Get all grades for a specific student by roll number",
)
def get_student_grades(
    roll_number: str,
    session: Session = Depends(get_session),
):
    grades = session.exec(
        select(Grade).where(Grade.roll_number == roll_number)
    ).all()
    if not grades:
        raise HTTPException(
            status_code=404,
            detail=f"No grades found for roll number '{roll_number}'",
        )
    return grades




@app.get(
    "/grades/config",
    response_model=List[GradingConfigResponse],
    tags=["Grading Config"],
    summary="Get all grading configurations",
)
def get_grading_configs(session: Session = Depends(get_session)):
    return session.exec(select(GradingConfig)).all()


@app.post(
    "/grades/config",
    response_model=GradingConfigResponse,
    status_code=201,
    tags=["Grading Config"],
    summary="Create a grading threshold (e.g., A = 90–100)",
)
def create_grading_config(
    config_data: GradingConfigCreate,
    session: Session = Depends(get_session),
):
    db_config = GradingConfig(**config_data.model_dump())
    session.add(db_config)
    session.commit()
    session.refresh(db_config)
    return db_config


@app.delete(
    "/grades/config/{config_id}",
    tags=["Grading Config"],
    summary="Delete a grading config entry by ID",
)
def delete_grading_config(
    config_id: int,
    session: Session = Depends(get_session),
):
    config = session.get(GradingConfig, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Config entry not found")
    session.delete(config)
    session.commit()
    return {"message": f"Config '{config.label}' deleted successfully"}




@app.post(
    "/grades/bulk-upload",
    response_model=BulkUploadResult,
    tags=["Grades"],
    summary="Bulk upload grades via CSV or Excel file",
)
async def bulk_upload_grades(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    
    filename = file.filename or ""
    if not (filename.endswith(".csv") or filename.endswith(".xlsx") or filename.endswith(".xls")):
        raise HTTPException(
            status_code=400,
            detail="Only .csv, .xlsx, and .xls files are accepted",
        )

    content = await file.read()

    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
        else:
            df = pd.read_excel(io.BytesIO(content))
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Could not parse file: {exc}",
        )

    
    required_cols = [
        "student_name", "roll_number", "subject",
        "marks_obtained", "total_marks", "semester", "date",
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"Missing required columns: {', '.join(missing)}",
        )

    rows_added = 0
    rows_skipped = 0
    errors: List[str] = []
    total_rows = len(df)

    for idx, row in df.iterrows():
        row_num = int(idx) + 2  

        
        if pd.isna(row["student_name"]) or str(row["student_name"]).strip() == "":
            errors.append(f"Row {row_num}: Empty student_name — skipped")
            rows_skipped += 1
            continue

        if pd.isna(row["roll_number"]) or str(row["roll_number"]).strip() == "":
            errors.append(f"Row {row_num}: Empty roll_number — skipped")
            rows_skipped += 1
            continue

        
        try:
            marks_obtained = float(row["marks_obtained"])
            total_marks = float(row["total_marks"])
        except (ValueError, TypeError):
            errors.append(
                f"Row {row_num}: marks_obtained or total_marks is not numeric — skipped"
            )
            rows_skipped += 1
            continue

        if total_marks <= 0:
            errors.append(f"Row {row_num}: total_marks must be > 0 — skipped")
            rows_skipped += 1
            continue

        if marks_obtained < 0:
            errors.append(f"Row {row_num}: marks_obtained cannot be negative — skipped")
            rows_skipped += 1
            continue

        
        if marks_obtained > total_marks:
            errors.append(
                f"Row {row_num}: marks_obtained ({marks_obtained}) > "
                f"total_marks ({total_marks}) — skipped"
            )
            rows_skipped += 1
            continue

        
        percentage = compute_percentage(marks_obtained, total_marks)
        grade_letter = compute_grade_letter(percentage, session)

        grade = Grade(
            student_name=str(row["student_name"]).strip(),
            roll_number=str(row["roll_number"]).strip(),
            subject=str(row["subject"]).strip(),
            marks_obtained=marks_obtained,
            total_marks=total_marks,
            semester=str(row["semester"]).strip(),
            date=str(row["date"]).strip(),
            percentage=percentage,
            grade_letter=grade_letter,
        )
        session.add(grade)
        rows_added += 1

    session.commit()

    return BulkUploadResult(
        rows_added=rows_added,
        rows_skipped=rows_skipped,
        total_rows=total_rows,
        error_details=errors,
    )



@app.post(
    "/grades",
    response_model=GradeResponse,
    status_code=201,
    tags=["Grades"],
    summary="Create a single grade record",
)
def create_grade(
    grade_data: GradeCreate,
    session: Session = Depends(get_session),
):
    percentage = compute_percentage(grade_data.marks_obtained, grade_data.total_marks)
    grade_letter = compute_grade_letter(percentage, session)

    grade = Grade(
        **grade_data.model_dump(),
        percentage=percentage,
        grade_letter=grade_letter,
    )
    session.add(grade)
    session.commit()
    session.refresh(grade)
    return grade


@app.get(
    "/grades",
    response_model=List[GradeResponse],
    tags=["Grades"],
    summary="List all grade records (optionally filter by semester)",
)
def list_grades(
    semester: Optional[str] = Query(None, description="Filter by semester"),
    subject: Optional[str] = Query(None, description="Filter by subject"),
    session: Session = Depends(get_session),
):
    query = select(Grade)
    if semester:
        query = query.where(Grade.semester == semester)
    if subject:
        query = query.where(Grade.subject == subject)
    return session.exec(query).all()


@app.get(
    "/grades/{grade_id}",
    response_model=GradeResponse,
    tags=["Grades"],
    summary="Get a single grade record by ID",
)
def get_grade(grade_id: int, session: Session = Depends(get_session)):
    grade = session.get(Grade, grade_id)
    if not grade:
        raise HTTPException(status_code=404, detail=f"Grade with id={grade_id} not found")
    return grade


@app.put(
    "/grades/{grade_id}",
    response_model=GradeResponse,
    tags=["Grades"],
    summary="Update a grade record (percentage & grade_letter auto-recomputed)",
)
def update_grade(
    grade_id: int,
    grade_data: GradeUpdate,
    session: Session = Depends(get_session),
):
    grade = session.get(Grade, grade_id)
    if not grade:
        raise HTTPException(status_code=404, detail=f"Grade with id={grade_id} not found")

    update_fields = grade_data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(grade, field, value)

    # Always recompute after any update
    grade.percentage = compute_percentage(grade.marks_obtained, grade.total_marks)
    grade.grade_letter = compute_grade_letter(grade.percentage, session)

    session.add(grade)
    session.commit()
    session.refresh(grade)
    return grade


@app.delete(
    "/grades/{grade_id}",
    tags=["Grades"],
    summary="Delete a grade record by ID",
)
def delete_grade(grade_id: int, session: Session = Depends(get_session)):
    grade = session.get(Grade, grade_id)
    if not grade:
        raise HTTPException(status_code=404, detail=f"Grade with id={grade_id} not found")
    session.delete(grade)
    session.commit()
    return {"message": f"Grade id={grade_id} deleted successfully"}



#  AI ENDPOINTS


@app.post(
    "/grades/{grade_id}/study-tips",
    response_model=StudyTipsResponse,
    tags=["AI Features"],
    summary="Generate AI-powered personalised study tips for a grade record",
)
def grade_study_tips(grade_id: int, session: Session = Depends(get_session)):
    grade = session.get(Grade, grade_id)
    if not grade:
        raise HTTPException(status_code=404, detail=f"Grade with id={grade_id} not found")

    try:
        tips = get_study_tips(
            student_name=grade.student_name,
            subject=grade.subject,
            marks_obtained=grade.marks_obtained,
            total_marks=grade.total_marks,
            percentage=grade.percentage,
            grade_letter=grade.grade_letter,
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"AI service error: {exc}")

    return StudyTipsResponse(
        student_name=grade.student_name,
        subject=grade.subject,
        percentage=grade.percentage,
        grade_letter=grade.grade_letter,
        tips=tips,
    )


@app.post(
    "/grades/{grade_id}/routine",
    tags=["AI Features"],
    summary="Generate a full AI daily study routine based on student inputs",
)
def grade_daily_routine(
    grade_id: int,
    routine_req: RoutineRequest,
    session: Session = Depends(get_session),
):
    grade = session.get(Grade, grade_id)
    if not grade:
        raise HTTPException(status_code=404, detail=f"Grade with id={grade_id} not found")

    try:
        routine = get_daily_routine(
            free_hours=routine_req.free_hours,
            weak_subject=routine_req.weak_subject,
            physical_activity=routine_req.physical_activity,
            sleep_hours=routine_req.sleep_hours,
            water_intake=routine_req.water_intake,
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"AI service error: {exc}")

    return {
        "grade_id": grade_id,
        "student_name": grade.student_name,
        "subject": grade.subject,
        "routine": routine,
    }

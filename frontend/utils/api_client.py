
import os
import requests
from typing import Optional

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "https://grade-tracker-helper-production.up.railway.app").rstrip("/")
TIMEOUT = 30  


def _handle_response(response: requests.Response) -> dict | list:
    """Raise a user-friendly error for non-2xx responses."""
    if response.status_code >= 400:
        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text
        raise ValueError(f"API Error {response.status_code}: {detail}")
    return response.json()




def health_check() -> bool:
    try:
        r = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return r.status_code == 200
    except Exception:
        return False




def get_all_grades(semester: Optional[str] = None, subject: Optional[str] = None) -> list:
    params = {}
    if semester:
        params["semester"] = semester
    if subject:
        params["subject"] = subject
    r = requests.get(f"{API_BASE_URL}/grades", params=params, timeout=TIMEOUT)
    return _handle_response(r)


def get_grade(grade_id: int) -> dict:
    r = requests.get(f"{API_BASE_URL}/grades/{grade_id}", timeout=TIMEOUT)
    return _handle_response(r)


def create_grade(payload: dict) -> dict:
    r = requests.post(f"{API_BASE_URL}/grades", json=payload, timeout=TIMEOUT)
    return _handle_response(r)


def update_grade(grade_id: int, payload: dict) -> dict:
    r = requests.put(f"{API_BASE_URL}/grades/{grade_id}", json=payload, timeout=TIMEOUT)
    return _handle_response(r)


def delete_grade(grade_id: int) -> dict:
    r = requests.delete(f"{API_BASE_URL}/grades/{grade_id}", timeout=TIMEOUT)
    return _handle_response(r)




def get_student_grades(roll_number: str) -> list:
    r = requests.get(
        f"{API_BASE_URL}/grades/student/{roll_number}", timeout=TIMEOUT
    )
    return _handle_response(r)




def bulk_upload(file_bytes: bytes, filename: str) -> dict:
    ext = filename.rsplit(".", 1)[-1].lower()
    mime = "text/csv" if ext == "csv" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    r = requests.post(
        f"{API_BASE_URL}/grades/bulk-upload",
        files={"file": (filename, file_bytes, mime)},
        timeout=TIMEOUT,
    )
    return _handle_response(r)




def get_study_tips(grade_id: int) -> dict:
    r = requests.post(
        f"{API_BASE_URL}/grades/{grade_id}/study-tips", timeout=60
    )
    return _handle_response(r)


def get_routine(grade_id: int, payload: dict) -> dict:
    r = requests.post(
        f"{API_BASE_URL}/grades/{grade_id}/routine",
        json=payload,
        timeout=60,
    )
    return _handle_response(r)




def get_grading_config() -> list:
    r = requests.get(f"{API_BASE_URL}/grades/config", timeout=TIMEOUT)
    return _handle_response(r)


def create_grading_config(payload: dict) -> dict:
    r = requests.post(
        f"{API_BASE_URL}/grades/config", json=payload, timeout=TIMEOUT
    )
    return _handle_response(r)


def delete_grading_config(config_id: int) -> dict:
    r = requests.delete(
        f"{API_BASE_URL}/grades/config/{config_id}", timeout=TIMEOUT
    )
    return _handle_response(r)




def export_grades_csv() -> bytes:
    r = requests.get(
        f"{API_BASE_URL}/grades/export", params={"format": "csv"}, timeout=TIMEOUT
    )
    if r.status_code >= 400:
        raise ValueError(f"Export failed: {r.text}")
    return r.content


def export_grades_excel() -> bytes:
    r = requests.get(
        f"{API_BASE_URL}/grades/export", params={"format": "excel"}, timeout=TIMEOUT
    )
    if r.status_code >= 400:
        raise ValueError(f"Export failed: {r.text}")
    return r.content


def export_grades_json() -> dict:
    r = requests.get(
        f"{API_BASE_URL}/grades/export", params={"format": "json"}, timeout=TIMEOUT
    )
    return _handle_response(r)

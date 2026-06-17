from sqlmodel import SQLModel, Field
from typing import Optional


class Grade(SQLModel, table=True):
    """Main grade record table."""
    id: Optional[int] = Field(default=None, primary_key=True)
    student_name: str = Field(index=True)
    roll_number: str = Field(index=True)
    subject: str
    marks_obtained: float
    total_marks: float
    semester: str
    date: str
    percentage: float = Field(default=0.0)
    grade_letter: str = Field(default="")


class GradingConfig(SQLModel, table=True):
    """User-defined grading thresholds table."""
    id: Optional[int] = Field(default=None, primary_key=True)
    label: str          # e.g., "A", "B+", "F"
    min_percentage: float
    max_percentage: float
    is_passing: bool = Field(default=True)

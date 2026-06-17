from pydantic import BaseModel, field_validator, model_validator
from typing import Optional, List, Any


# GRADE SCHEMAS 

class GradeCreate(BaseModel):
    student_name: str
    roll_number: str
    subject: str
    marks_obtained: float
    total_marks: float
    semester: str
    date: str

    @field_validator("student_name", "roll_number", "subject", "semester", "date")
    @classmethod
    def must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field must not be empty")
        return v.strip()

    @field_validator("total_marks")
    @classmethod
    def total_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("total_marks must be greater than 0")
        return v

    @field_validator("marks_obtained")
    @classmethod
    def marks_must_be_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("marks_obtained must be non-negative")
        return v

    @model_validator(mode="after")
    def marks_not_exceed_total(self) -> "GradeCreate":
        if self.marks_obtained > self.total_marks:
            raise ValueError("marks_obtained cannot exceed total_marks")
        return self


class GradeResponse(BaseModel):
    id: int
    student_name: str
    roll_number: str
    subject: str
    marks_obtained: float
    total_marks: float
    semester: str
    date: str
    percentage: float
    grade_letter: str

    model_config = {"from_attributes": True}


class GradeUpdate(BaseModel):
    student_name: Optional[str] = None
    roll_number: Optional[str] = None
    subject: Optional[str] = None
    marks_obtained: Optional[float] = None
    total_marks: Optional[float] = None
    semester: Optional[str] = None
    date: Optional[str] = None


#  BULK UPLOAD 

class BulkUploadResult(BaseModel):
    rows_added: int
    rows_skipped: int
    total_rows: int
    error_details: List[str]


#  GRADING CONFIG 

class GradingConfigCreate(BaseModel):
    label: str
    min_percentage: float
    max_percentage: float
    is_passing: bool = True

    @field_validator("label")
    @classmethod
    def label_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Label must not be empty")
        return v.strip().upper()

    @model_validator(mode="after")
    def min_less_than_max(self) -> "GradingConfigCreate":
        if self.min_percentage >= self.max_percentage:
            raise ValueError("min_percentage must be less than max_percentage")
        return self


class GradingConfigResponse(BaseModel):
    id: int
    label: str
    min_percentage: float
    max_percentage: float
    is_passing: bool

    model_config = {"from_attributes": True}


# AI SCHEMAS 


class StudyTipsResponse(BaseModel):
    student_name: str
    subject: str
    percentage: float
    grade_letter: str
    tips: str


class RoutineRequest(BaseModel):
    free_hours: float
    weak_subject: str
    physical_activity: bool
    sleep_hours: float
    water_intake: str


class RoutineResponse(BaseModel):
    grade_id: int
    student_name: str
    routine: Any  

from sqlmodel import Session, select
from models import GradingConfig


DEFAULT_GRADES = [
    {"label": "A+", "min": 95.0,  "max": 100.0, "is_passing": True},
    {"label": "A",  "min": 90.0,  "max": 94.99, "is_passing": True},
    {"label": "B+", "min": 85.0,  "max": 89.99, "is_passing": True},
    {"label": "B",  "min": 75.0,  "max": 84.99, "is_passing": True},
    {"label": "C+", "min": 65.0,  "max": 74.99, "is_passing": True},
    {"label": "C",  "min": 60.0,  "max": 64.99, "is_passing": True},
    {"label": "D",  "min": 50.0,  "max": 59.99, "is_passing": True},
    {"label": "F",  "min": 0.0,   "max": 49.99, "is_passing": False},
]


def compute_percentage(marks_obtained: float, total_marks: float) -> float:
    """Compute percentage from marks. Returns 0.0 if total_marks is 0."""
    if total_marks == 0:
        return 0.0
    return round((marks_obtained / total_marks) * 100, 2)


def compute_grade_letter(percentage: float, session: Session) -> str:
    """
    Assign grade letter based on GradingConfig table.
    Falls back to DEFAULT_GRADES if config table is empty.
    """
    configs = session.exec(select(GradingConfig)).all()

    if configs:
        # Sort descending by min_percentage to match highest grade first
        sorted_configs = sorted(configs, key=lambda x: x.min_percentage, reverse=True)
        for config in sorted_configs:
            if config.min_percentage <= percentage <= config.max_percentage:
                return config.label
        return "N/A"

    # Use default scale
    for grade in DEFAULT_GRADES:
        if grade["min"] <= percentage <= grade["max"]:
            return grade["label"]

    return "F"


def is_passing_grade(grade_letter: str, session: Session) -> bool:
    """Check if a grade letter is considered passing per config."""
    configs = session.exec(select(GradingConfig)).all()

    if configs:
        for config in configs:
            if config.label.upper() == grade_letter.upper():
                return config.is_passing
        return False

    # Default: F is failing, everything else passes
    for grade in DEFAULT_GRADES:
        if grade["label"] == grade_letter:
            return grade["is_passing"]

    return False

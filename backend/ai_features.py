import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "llama-3.3-70b-versatile"


def _get_llm() -> ChatGroq:
    if not GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is not set. Please add it to your .env file."
        )
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model=MODEL_NAME,
        temperature=0.7,
        max_tokens=1024,
    )


# ─────────────────────────── STUDY TIPS CHAIN ─────────────────────────

STUDY_TIPS_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert academic advisor who delivers personalized, "
        "subject-specific, and motivational study advice. Be concise, "
        "practical, and encouraging. Always respond in English.",
    ),
    (
        "human",
        """A student named {student_name} scored {percentage:.1f}% """
        """({marks_obtained}/{total_marks}) in {subject}, earning a grade of {grade_letter}.

Provide exactly 5 specific, actionable study tips tailored to this student's """
        """performance level and the subject.

Use this exact format:

📚 **Personalized Study Tips for {student_name} — {subject}**
**Current Score:** {percentage:.1f}% | Grade: {grade_letter}

---

**💡 Tip 1 — [Short Title]**
[2-3 sentences of actionable, specific advice for this score level and subject]

**💡 Tip 2 — [Short Title]**
[2-3 sentences of actionable, specific advice]

**💡 Tip 3 — [Short Title]**
[2-3 sentences of actionable, specific advice]

**💡 Tip 4 — [Short Title]**
[2-3 sentences of actionable, specific advice]

**💡 Tip 5 — [Short Title]**
[2-3 sentences of actionable, specific advice]

---
✨ **Motivational Note:** [One encouraging closing sentence]""",
    ),
])


def get_study_tips(
    student_name: str,
    subject: str,
    marks_obtained: float,
    total_marks: float,
    percentage: float,
    grade_letter: str,
) -> str:
    """Run the study tips LangChain chain and return formatted string."""
    llm = _get_llm()
    chain = STUDY_TIPS_PROMPT | llm | StrOutputParser()

    return chain.invoke(
        {
            "student_name": student_name,
            "subject": subject,
            "marks_obtained": marks_obtained,
            "total_marks": total_marks,
            "percentage": percentage,
            "grade_letter": grade_letter,
        }
    )


# ─────────────────────────── DAILY ROUTINE CHAIN ──────────────────────

ROUTINE_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a productivity and academic wellness coach. "
        "You create structured, realistic, and healthy daily routines for students. "
        "Always respond with ONLY valid JSON — no markdown fences, no extra text.",
    ),
    (
        "human",
        """Create a complete daily study routine for a student with these details:
- Free hours available per day: {free_hours}
- Weakest / priority subject: {weak_subject}
- Physical activity: {activity_text}
- Nightly sleep hours: {sleep_hours}
- Water intake habit: {water_intake}

Return ONLY a valid JSON object with EXACTLY this structure (fill realistic values):
{{
  "morning": {{
    "time": "e.g. 6:00 AM – 7:30 AM",
    "activities": ["Wake up & freshen up", "Light breakfast", "5-min mindfulness"]
  }},
  "study_blocks": [
    {{
      "time": "e.g. 8:00 AM – 10:00 AM",
      "subject": "{weak_subject}",
      "technique": "Pomodoro 25+5",
      "goals": ["Complete chapter summary", "Solve 10 practice problems"]
    }},
    {{
      "time": "e.g. 11:00 AM – 12:30 PM",
      "subject": "Other subjects / revision",
      "technique": "Active recall",
      "goals": ["Review notes", "Flashcard drill"]
    }}
  ],
  "breaks": {{
    "duration": "5-10 min every 25-30 min",
    "activities": ["Stretch", "Walk around", "Hydrate"]
  }},
  "evening": {{
    "time": "e.g. 6:00 PM – 8:00 PM",
    "activities": ["Light review of day's topics", "Prepare tomorrow's plan", "Relax"]
  }},
  "sleep": {{
    "bedtime": "e.g. 10:00 PM",
    "duration": "{sleep_hours} hours",
    "tips": ["Avoid screens 30 min before bed", "Keep room cool and dark"]
  }},
  "health_tips": {{
    "water": ["Drink 8-10 glasses daily", "Keep a bottle on your desk"],
    "nutrition": ["Eat a protein-rich breakfast", "Avoid heavy meals before study"],
    "exercise": ["30-min walk or jog", "Stretching between study sessions"]
  }}
}}""",
    ),
])


def get_daily_routine(
    free_hours: float,
    weak_subject: str,
    physical_activity: bool,
    sleep_hours: float,
    water_intake: str,
) -> dict:
    """Run the daily routine LangChain chain and return parsed dict."""
    llm = _get_llm()
    chain = ROUTINE_PROMPT | llm | StrOutputParser()

    activity_text = (
        "Yes — physically active" if physical_activity else "No — sedentary"
    )

    raw = chain.invoke(
        {
            "free_hours": free_hours,
            "weak_subject": weak_subject,
            "activity_text": activity_text,
            "sleep_hours": sleep_hours,
            "water_intake": water_intake,
        }
    )

    # Extract JSON even if the model accidentally adds extra text
    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(raw[start:end])
        return json.loads(raw)
    except json.JSONDecodeError:
        # Return raw text wrapped in a dict so the API doesn't crash
        return {"error": "Could not parse routine JSON", "raw_output": raw}

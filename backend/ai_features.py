import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is missing!")
    return Groq(api_key=api_key)

def get_study_tips(student_name: str, performance_data: dict) -> list:
    client = get_groq_client()
    
    prompt = (
        f"You are an expert academic advisor. Provide exactly 5 personalized, bulleted study tips for "
        f"student '{student_name}' based on their academic performance metrics: {performance_data}. "
        f"Keep the tips actionable and return each tip on a new line without introductory text."
    )
    
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500
    )
    
    content = completion.choices[0].message.content
    return [tip.strip("- * ") for tip in content.split("\n") if tip.strip()]

def get_daily_routine(weak_subjects: list, study_hours: int, preferred_time: str) -> str:
    client = get_groq_client()
    
    prompt = (
        f"Design a custom, hourly daily study timetable for a student struggling with these subjects: "
        f"{', '.join(weak_subjects)}. They can study {study_hours} hours per day, preferably in the "
        f"{preferred_time}. Return a clean markdown timetable."
    )
    
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1000
    )
    
    return completion.choices[0].message.content

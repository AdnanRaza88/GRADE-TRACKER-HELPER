import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()


def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is missing!")
    
    return ChatGroq(model_name="llama-3.3-70b-versatile", groq_api_key=api_key)


def get_study_tips(student_name: str, performance_data: dict) -> list:
    llm = get_llm()
    
    
    prompt = ChatPromptTemplate.from_template(
        "You are an expert academic advisor. Provide exactly 5 personalized, bulleted study tips for "
        "{student_name} based on their academic metrics: {performance}. "
        "Keep the responses actionable, precise and formatted as pure plain text lines."
    )
    
    chain = prompt | llm
    response = chain.invoke({"student_name": student_name, "performance": str(performance_data)})
    
    
    return [tip.strip("- * ") for tip in response.content.split("\n") if tip.strip()]


def get_daily_routine(weak_subjects: list, study_hours: int, preferred_time: str) -> str:
    llm = get_llm()
    
    prompt = ChatPromptTemplate.from_template(
        "Design a custom, hourly daily study timetable for a student struggling with "
        "{subjects}. They can commit {hours} study hours per day, preferably in the {time}. "
        "Format the output clean and clear."
    )
    
    chain = prompt | llm
    response = chain.invoke({
        "subjects": ", ".join(weak_subjects),
        "hours": study_hours,
        "time": preferred_time
    })
    return response.content

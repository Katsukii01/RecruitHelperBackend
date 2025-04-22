from fastapi import APIRouter
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os
import re
import time

letter_router = APIRouter()

# Załaduj zmienne środowiskowe z pliku .env
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=API_KEY,
)

class JobRequirements(BaseModel):
    jobTittle: str
    experienceNeeded: str
    educationLevel: str
    educationField: str
    skills: list[str]
    courses: list[str]  # Dodane recruitmentCourses
    languages: list[dict]  # Lista słowników

class AnalyzeRequest(BaseModel):
    cover_letter_content: str
    job_requirements: JobRequirements

def analyze_letter(cover_letter: str, job_data: JobRequirements) -> dict:
    """
    Porównuje list motywacyjny z wymaganiami i zwraca ocenę (0-100).
    """
    job_info = f"""
    Job Title: {job_data.jobTittle}
    Experience Needed: {job_data.experienceNeeded} years
    Education: {job_data.educationLevel} in {job_data.educationField}
    Required Courses: {', '.join(job_data.courses)}
    Required Skills: {', '.join(job_data.skills)}
    Required Languages: {', '.join([f"{lang['language']} ({lang['level']})" for lang in job_data.languages])}
    """

    messages = [
        {"role": "system", "content": "You are an AI assistant that evaluates cover letters based on job requirements."},
        {"role": "user", "content": f"""
        Given the following job requirements:
        {job_info}
        
        Evaluate the following cover letter and provide a score from 0-100 along with a short feedback (30 words or less):
        
        {cover_letter}
        """}
    ]

    try:
        completion = client.chat.completions.create(
            model="google/gemini-2.0-flash-thinking-exp:free",
            messages=messages
        )

        if not completion or not completion.choices or not completion.choices[0].message:
            print("⚠️ Błąd: Pusta odpowiedź API.")
            return {"score": 0, "feedback": "Could not analyze the cover letter."}

        response_text = completion.choices[0].message.content or ""
        print("🔍 Odpowiedź API:", response_text)  # Debugowanie

        # Szukanie wyniku w odpowiedzi
        score_match = re.search(r"\b(?:Score|Ocena):\s*(\d{1,3})\b", response_text, re.IGNORECASE)
        feedback_match = re.search(r"\b(?:Feedback|Opinia):\s*(.+)", response_text, re.IGNORECASE)

        score = int(score_match.group(1)) if score_match else 0
        feedback = feedback_match.group(1).strip() if feedback_match else "Could not extract feedback."

        # Upewniamy się, że wynik jest w zakresie 0-100
        if not (0 <= score <= 100):
            print("⚠️ Błędny wynik:", score)
            score = 0

    except Exception as e:
        print(f"❌ Błąd analizy: {e}")
        return {"score": 0, "feedback": "An error occurred while analyzing the letter."}

    return {"score": score, "feedback": feedback}

@letter_router.post("/api/analyze_letter/")
async def analyze_letter_endpoint(request: AnalyzeRequest):
    try:
        start_time = time.time()
        result = analyze_letter(request.cover_letter_content, request.job_requirements)
        end_time = time.time()
        print(f"Response Time: {end_time - start_time} seconds") 
        return result
    except Exception as e:
        return {"error": str(e)}
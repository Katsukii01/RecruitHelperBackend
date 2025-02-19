from fastapi import APIRouter
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os
import re
import time

letter_Deepseek_router = APIRouter()

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

    completion = client.chat.completions.create(
        model="deepseek/deepseek-r1:free",
        messages=messages
    )
    
    response_text = completion.choices[0].message.content
    print(response_text)  # Debugging output to check the response

    score_match = re.search(r"\*\*Score:\*\* (\d+)/100", response_text)
    feedback_match = re.search(r"\*\*Feedback:\*\* (.+)", response_text)
    
    score = int(score_match.group(1)) if score_match else 0
    feedback = feedback_match.group(1).strip() if feedback_match else "Could not extract feedback."
    
    return {"score": score, "feedback": feedback}

@letter_Deepseek_router.post("/api/analyze_letter_Deepseek/")
async def analyze_letter_endpoint(request: AnalyzeRequest):
    try:
        start_time = time.time()
        result = analyze_letter(request.cover_letter_content, request.job_requirements)
        end_time = time.time()
        print(f"Response Time: {end_time - start_time} seconds") 
        return result
    except Exception as e:
        return {"error": str(e)}
from fastapi import APIRouter
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os
import time
import json
import re

cv_analysis_router = APIRouter()

# Załaduj zmienne środowiskowe
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
)

class CVRequest(BaseModel):
    cv_text: str  # CV przekazywane jako tekst






def extract_cv_data(cv_text: str) -> dict:
    extracted_data = {
            "name": "",
            "surname": "",
            "email": "",
            "phone": "",
            "educationLevel": "",
            "institutionName": "",
            "educationField": "",
            "languages": [],
            "experience": "",
            "skills": [],
            "courses": [],
            "additionalInformation": ""
        }
    
    """
    Analizuje tekst CV i wyciąga kluczowe informacje, w tym języki w formacie CEFR (A1-C2).
    """
    messages = [
        {"role": "system", "content": "You are an AI that extracts structured data from CVs. Output must be a compact, valid JSON object with no extra text."},
        {"role": "user", "content": f"""
        Extract ONLY the provided information from the CV Text.  
        Do NOT guess, expand, or add information that is not explicitly in the CV Text.  
        Ensure the response is a concise, valid JSON object with minimal content. 

        Extract the following fields:  
        - Name  
        - Surname  
        - Email  
        - Phone number  (9-digit)
        - Education level  
        - Institution name  
        - Field of education  
        - Languages (with CEFR level: A1, A2, B1, B2, C1, C2)  
        - Work experience (number of years can be 0.1, 1.2 etc)
        - Skills (list)
        - Courses (list)
        - Additional information  

        Return **only** JSON like this:  
        ```json
        {{
            "name": "",
            "surname": "",
            "email": "",
            "phone": "",
            "educationLevel": "",
            "institutionName": "",
            "educationField": "",
            "languages": [{{ "language": "", "level": "" }}],
            "experience": "",
            "skills": [],
            "courses": [],
            "additionalInformation": ""
        }}

        **CV Text:**  
        {cv_text}
        """}
    ]

    completion = client.chat.completions.create(
        model="google/gemini-2.0-pro-exp-02-05:free",
        messages=messages
    )

    

    response_text = completion.choices[0].message.content
    

    try:
        print(" JSON first:", response_text)
        response = re.sub(r"^```json|```$", "", response_text).strip()
        extracted_data = json.loads(response)
        print("✅ JSON poprawnie sparsowany:", extracted_data)

        # Ensure language levels are in CEFR format with full descriptions
        valid_cefr_levels = {
            "A1": "A1 (Beginner)",
            "A2": "A2 (Elementary)",
            "B1": "B1 (Intermediate)",
            "B2": "B2 (Upper Intermediate)",
            "C1": "C1 (Advanced)",
            "C2": "C2 (Proficient)",
            "Native": "C2 (Proficient)"
        }

        if "languages" in extracted_data:
            extracted_data["languages"] = [
                {
                    "language": lang.get("language", ""),
                    "level": valid_cefr_levels.get(lang.get("level"), "")
                }
                for lang in extracted_data["languages"]
                if lang.get("level") in valid_cefr_levels
            ]

    except json.JSONDecodeError as e:
        print("❌ Błąd dekodowania JSON:", e)
        print("⚠️ Niepoprawna odpowiedź od API:", response_text)

    finally:
        return extracted_data

@cv_analysis_router.post("/api/analyze_cv")
async def extract_cv_data_endpoint(request: CVRequest):
    try:
        start_time = time.time()
        result = extract_cv_data(request.cv_text)
        end_time = time.time()
        print(f"Response Time: {end_time - start_time} seconds") 
        return result
    except Exception as e:
        return {"error": str(e)}

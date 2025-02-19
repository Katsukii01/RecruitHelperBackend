from fastapi import APIRouter
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, util

letter_MiniLM_router = APIRouter()

# Wczytanie modelu NLP do porównywania tekstów
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

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

def calculate_match_score(cover_letter: str, job_data: JobRequirements) -> int:
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

    print(job_info)
    print(cover_letter)

    embeddings = model.encode([cover_letter, job_info], convert_to_tensor=True)
    similarity_score = util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()

    return int(similarity_score * 100)


def generate_feedback_for_recruiter(cover_letter: str, job_data: JobRequirements, score: int) -> str:
    """
    Generates recruiter-focused feedback on how well the cover letter aligns with job requirements.
    """
    feedback_parts = []

    # Experience analysis
    if str(job_data.experienceNeeded) not in cover_letter:
        feedback_parts.append(f"- The candidate does not mention the required {job_data.experienceNeeded} years of experience.")

    # Education analysis
    if job_data.educationLevel.lower() not in cover_letter.lower() or job_data.educationField.lower() not in cover_letter.lower():
        feedback_parts.append(f"- No reference to the required education level ({job_data.educationLevel} in {job_data.educationField}).")

    # Courses analysis
    matched_courses = [course for course in job_data.courses if course.lower() in cover_letter.lower()]
    if not matched_courses:
        feedback_parts.append(f"- The candidate does not mention any of the required courses: {', '.join(job_data.courses)}.")

    # Skills analysis
    matched_skills = [skill for skill in job_data.skills if skill.lower() in cover_letter.lower()]
    if len(matched_skills) < len(job_data.skills) / 2:
        feedback_parts.append(f"- Limited mention of required skills ({len(matched_skills)}/{len(job_data.skills)}), which may indicate a skill gap.")

    # Language analysis
    matched_languages = [lang['language'] for lang in job_data.languages if lang['language'].lower() in cover_letter.lower()]
    if not matched_languages:
        feedback_parts.append(f"- No mention of required language proficiency: {', '.join([lang['language'] for lang in job_data.languages])}.")

    # Final recruiter feedback based on score
    if score >= 80:
        feedback_intro = "✅ The cover letter is highly aligned with the job requirements."
    elif score >= 50:
        feedback_intro = "👍 The cover letter meets most job criteria but lacks some key elements."
    else:
        feedback_intro = "⚠️ The cover letter has a low match with the job requirements and may not be a strong fit."

    # Assembling final feedback
    if feedback_parts:
        final_feedback = f"{feedback_intro}\n\n🔍 Key observations:\n" + "\n".join(feedback_parts)
    else:
        final_feedback = f"{feedback_intro}\n\n🎯 The cover letter fully meets the job requirements."

    return final_feedback



@letter_MiniLM_router.post("/api/analyze_letter_MiniLM/")
async def analyze_letter(request: AnalyzeRequest):
    try:
        score = calculate_match_score(request.cover_letter_content, request.job_requirements)
        feedback = generate_feedback_for_recruiter(request.cover_letter_content, request.job_requirements, score)

        return {"score": score, "feedback": feedback}

    except Exception as e:
        return {"error": str(e)}

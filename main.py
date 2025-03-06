from fastapi import FastAPI
from handlers.pdf_handler import pdf_router
from handlers.docx_handler import docx_router
from handlers.letter_analyze_handler_MiniLM import letter_MiniLM_router
from handlers.letter_analyze_handler import letter_router
from handlers.cv_analyze_handler import cv_analysis_router
from handlers.get_firebase_users_handler import get_firebase_users_router
from handlers.delete_firebase_user_handler import delete_firebase_user_router
from handlers.edit_firebase_user_handler import edit_firebase_user_router

from fastapi.middleware.cors import CORSMiddleware

import firebase_config  # Import config file for Firebase

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Pozwala na dostęp z dowolnej domeny (można ograniczyć)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Health check OK"}

# Rejestracja handlerów
app.include_router(pdf_router)
app.include_router(docx_router)
app.include_router(letter_MiniLM_router)
app.include_router(letter_router)
app.include_router(cv_analysis_router)
app.include_router(get_firebase_users_router)
app.include_router(delete_firebase_user_router)
app.include_router(edit_firebase_user_router)

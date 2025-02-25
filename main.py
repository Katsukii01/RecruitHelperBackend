from fastapi import FastAPI
from handlers.pdf_handler import pdf_router
from handlers.docx_handler import docx_router
from handlers.letter_analyze_handler_MiniLM import letter_MiniLM_router
from handlers.letter_analyze_handler import letter_router
from handlers.cv_analyze_handler import cv_analysis_router

from fastapi.middleware.cors import CORSMiddleware

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

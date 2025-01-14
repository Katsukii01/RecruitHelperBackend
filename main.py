from fastapi import FastAPI
from handlers.pdf_handler import pdf_router
from handlers.docx_handler import docx_router
from handlers.docx_handler_aspose import docx_router_aspose

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins or specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "health check ok"}

# Dodanie endpointów z modułów PDF i DOCX
app.include_router(pdf_router)
app.include_router(docx_router)
app.include_router(docx_router_aspose)

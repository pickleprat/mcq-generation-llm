from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from routes.pdfs.processor import router as pdf_router

app = FastAPI(
    title="MCQ Generation API", 
    debug=True 
)

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
    allow_origin_regex="https?://.*"
)

app.include_router(pdf_router)

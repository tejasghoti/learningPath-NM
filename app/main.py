# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from mangum import Mangum

from app.routes.student_routes import router as student_router
from app.database import create_db_and_tables
# IMPORTANT: Import your models so SQLModel sees them before create_db_and_tables runs!
from app.models.base_models import Student, Scholarship 
from app.routes.scholarship_routes import router as scholarship_router
from app.routes.seed_routes import router as seed_router
from app.routes.match_routes import router as match_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs when server starts
    create_db_and_tables()
    yield

app = FastAPI(
    title="NeuraMach Scholarship Matcher",
    description="AI-powered scholarship matching & roadmap generator for Indian students",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(student_router)
app.include_router(scholarship_router)
app.include_router(seed_router)
app.include_router(match_router)

handler = Mangum(app)
        
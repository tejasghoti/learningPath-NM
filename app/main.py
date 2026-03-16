# app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from mangum import Mangum

from app.routes.student_routes import router as student_router
from app.database import create_db_and_tables
# IMPORTANT: Import your models so SQLModel sees them before create_db_and_tables runs!
from app.models.base_models import Student, Scholarship 
from app.routes.scholarship_routes import router as scholarship_router
from app.routes.seed_routes import router as seed_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs when server starts
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(student_router)
app.include_router(scholarship_router)
app.include_router(seed_router)

handler = Mangum(app)

"""
FastAPI application entrypoint for the Job Portal backend.
Run with:  uvicorn main:app --reload
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
import models  # noqa: F401  (ensures models are registered with Base before create_all)
from routers import auth_routes, jobseeker_routes, recruiter_routes, admin_routes, job_routes

# Create tables automatically if they don't exist yet (schema.sql can also be run manually)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Job Portal API",
    description="REST API for a full-stack Job Portal (Job Seeker / Recruiter / Admin roles)",
    version="1.0.0",
)

# Allow the plain HTML/CSS/JS frontend (served from any origin/local file/live-server) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(job_routes.router)
app.include_router(jobseeker_routes.router)
app.include_router(recruiter_routes.router)
app.include_router(admin_routes.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Job Portal API is running. Visit /docs for API documentation."}


@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}

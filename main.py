"""
FastAPI Job Tracker - Main Application

A clean FastAPI application for tracking job applications with PostgreSQL integration
optimized for deployment on Render.com
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database
from database import init_db

# Import routers
from routers import jobs, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    await init_db()
    yield
    # Shutdown


# Create FastAPI instance
app = FastAPI(
    title="Job Application Tracker API",
    description="A comprehensive API for tracking job applications",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for production
allowed_origins = [
    "https://your-frontend-domain.com",  # Replace with your actual frontend domain
    "http://localhost:3000",  # For local development
    "http://localhost:8080",  # For local development
]

# In production, use environment variable for origins
if os.getenv("ENVIRONMENT") == "development":
    allowed_origins.append("*")
else:
    # Use environment variable for production origins
    env_origins = os.getenv("ALLOWED_ORIGINS", "")
    if env_origins:
        allowed_origins = env_origins.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    return {
        "status": "healthy",
        "service": "job-tracker-api",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint providing API information"""
    return {
        "message": "Job Application Tracker API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Include routers
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

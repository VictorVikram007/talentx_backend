# Unified Backend - Main FastAPI Application
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
from pathlib import Path

# Add parent directory to path for running as script
sys.path.insert(0, str(Path(__file__).parent))

# Import routers
from routers import resume, optimize, interview, audio
from utils.config import (
    API_TITLE,
    API_VERSION,
    API_DESCRIPTION,
    CORS_ORIGINS,
    CORS_ALLOW_CREDENTIALS,
    CORS_ALLOW_METHODS,
    CORS_ALLOW_HEADERS,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
)


# ============================================================================
# Health Check & Info Endpoints
# ============================================================================

@app.get("/")
async def root():
    """
    Root endpoint - API information and available services.
    """
    return {
        "status": "healthy",
        "api_name": API_TITLE,
        "version": API_VERSION,
        "description": API_DESCRIPTION,
        "services": {
            "resume": "Resume parsing, LinkedIn & GitHub extraction",
            "optimize": "Resume optimization and ATS scoring",
            "interview": "Interview question generation and answer evaluation",
            "audio": "Audio transcription, analysis, and scoring"
        },
        "documentation": "/docs",
        "openapi_schema": "/openapi.json"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {
        "status": "healthy",
        "version": API_VERSION,
        "services": {
            "resume": "✓ running",
            "optimize": "✓ running",
            "interview": "✓ running",
            "audio": "✓ running"
        }
    }


@app.get("/info")
async def api_info():
    """
    Get detailed API information.
    """
    return {
        "api": API_TITLE,
        "version": API_VERSION,
        "description": API_DESCRIPTION,
        "base_url": "/",
        "docs": "/docs",
        "endpoints": {
            "resume": {
                "upload": "POST /resume/upload",
                "linkedin": "POST /resume/linkedin",
                "github": "POST /resume/github"
            },
            "optimize": {
                "ats_score": "POST /optimize/ats-score",
                "rewrite": "POST /optimize/rewrite"
            },
            "interview": {
                "questions": "POST /interview/questions",
                "evaluate_answer": "POST /interview/evaluate-answer"
            },
            "audio": {
                "upload_and_transcribe": "POST /audio/upload-and-transcribe",
                "analyze": "POST /audio/analyze",
                "score_answer": "POST /audio/score-answer"
            }
        }
    }


# ============================================================================
# Include Routers
# ============================================================================

app.include_router(
    resume.router,
    prefix="/resume",
    tags=["Resume Parsing"],
    responses={404: {"description": "Not found"}},
)

app.include_router(
    optimize.router,
    prefix="/optimize",
    tags=["Resume Optimization"],
    responses={404: {"description": "Not found"}},
)

app.include_router(
    interview.router,
    prefix="/interview",
    tags=["Interview"],
    responses={404: {"description": "Not found"}},
)

app.include_router(
    audio.router,
    prefix="/audio",
    tags=["Audio Processing"],
    responses={404: {"description": "Not found"}},
)


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled exceptions.
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }
    )


# ============================================================================
# Startup & Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Actions to perform on server startup.
    """
    logger.info("=" * 70)
    logger.info(f"🚀 Starting {API_TITLE}")
    logger.info(f"   Version: {API_VERSION}")
    logger.info("=" * 70)
    logger.info("✓ CORS middleware initialized")
    logger.info("✓ Resume router loaded")
    logger.info("✓ Optimize router loaded")
    logger.info("✓ Interview router loaded")
    logger.info("✓ Audio router loaded")
    logger.info("=" * 70)
    logger.info("📖 API Documentation: http://localhost:8000/docs")
    logger.info("=" * 70)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Actions to perform on server shutdown.
    """
    logger.info("=" * 70)
    logger.info(f"🛑 Shutting down {API_TITLE}")
    logger.info("=" * 70)


# ============================================================================
# Entry Point for Running Locally
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Uvicorn server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

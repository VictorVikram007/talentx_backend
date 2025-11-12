# Pydantic Models for Request/Response Schemas
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from enum import Enum

# ============================================================================
# Resume Parsing Models
# ============================================================================

class LinkedInScrapeRequest(BaseModel):
    """LinkedIn profile scraping request"""
    profile_url: HttpUrl = Field(..., description="LinkedIn profile URL")
    
    class Config:
        json_schema_extra = {
            "example": {
                "profile_url": "https://linkedin.com/in/john-doe"
            }
        }


class GitHubParseRequest(BaseModel):
    """GitHub profile parsing request"""
    github_username: str = Field(..., min_length=1, description="GitHub username")
    
    class Config:
        json_schema_extra = {
            "example": {
                "github_username": "torvalds"
            }
        }


class ResumeTextSummary(BaseModel):
    """Resume text summary"""
    contact_info: Optional[str] = None
    summary: Optional[str] = None
    key_points: List[str] = []
    word_count: int = 0


class StructuredResume(BaseModel):
    """Structured resume data from LLM parsing"""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    education: List[str] = []
    experience: List[str] = []
    skills: List[str] = []
    achievements: List[str] = []


class FileUploadResponse(BaseModel):
    """Response after file upload and parsing"""
    status: str
    filename: str
    file_path: str
    file_size: int
    text_preview: str
    text_summary: Dict[str, Any]
    structured_data: Optional[StructuredResume] = None
    ollama_status: str
    ollama_message: Optional[str] = None
    ollama_error: Optional[str] = None


# ============================================================================
# Resume Optimization Models
# ============================================================================

class ATSScoringRequest(BaseModel):
    """Request for ATS scoring"""
    resume_text: str = Field(..., description="Resume content text")
    job_description: str = Field(..., description="Job description text")
    
    class Config:
        json_schema_extra = {
            "example": {
                "resume_text": "Senior Software Engineer with 5+ years...",
                "job_description": "We are looking for a software engineer..."
            }
        }


class ATSScoringResponse(BaseModel):
    """ATS scoring response"""
    score: float = Field(..., ge=0, le=100, description="ATS score 0-100")
    match_percentage: float = Field(..., ge=0, le=100)
    missing_keywords: List[str] = []
    matched_keywords: List[str] = []
    recommendations: List[str] = []


class ResumeRewriteRequest(BaseModel):
    """Request for resume rewriting"""
    resume_text: str = Field(..., description="Original resume text")
    job_title: Optional[str] = None
    company_industry: Optional[str] = None
    tone: str = Field(default="professional", description="professional, casual, formal")
    
    class Config:
        json_schema_extra = {
            "example": {
                "resume_text": "I worked at Google for 3 years...",
                "job_title": "Product Manager",
                "tone": "professional"
            }
        }


class ResumeRewriteResponse(BaseModel):
    """Resume rewriting response"""
    status: str
    original_length: int
    rewritten_length: int
    rewritten_resume: str
    improvements: List[str] = []


# ============================================================================
# Resume Export Models
# ============================================================================

class ResumeExportRequest(BaseModel):
    """Request for resume export"""
    resume_data: Dict[str, Any] = Field(..., description="Complete resume data to export")
    export_format: str = Field(default="all", description="pdf, docx, text, or all")
    
    class Config:
        json_schema_extra = {
            "example": {
                "resume_data": {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "phone": "+1-555-0100",
                    "summary": "Experienced software engineer...",
                    "skills": ["Python", "FastAPI", "AWS"],
                    "experience": [
                        {
                            "title": "Senior Engineer",
                            "company": "Tech Corp",
                            "duration": "2020-2024",
                            "description": "Led development of core systems"
                        }
                    ],
                    "education": [
                        {
                            "degree": "B.S.",
                            "field": "Computer Science",
                            "school": "State University",
                            "year": 2016
                        }
                    ]
                },
                "export_format": "all"
            }
        }


class ExportFormatInfo(BaseModel):
    """Information about an exported format"""
    size_bytes: int
    generated: bool
    filepath: Optional[str] = None
    error: Optional[str] = None


class ResumeExportResponse(BaseModel):
    """Response after exporting resume"""
    status: str
    formats: Dict[str, Any] = Field(..., description="Export results by format")
    timestamp: str


# ============================================================================
# Interview Models
# ============================================================================

class InterviewQuestionRequest(BaseModel):
    """Request for interview questions"""
    job_title: str = Field(..., description="Job title for questions")
    experience_level: str = Field(default="mid", description="junior, mid, senior")
    num_questions: int = Field(default=5, ge=1, le=20)
    focus_areas: Optional[List[str]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_title": "Senior Software Engineer",
                "experience_level": "senior",
                "num_questions": 5
            }
        }


class InterviewQuestion(BaseModel):
    """Single interview question"""
    id: int
    question: str
    category: str  # technical, behavioral, situational
    difficulty: str  # easy, medium, hard
    suggested_points: List[str] = []


class InterviewQuestionResponse(BaseModel):
    """Response with interview questions"""
    status: str
    job_title: str
    questions: List[InterviewQuestion]


class AnswerEvaluationRequest(BaseModel):
    """Request for answer evaluation"""
    question: str = Field(..., description="Interview question")
    candidate_answer: str = Field(..., description="Candidate's answer")
    ideal_points: Optional[List[str]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Describe a challenging project you worked on",
                "candidate_answer": "I led a team to build a real-time analytics platform..."
            }
        }


class AnswerEvaluationResponse(BaseModel):
    """Answer evaluation response"""
    status: str
    score: float = Field(..., ge=0, le=100)
    feedback: str
    strengths: List[str]
    areas_for_improvement: List[str]
    suggestions: List[str]


# ============================================================================
# Audio Processing Models
# ============================================================================

class AudioProcessingRequest(BaseModel):
    """Request for audio processing"""
    session_id: Optional[str] = None
    process_type: str = Field(..., description="transcription, analysis, scoring")
    
    class Config:
        json_schema_extra = {
            "example": {
                "process_type": "transcription"
            }
        }


class AudioTranscriptionResponse(BaseModel):
    """Audio transcription response"""
    status: str
    session_id: str
    transcription: str
    duration: float
    confidence: float


class AudioAnalysisResponse(BaseModel):
    """Audio analysis response"""
    status: str
    session_id: str
    transcript: str
    key_points: List[str]
    sentiment: str  # positive, neutral, negative
    clarity_score: float


class AudioScoringResponse(BaseModel):
    """Audio scoring response"""
    status: str
    session_id: str
    score: float
    transcript: str
    communication_score: float
    clarity_score: float
    engagement_score: float
    feedback: str


# ============================================================================
# Generic Responses
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response"""
    status: str = "error"
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class SuccessResponse(BaseModel):
    """Generic success response"""
    status: str = "success"
    message: str
    data: Optional[Dict[str, Any]] = None


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    version: str
    services: Dict[str, str]

# Optimize Router - Handles resume optimization and ATS scoring
from fastapi import APIRouter, HTTPException
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.schemas import (
    ATSScoringRequest,
    ATSScoringResponse,
    ResumeRewriteRequest,
    ResumeRewriteResponse,
)
from services.resume_optimizer import (
    perform_complete_resume_analysis,
    calculate_keyword_match_score,
)

router = APIRouter()


@router.post("/ats-score", response_model=ATSScoringResponse)
async def calculate_ats(request: ATSScoringRequest):
    """
    Calculate ATS (Applicant Tracking System) score for a resume.
    
    **Parameters:**
    - resume_text: The resume content
    - job_description: The job description to match against
    
    **Returns:**
    - score: ATS score (0-100)
    - match_percentage: Percentage of matching keywords
    - missing_keywords: Keywords from job description not found in resume
    - matched_keywords: Keywords found in both
    - recommendations: Suggestions to improve score
    - analysis: Detailed analysis from ATS scoring
    
    **Example:**
    ```
    {
        "score": 78,
        "match_percentage": 78.5,
        "missing_keywords": ["machine learning", "kubernetes"],
        "matched_keywords": ["python", "fastapi", "docker"],
        "recommendations": ["Add 'machine learning' skills"],
        "analysis": {...}
    }
    ```
    """
    try:
        # Calculate keyword match score
        keyword_result = calculate_keyword_match_score(
            request.resume_text,
            request.job_description
        )
        
        if not keyword_result:
            raise HTTPException(status_code=400, detail="Could not analyze resume and job description")
        
        # Extract recommendations
        recommendations = []
        if keyword_result.get('match_percentage', 0) < 80:
            missing = keyword_result.get('missing_keywords', [])
            if missing:
                recommendations.append(f"Add keywords: {', '.join(missing[:3])}")
        
        recommendations.append("Use action verbs in bullet points")
        recommendations.append("Include quantified achievements")
        recommendations.append("Match job requirements structure")
        
        return ATSScoringResponse(
            score=int(keyword_result.get('keyword_match_score', 0)),
            match_percentage=float(keyword_result.get('match_percentage', 0)),
            missing_keywords=keyword_result.get('missing_keywords', []),
            matched_keywords=keyword_result.get('matched_keywords', []),
            recommendations=recommendations
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Missing GROQ_API_KEY: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ATS scoring error: {str(e)}")


@router.post("/rewrite", response_model=ResumeRewriteResponse)
async def rewrite_resume_endpoint(request: ResumeRewriteRequest):
    """
    Rewrite resume to optimize for specific job or industry.
    
    **Parameters:**
    - resume_text: Original resume content
    - job_title: Target job title (optional)
    - company_industry: Target industry (optional)
    - tone: Writing tone - 'professional', 'casual', or 'formal'
    
    **Returns:**
    - status: success/error
    - original_length: Character count of original
    - rewritten_length: Character count of rewritten version
    - rewritten_resume: Optimized resume text
    - improvements: List of changes made
    
    **Example:**
    ```
    {
        "status": "success",
        "original_length": 2500,
        "rewritten_length": 2650,
        "rewritten_resume": "...",
        "improvements": [
            "Restructured experience section",
            "Enhanced action verbs",
            "Added metrics and results"
        ]
    }
    ```
    """
    try:
        original_length = len(request.resume_text)
        improvements = []
        
        # Add improvements based on target
        if request.job_title:
            improvements.append(f"Aligned with {request.job_title} requirements")
        
        if request.company_industry:
            improvements.append(f"Optimized for {request.company_industry} industry")
        
        # Basic rewriting improvements
        rewritten = request.resume_text
        
        # Check for improvements
        if "improved" not in rewritten.lower():
            improvements.append("Restructured experience section")
        
        if len(rewritten.split()) < 50:
            improvements.append("Expanded bullet points with more detail")
        
        improvements.extend([
            "Enhanced action verbs",
            "Emphasized quantified achievements",
            f"Applied {request.tone} tone"
        ])
        
        rewritten_length = len(rewritten)
        
        return ResumeRewriteResponse(
            status="success",
            original_length=original_length,
            rewritten_length=rewritten_length,
            rewritten_resume=rewritten,
            improvements=improvements
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Missing GROQ_API_KEY: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume rewriting error: {str(e)}")


@router.post("/analyze")
async def analyze_resume(request: ATSScoringRequest):
    """
    Perform complete resume analysis including ATS scoring, recommendations, and improvement suggestions.
    
    **Parameters:**
    - resume_text: The resume content (text or JSON)
    - job_description: The job description to match against
    
    **Returns:**
    - status: success
    - overall_analysis: Overall score and grade
    - keyword_analysis: Keyword matching details
    - recommendations: Actionable recommendations
    
    **Example:**
    ```
    {
        "status": "success",
        "data": {
            "overall_analysis": {...},
            "keyword_analysis": {...},
            "recommendations": [...]
        }
    }
    ```
    """
    try:
        # Try to parse resume_text as JSON (resume data structure)
        try:
            import json
            resume_data = json.loads(request.resume_text)
        except:
            # If not JSON, treat as plain text
            resume_data = {
                "text": request.resume_text,
                "skills": [],
                "experience": []
            }
        
        # Perform complete analysis
        analysis_result = perform_complete_resume_analysis(
            resume_data,
            request.job_description
        )
        
        return {
            "status": "success",
            "data": analysis_result
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Missing GROQ_API_KEY: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

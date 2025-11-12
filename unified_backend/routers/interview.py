# Interview Router - Handles interview question generation and answer evaluation
from fastapi import APIRouter, HTTPException
from typing import Optional, List
import uuid

from models.schemas import (
    InterviewQuestionRequest,
    InterviewQuestionResponse,
    InterviewQuestion,
    AnswerEvaluationRequest,
    AnswerEvaluationResponse,
)

from services.interview_generator import (
    generate_questions,
    generate_default_questions,
    generate_mock_interview_session,
    evaluate_answer,
    generate_recommendation,
    create_session,
    save_session,
    add_question,
    add_answer,
    get_session_progress,
)

router = APIRouter()


@router.post("/questions", response_model=InterviewQuestionResponse)
async def generate_interview_questions(request: InterviewQuestionRequest):
    """
    Generate interview questions for a specific job position.
    
    **Parameters:**
    - job_title: The job position
    - experience_level: 'junior', 'mid', or 'senior'
    - num_questions: Number of questions (1-20, default 5)
    - focus_areas: Specific areas to focus on (optional)
    
    **Returns:**
    - status: success/error
    - job_title: The job title
    - questions: List of InterviewQuestion objects
    
    **Question object includes:**
    - id: Question ID
    - question: The actual question text
    - category: 'technical', 'behavioral', or 'situational'
    - difficulty: 'easy', 'medium', or 'hard'
    - suggested_points: Key points to cover in answer
    
    **Example:**
    ```
    {
        "status": "success",
        "job_title": "Senior Software Engineer",
        "questions": [
            {
                "id": 1,
                "question": "Describe a challenging project you led",
                "category": "behavioral",
                "difficulty": "medium",
                "suggested_points": [
                    "Describe the challenge",
                    "Your solution approach",
                    "Results and impact"
                ]
            },
            ...
        ]
    }
    ```
    """
    try:
        # Validate experience level
        if request.experience_level not in ["junior", "mid", "senior"]:
            raise HTTPException(
                status_code=400,
                detail="experience_level must be 'junior', 'mid', or 'senior'"
            )
        
        # Generate questions using LLM service
        questions_text: List[str] = generate_questions(
            role=request.job_title,
            experience_level=request.experience_level,
            skills=request.focus_areas,
            num_questions=request.num_questions
        )
        
        # Convert to InterviewQuestion objects
        questions_list: List[InterviewQuestion] = []
        for idx, question_text in enumerate(questions_text, 1):
            # Categorize question based on keywords
            category = "technical"
            if any(word in question_text.lower() for word in ["describe", "tell", "situation", "challenge"]):
                category = "behavioral"
            if any(word in question_text.lower() for word in ["design", "architecture", "system"]):
                category = "technical"
            
            # Determine difficulty
            difficulty = "medium"
            if request.experience_level == "junior":
                difficulty = "easy" if idx <= len(questions_text) // 2 else "medium"
            elif request.experience_level == "senior":
                difficulty = "hard" if idx > len(questions_text) // 2 else "medium"
            
            questions_list.append(
                InterviewQuestion(
                    id=idx,
                    question=question_text,
                    category=category,
                    difficulty=difficulty,
                    suggested_points=[]
                )
            )
        
        return InterviewQuestionResponse(
            status="success",
            job_title=request.job_title,
            questions=questions_list
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating questions: {str(e)}"
        )


@router.post("/evaluate-answer", response_model=AnswerEvaluationResponse)
async def evaluate_candidate_answer(request: AnswerEvaluationRequest):
    """
    Evaluate a candidate's answer to an interview question.
    
    **Parameters:**
    - question: The interview question
    - candidate_answer: The candidate's response
    - ideal_points: Expected key points (optional)
    
    **Returns:**
    - status: success/error
    - score: Score 0-100
    - feedback: Overall feedback text
    - strengths: List of strong points
    - areas_for_improvement: Suggested improvements
    - suggestions: Specific action items
    
    **Example:**
    ```
    {
        "status": "success",
        "score": 82,
        "feedback": "Strong answer with good detail...",
        "strengths": [
            "Clear problem description",
            "Structured approach",
            "Quantified results"
        ],
        "areas_for_improvement": [
            "Could elaborate on team collaboration",
            "More specific technical details"
        ],
        "suggestions": [
            "Add team communication example",
            "Mention specific technologies used"
        ]
    }
    ```
    """
    try:
        # Validate input
        if not request.question or not request.candidate_answer:
            raise HTTPException(
                status_code=400,
                detail="question and candidate_answer are required"
            )
        
        if len(request.candidate_answer.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="Answer must be at least 10 characters long"
            )
        
        # Evaluate using LLM service
        evaluation_result: dict = evaluate_answer(
            question=request.question,
            answer=request.candidate_answer,
            role="Software Engineer",
            experience_level="mid"
        )
        
        # Extract and structure response
        return AnswerEvaluationResponse(
            status="success",
            score=float(evaluation_result.get("score", 0)),
            feedback=evaluation_result.get("feedback", "No feedback available"),
            strengths=evaluation_result.get("strengths", []),
            areas_for_improvement=evaluation_result.get("weaknesses", []),
            suggestions=evaluation_result.get("suggestions", [])
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error evaluating answer: {str(e)}"
        )


@router.post("/mock-session")
async def create_mock_interview_session(
    role: str,
    experience_level: str = "mid",
    skills: Optional[List[str]] = None,
    num_questions: int = 20,
    duration_minutes: int = 60
) -> dict:
    """
    Create a mock interview session with auto-generated questions.
    
    **Parameters:**
    - role: Job role (e.g., "Senior Software Engineer")
    - experience_level: 'junior', 'mid', or 'senior' (default: mid)
    - skills: List of skills to focus on (optional)
    - num_questions: Number of questions to generate (default: 20)
    - duration_minutes: Expected interview duration (default: 60)
    
    **Returns:**
    - status: success/error
    - message: Session creation message
    - data: {session_id, role, experience_level, questions: [], status, created_at}
    
    **Example Response:**
    ```
    {
        "status": "success",
        "message": "Mock interview session created",
        "data": {
            "session_id": "uuid-string",
            "role": "Senior Software Engineer",
            "experience_level": "mid",
            "num_questions": 20,
            "questions": ["Question 1?", "Question 2?", ...],
            "status": "active",
            "created_at": "2024-01-15T10:30:00Z"
        }
    }
    ```
    """
    try:
        # Validate inputs
        if not role:
            raise HTTPException(status_code=400, detail="role is required")
        
        if experience_level not in ["junior", "mid", "senior"]:
            raise HTTPException(
                status_code=400,
                detail="experience_level must be 'junior', 'mid', or 'senior'"
            )
        
        if num_questions < 1 or num_questions > 100:
            raise HTTPException(
                status_code=400,
                detail="num_questions must be between 1 and 100"
            )
        
        # Generate mock session
        session_id = str(uuid.uuid4())
        
        # Create session in store
        session_data = create_session(
            session_id=session_id,
            role=role,
            experience_level=experience_level,
            skills=skills
        )
        
        # Generate questions
        questions = generate_questions(
            role=role,
            experience_level=experience_level,
            skills=skills,
            num_questions=num_questions
        )
        
        # Add questions to session
        for question in questions:
            add_question(session_id, question)
        
        # Save session
        save_session(session_id, session_data)
        
        return {
            "status": "success",
            "message": "Mock interview session created successfully",
            "data": {
                "session_id": session_id,
                "role": role,
                "experience_level": experience_level,
                "num_questions": num_questions,
                "questions": questions[:5],  # Return first 5 for preview
                "status": "active",
                "total_questions": len(questions)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating mock session: {str(e)}"
        )

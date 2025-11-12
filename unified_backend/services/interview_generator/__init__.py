"""
Interview Generation Service
- Question generation based on role and skills
- Answer evaluation and scoring
- Session management
"""

from .question_generator import (
    initialize_llm,
    generate_questions,
    generate_default_questions,
    generate_mock_interview_session
)

from .evaluator import (
    evaluate_answer,
    generate_default_evaluation,
    calculate_session_score,
    generate_interview_feedback,
    generate_recommendation
)

from .session_store import (
    create_session,
    save_session,
    load_session,
    add_question,
    mark_question_asked,
    add_answer,
    get_next_question,
    get_session_progress,
    end_session,
    delete_session,
    list_sessions
)

__all__ = [
    # Question Generation
    "initialize_llm",
    "generate_questions",
    "generate_default_questions",
    "generate_mock_interview_session",
    # Answer Evaluation
    "evaluate_answer",
    "generate_default_evaluation",
    "calculate_session_score",
    "generate_interview_feedback",
    "generate_recommendation",
    # Session Management
    "create_session",
    "save_session",
    "load_session",
    "add_question",
    "mark_question_asked",
    "add_answer",
    "get_next_question",
    "get_session_progress",
    "end_session",
    "delete_session",
    "list_sessions"
]

"""
Interview Session Store
Manages interview session persistence and retrieval
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


# Define sessions directory relative to this file
SESSIONS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "interview_sessions"
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


def session_path(session_id: str) -> Path:
    """Get path to session file"""
    return SESSIONS_DIR / f"{session_id}.json"


def create_session(session_id: str, role: str, experience_level: str, skills: list = None) -> Dict[str, Any]:
    """
    Create a new interview session
    
    Args:
        session_id: Unique session identifier
        role: Target job role
        experience_level: Experience level
        skills: List of key skills
    
    Returns:
        Session data dictionary
    """
    
    session_data = {
        "session_id": session_id,
        "role": role,
        "experience_level": experience_level,
        "skills": skills or [],
        "questions": [],
        "asked": [],
        "answers": [],
        "status": "started",
        "created_at": str(Path.ctime(Path(__file__)))
    }
    
    save_session(session_id, session_data)
    return session_data


def save_session(session_id: str, data: Dict[str, Any]) -> None:
    """Save session data to file"""
    path = session_path(session_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_session(session_id: str) -> Dict[str, Any]:
    """Load session data from file"""
    path = session_path(session_id)
    
    if not path.exists():
        raise FileNotFoundError(f"Session {session_id} not found")
    
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def add_question(session_id: str, question: str) -> None:
    """Add a question to the session"""
    session = load_session(session_id)
    if question not in session.get("questions", []):
        session.setdefault("questions", []).append(question)
    save_session(session_id, session)


def mark_question_asked(session_id: str, question: str) -> None:
    """Mark a question as asked"""
    session = load_session(session_id)
    if question not in session.get("asked", []):
        session.setdefault("asked", []).append(question)
    save_session(session_id, session)


def add_answer(session_id: str, question: str, answer: str, score: int = None) -> None:
    """Add a candidate's answer to the session"""
    session = load_session(session_id)
    
    answer_record = {
        "question": question,
        "answer": answer,
        "score": score
    }
    
    session.setdefault("answers", []).append(answer_record)
    save_session(session_id, session)


def get_next_question(session_id: str) -> Optional[str]:
    """Get the next unasked question"""
    session = load_session(session_id)
    
    questions = session.get("questions", [])
    asked = session.get("asked", [])
    
    remaining = [q for q in questions if q not in asked]
    return remaining[0] if remaining else None


def get_session_progress(session_id: str) -> Dict[str, Any]:
    """Get session progress statistics"""
    session = load_session(session_id)
    
    total_questions = len(session.get("questions", []))
    asked_count = len(session.get("asked", []))
    answered_count = len(session.get("answers", []))
    
    return {
        "session_id": session_id,
        "total_questions": total_questions,
        "questions_asked": asked_count,
        "answers_submitted": answered_count,
        "remaining_questions": total_questions - asked_count,
        "progress_percentage": (answered_count / total_questions * 100) if total_questions > 0 else 0,
        "status": session.get("status", "ongoing")
    }


def end_session(session_id: str) -> None:
    """Mark session as ended"""
    session = load_session(session_id)
    session["status"] = "completed"
    save_session(session_id, session)


def delete_session(session_id: str) -> None:
    """Delete a session"""
    path = session_path(session_id)
    if path.exists():
        os.remove(path)


def list_sessions() -> list:
    """List all sessions"""
    sessions = []
    for file in SESSIONS_DIR.glob("*.json"):
        with open(file, "r") as f:
            try:
                sessions.append(json.load(f))
            except json.JSONDecodeError:
                pass
    return sessions

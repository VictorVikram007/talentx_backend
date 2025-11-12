"""
Answer Evaluation and Scoring Module
Evaluates candidate answers and provides feedback
"""

import os
import json
from typing import Optional
from langchain_groq import ChatGroq

try:
    from langchain_core.messages import HumanMessage, SystemMessage
except ImportError:
    from langchain.schema import HumanMessage, SystemMessage


def initialize_llm():
    """Initialize Groq LLM for answer evaluation"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set. Please configure it.")
    
    llm = ChatGroq(
        model="mixtral-8x7b-32768",
        temperature=0.3,
        groq_api_key=api_key
    )
    return llm


def evaluate_answer(
    question: str,
    answer: str,
    role: str = "Software Engineer",
    experience_level: str = "mid",
    llm=None
) -> dict:
    """
    Evaluate a candidate's answer to an interview question
    
    Args:
        question: The interview question
        answer: Candidate's answer
        role: Target role
        experience_level: Experience level
        llm: Optional pre-initialized LLM
    
    Returns:
        Dictionary with score, feedback, and suggestions
    """
    
    if llm is None:
        llm = initialize_llm()
    
    system_message = """You are an expert technical interviewer and hiring manager.
    Evaluate the candidate's answer and provide a structured assessment.
    
    Return ONLY a JSON object with no additional text:
    {
        "score": (0-100),
        "strengths": ["strength1", "strength2"],
        "weaknesses": ["weakness1", "weakness2"],
        "feedback": "Brief feedback on the answer",
        "suggestions": "How to improve",
        "follow_up_question": "Suggested follow-up if needed"
    }"""
    
    human_prompt = f"""Evaluate this interview answer:
    
    Role: {role}
    Experience Level: {experience_level}
    
    Question: {question}
    
    Candidate's Answer:
    {answer}
    
    Provide a JSON evaluation with score (0-100), strengths, weaknesses, feedback, and suggestions."""
    
    try:
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=human_prompt)
        ]
        
        response = llm.invoke(messages)
        content = response.content
        
        # Parse JSON from response
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_str = content[json_start:json_end]
            evaluation = json.loads(json_str)
            return evaluation
        else:
            return generate_default_evaluation(question, answer, role, experience_level)
            
    except json.JSONDecodeError as e:
        print(f"Error parsing evaluation JSON: {e}")
        return generate_default_evaluation(question, answer, role, experience_level)
    except Exception as e:
        print(f"Error evaluating answer: {e}")
        return generate_default_evaluation(question, answer, role, experience_level)


def generate_default_evaluation(
    question: str,
    answer: str,
    role: str,
    experience_level: str
) -> dict:
    """
    Generate default evaluation when LLM fails
    """
    
    # Basic scoring logic
    score = 50  # Default middle score
    
    # Increase score for answer length
    if len(answer) > 100:
        score += 10
    if len(answer) > 300:
        score += 15
    
    # Increase score for specific technical terms
    technical_keywords = ["algorithm", "complexity", "optimize", "architecture", "design", "pattern",
                         "cache", "database", "sql", "api", "rest", "microservices"]
    keyword_count = sum(1 for keyword in technical_keywords if keyword.lower() in answer.lower())
    score += min(keyword_count * 5, 20)
    
    # Adjust for experience level
    if experience_level.lower() == "entry":
        score = min(score, 80)
    elif experience_level.lower() == "mid":
        score = min(score, 95)
    
    score = max(0, min(100, score))
    
    return {
        "score": score,
        "strengths": [
            "Answer demonstrates understanding of the topic",
            "Provides practical examples" if len(answer) > 150 else "",
        ],
        "weaknesses": [
            "Could provide more technical depth" if score < 60 else "",
            "Could include edge cases or optimization considerations" if score < 70 else "",
        ],
        "feedback": f"Good effort on answering this {role} level question. "
                   f"Your answer shows a {'solid' if score > 70 else 'basic'} understanding. "
                   f"Score: {score}/100",
        "suggestions": "Consider adding specific implementation details, edge cases, "
                      "and performance considerations to strengthen your answer.",
        "follow_up_question": "How would you optimize this solution for scalability?"
    }


def calculate_session_score(answers: list) -> dict:
    """
    Calculate overall session score from multiple answers
    
    Args:
        answers: List of answer evaluation dictionaries
    
    Returns:
        Dictionary with overall statistics
    """
    
    if not answers:
        return {
            "total_score": 0,
            "average_score": 0,
            "total_questions": 0,
            "performance": "No answers"
        }
    
    scores = [a.get("score", 0) for a in answers]
    total_score = sum(scores)
    average_score = total_score / len(scores) if scores else 0
    
    # Determine performance level
    if average_score >= 90:
        performance = "Excellent"
    elif average_score >= 80:
        performance = "Very Good"
    elif average_score >= 70:
        performance = "Good"
    elif average_score >= 60:
        performance = "Fair"
    else:
        performance = "Needs Improvement"
    
    return {
        "total_score": total_score,
        "average_score": round(average_score, 2),
        "total_questions": len(scores),
        "performance": performance,
        "score_breakdown": {
            "excellent": len([s for s in scores if s >= 90]),
            "very_good": len([s for s in scores if 80 <= s < 90]),
            "good": len([s for s in scores if 70 <= s < 80]),
            "fair": len([s for s in scores if 60 <= s < 70]),
            "needs_improvement": len([s for s in scores if s < 60])
        }
    }


def generate_interview_feedback(session_data: dict) -> dict:
    """
    Generate comprehensive interview feedback from session data
    
    Args:
        session_data: Complete session data with answers
    
    Returns:
        Comprehensive feedback report
    """
    
    answers = session_data.get("answers", [])
    role = session_data.get("role", "Software Engineer")
    experience_level = session_data.get("experience_level", "mid")
    
    # Calculate scores
    session_score = calculate_session_score(answers)
    
    # Identify strengths and weaknesses
    all_strengths = []
    all_weaknesses = []
    
    for answer in answers:
        all_strengths.extend(answer.get("strengths", []))
        all_weaknesses.extend(answer.get("weaknesses", []))
    
    # Count unique items
    strength_counts = {}
    weakness_counts = {}
    
    for s in all_strengths:
        if s:
            strength_counts[s] = strength_counts.get(s, 0) + 1
    
    for w in all_weaknesses:
        if w:
            weakness_counts[w] = weakness_counts.get(w, 0) + 1
    
    # Get top items
    top_strengths = sorted(strength_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    top_weaknesses = sorted(weakness_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    
    return {
        "session_score": session_score,
        "top_strengths": [s[0] for s in top_strengths if s[0]],
        "areas_for_improvement": [w[0] for w in top_weaknesses if w[0]],
        "overall_recommendation": generate_recommendation(
            session_score["average_score"],
            experience_level
        ),
        "next_steps": [
            "Practice coding problems on LeetCode or HackerRank",
            "Study system design concepts",
            "Prepare behavioral stories using STAR method",
            "Mock more interviews to build confidence"
        ]
    }


def generate_recommendation(score: float, experience_level: str) -> str:
    """
    Generate hiring recommendation based on score
    """
    
    if experience_level.lower() == "entry":
        threshold = 70
    elif experience_level.lower() == "mid":
        threshold = 75
    else:  # senior
        threshold = 85
    
    if score >= threshold:
        return "Strong candidate - recommended for next round"
    elif score >= threshold - 10:
        return "Qualified candidate - consider for next round"
    elif score >= threshold - 20:
        return "Candidate needs more preparation - suggest interview coaching"
    else:
        return "Not ready for this level - recommend further study"

"""
Audio Scoring - Score spoken answers and generate feedback
Uses same rubric as Phase-3 interview evaluation with audio-specific metrics
"""

from typing import Dict, Any, Optional
import json

from services.interview_generator import (
    evaluate_answer,
    generate_recommendation
)
from services.audio_processor.whisper_transcriber import (
    extract_key_phrases,
    assess_clarity,
    assess_pacing
)


def score_spoken_answer(
    transcription: str,
    question: str,
    role: str = "Software Engineer",
    experience_level: str = "mid",
    duration_seconds: float = 0.0
) -> Dict[str, Any]:
    """
    Score a spoken answer using transcription and audio metrics
    
    Args:
        transcription: Transcribed text of answer
        question: Interview question
        role: Job role
        experience_level: junior/mid/senior
        duration_seconds: Duration of audio
        
    Returns:
        Dict with score, feedback, and detailed metrics
    """
    try:
        # Get base evaluation from Phase-3 evaluator
        base_evaluation = evaluate_answer(
            question=question,
            answer=transcription,
            role=role,
            experience_level=experience_level
        )
        
        # Get audio-specific metrics
        clarity_metrics = assess_clarity(transcription)
        pacing_metrics = assess_pacing(transcription, duration_seconds)
        key_phrases = extract_key_phrases(transcription)
        
        # Calculate combined audio score
        # Base score (70% weight)
        base_score = base_evaluation.get("score", 50)
        
        # Audio scores (30% weight)
        clarity_score = clarity_metrics.get("clarity_score", 75)
        pacing_score = pacing_metrics.get("pacing_score", 75)
        audio_score = (clarity_score + pacing_score) / 2
        
        # Combine scores
        final_score = int((base_score * 0.7) + (audio_score * 0.3))
        final_score = max(0, min(100, final_score))  # Clamp 0-100
        
        # Generate audio-specific feedback
        audio_feedback = _generate_audio_feedback(
            clarity_metrics,
            pacing_metrics,
            base_evaluation
        )
        
        # Get hiring recommendation
        recommendation = generate_recommendation(final_score, experience_level)
        
        return {
            "status": "success",
            "overall_score": final_score,
            "content_score": base_score,
            "delivery_score": audio_score,
            "clarity_score": clarity_score,
            "pacing_score": pacing_score,
            "duration_seconds": duration_seconds,
            "transcription": transcription,
            "key_phrases": key_phrases,
            "feedback": audio_feedback,
            "strengths": base_evaluation.get("strengths", []),
            "weaknesses": base_evaluation.get("weaknesses", []),
            "suggestions": base_evaluation.get("suggestions", []),
            "recommendation": recommendation,
            "clarity_assessment": clarity_metrics.get("assessment", ""),
            "pacing_assessment": pacing_metrics.get("assessment", ""),
            "word_count": clarity_metrics.get("word_count", 0),
            "words_per_minute": pacing_metrics.get("words_per_minute", 0)
        }
    
    except Exception as e:
        print(f"Scoring error: {str(e)}")
        return _score_fallback(transcription, question)


def _generate_audio_feedback(
    clarity_metrics: Dict[str, Any],
    pacing_metrics: Dict[str, Any],
    content_evaluation: Dict[str, Any]
) -> str:
    """
    Generate feedback combining content and delivery metrics
    
    Args:
        clarity_metrics: Clarity assessment
        pacing_metrics: Pacing assessment
        content_evaluation: Content evaluation from Phase-3
        
    Returns:
        Comprehensive feedback string
    """
    feedback_parts = []
    
    # Content feedback
    content_feedback = content_evaluation.get("feedback", "")
    if content_feedback:
        feedback_parts.append(f"Content: {content_feedback}")
    
    # Clarity feedback
    clarity_score = clarity_metrics.get("clarity_score", 0)
    clarity_assessment = clarity_metrics.get("assessment", "")
    
    if clarity_score >= 80:
        feedback_parts.append(f"Excellent audio clarity and articulation. {clarity_assessment}")
    elif clarity_score >= 60:
        feedback_parts.append(f"Good audio quality. {clarity_assessment}")
    else:
        feedback_parts.append(f"Audio clarity could be improved. {clarity_assessment}")
    
    # Pacing feedback
    pacing_assessment = pacing_metrics.get("assessment", "")
    words_per_minute = pacing_metrics.get("words_per_minute", 0)
    
    if pacing_assessment:
        feedback_parts.append(f"Speaking pace: {pacing_assessment} ({words_per_minute} WPM)")
    
    # Combined feedback
    feedback = " ".join(feedback_parts)
    
    return feedback if feedback else "Answer recorded and analyzed. See detailed metrics below."


def _score_fallback(transcription: str, question: str) -> Dict[str, Any]:
    """
    Fallback scoring when evaluation fails
    
    Args:
        transcription: Transcribed text
        question: Question asked
        
    Returns:
        Fallback score dict
    """
    # Basic keyword matching
    keywords = ["experience", "system", "design", "implementation", "solution"]
    keyword_count = sum(1 for kw in keywords if kw.lower() in transcription.lower())
    
    base_score = 50 + (keyword_count * 5)  # 50-75 range
    base_score = min(100, base_score)
    
    clarity_metrics = assess_clarity(transcription)
    pacing_metrics = assess_pacing(transcription, 0.0)
    
    return {
        "status": "success",
        "overall_score": base_score,
        "content_score": base_score,
        "delivery_score": (clarity_metrics.get("clarity_score", 75) + pacing_metrics.get("pacing_score", 75)) / 2,
        "clarity_score": clarity_metrics.get("clarity_score", 75),
        "pacing_score": pacing_metrics.get("pacing_score", 75),
        "duration_seconds": 0,
        "transcription": transcription,
        "key_phrases": extract_key_phrases(transcription),
        "feedback": "Fallback scoring - detailed analysis unavailable",
        "strengths": ["Audio successfully transcribed", "Key concepts identified"],
        "weaknesses": ["Scoring system unavailable"],
        "suggestions": ["Provide more specific technical details"],
        "recommendation": "Audio processed - manual review recommended",
        "clarity_assessment": clarity_metrics.get("assessment", ""),
        "pacing_assessment": pacing_metrics.get("assessment", ""),
        "word_count": clarity_metrics.get("word_count", 0),
        "words_per_minute": pacing_metrics.get("words_per_minute", 0)
    }


def generate_audio_report(
    scored_answer: Dict[str, Any],
    candidate_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate comprehensive audio interview report
    
    Args:
        scored_answer: Result from score_spoken_answer
        candidate_name: Name of candidate (optional)
        
    Returns:
        Detailed report dict
    """
    score = scored_answer.get("overall_score", 0)
    
    if score >= 85:
        performance_level = "Excellent"
    elif score >= 75:
        performance_level = "Very Good"
    elif score >= 65:
        performance_level = "Good"
    elif score >= 50:
        performance_level = "Fair"
    else:
        performance_level = "Needs Improvement"
    
    return {
        "candidate_name": candidate_name or "Unknown",
        "overall_score": score,
        "performance_level": performance_level,
        "content_score": scored_answer.get("content_score", 0),
        "delivery_score": scored_answer.get("delivery_score", 0),
        "clarity_score": scored_answer.get("clarity_score", 0),
        "pacing_score": scored_answer.get("pacing_score", 0),
        "duration_seconds": scored_answer.get("duration_seconds", 0),
        "word_count": scored_answer.get("word_count", 0),
        "words_per_minute": scored_answer.get("words_per_minute", 0),
        "key_phrases": scored_answer.get("key_phrases", []),
        "feedback": scored_answer.get("feedback", ""),
        "strengths": scored_answer.get("strengths", []),
        "weaknesses": scored_answer.get("weaknesses", []),
        "suggestions": scored_answer.get("suggestions", []),
        "recommendation": scored_answer.get("recommendation", ""),
        "clarity_assessment": scored_answer.get("clarity_assessment", ""),
        "pacing_assessment": scored_answer.get("pacing_assessment", "")
    }


def compare_text_vs_audio(
    text_score: int,
    audio_score: int
) -> Dict[str, Any]:
    """
    Compare performance between written and spoken answers
    
    Args:
        text_score: Score from text answer (Phase-3)
        audio_score: Score from audio answer (Phase-4)
        
    Returns:
        Comparison dict
    """
    difference = audio_score - text_score
    
    if difference > 5:
        trend = "Better performance in spoken format"
    elif difference < -5:
        trend = "Better performance in written format"
    else:
        trend = "Consistent performance across formats"
    
    return {
        "text_score": text_score,
        "audio_score": audio_score,
        "difference": difference,
        "trend": trend,
        "improvement_areas": _identify_improvement_areas(text_score, audio_score)
    }


def _identify_improvement_areas(text_score: int, audio_score: int) -> list:
    """
    Identify areas where candidate can improve based on score comparison
    
    Args:
        text_score: Text-based score
        audio_score: Audio-based score
        
    Returns:
        List of improvement suggestions
    """
    suggestions = []
    
    if text_score > audio_score + 10:
        suggestions.append("Practice public speaking - speaking skills lag written skills")
        suggestions.append("Work on clarity and pacing")
        suggestions.append("Reduce verbal fillers (um, uh, like)")
    
    if audio_score > text_score + 10:
        suggestions.append("Practice written communication - writing skills need improvement")
        suggestions.append("Focus on technical writing and documentation")
    
    if text_score < 60 and audio_score < 60:
        suggestions.append("Both written and spoken answers need improvement")
        suggestions.append("Focus on deep technical knowledge and problem-solving")
        suggestions.append("Practice articulating your thoughts clearly")
    
    return suggestions

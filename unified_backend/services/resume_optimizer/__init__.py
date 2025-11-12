"""
Resume Optimization Service
- ATS scoring with keyword matching and skill analysis
- Resume rewriting and optimization for job requirements
"""

from .ats_scorer import (
    initialize_llm,
    get_structured_json_output,
    calculate_keyword_match_score,
    calculate_quantified_achievements_score,
    calculate_skills_relevance_score,
    calculate_overall_resume_score,
    perform_complete_resume_analysis,
    generate_improvement_recommendations,
    extract_resume_text,
    extract_all_bullet_points,
    extract_job_requirements,
    generate_ats_optimization_suggestions,
    get_grade
)

from .rewriter import (
    parse_job_description,
    quantify_bullet_point,
    optimize_resume_section,
    generate_targeted_resume
)

__all__ = [
    # ATS Scoring Functions
    "initialize_llm",
    "get_structured_json_output",
    "calculate_keyword_match_score",
    "calculate_quantified_achievements_score",
    "calculate_skills_relevance_score",
    "calculate_overall_resume_score",
    "perform_complete_resume_analysis",
    "generate_improvement_recommendations",
    "extract_resume_text",
    "extract_all_bullet_points",
    "extract_job_requirements",
    "generate_ats_optimization_suggestions",
    "get_grade",
    # Rewriting Functions
    "parse_job_description",
    "quantify_bullet_point",
    "optimize_resume_section",
    "generate_targeted_resume"
]
__all__ = []

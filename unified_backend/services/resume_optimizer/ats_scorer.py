"""
ATS (Applicant Tracking System) Resume Scoring Module
Calculates keyword match, quantified achievements, skills relevance, and overall ATS score
"""

import json
import os
from langchain_groq import ChatGroq
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def initialize_llm():
    """
    Initialize Groq LLM for content generation
    Requires GROQ_API_KEY environment variable
    """
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set. Please configure it.")
    
    llm = ChatGroq(
        model="mixtral-8x7b-32768",
        temperature=0.3,
        groq_api_key=api_key
    )
    return llm


def get_structured_json_output(llm, system_message, human_prompt):
    """
    Get structured JSON output from LLM with error handling
    """
    try:
        from langchain_core.messages import HumanMessage, SystemMessage
    except ImportError:
        from langchain.schema import HumanMessage, SystemMessage
    
    try:
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=human_prompt)
        ]
        
        response = llm.invoke(messages)
        response_text = response.content
        
        # Parse JSON from response
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            return json.loads(json_str)
        else:
            print(f"Warning: Could not extract JSON from response: {response_text}")
            return None
            
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from LLM response: {e}")
        return None
    except Exception as e:
        print(f"Error getting structured output from LLM: {e}")
        return None


def calculate_keyword_match_score(resume_text, job_description):
    """
    Calculate keyword match score between resume and job description using TF-IDF
    Returns: keyword_match_score (0-100), matched_keywords, missing_keywords
    """
    print("--- Calculating Keyword Match Score ---")
    
    try:
        # Combine texts for TF-IDF
        texts = [resume_text, job_description]
        vectorizer = TfidfVectorizer(stop_words='english', max_features=100)
        tfidf_matrix = vectorizer.fit_transform(texts)
        
        # Calculate cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        keyword_match_score = min(similarity[0][0] * 100, 100)
        
        # Extract top keywords from job description
        job_tfidf = tfidf_matrix[1]
        feature_names = vectorizer.get_feature_names_out()
        
        job_keywords = []
        resume_keywords = []
        
        # Get job description keywords
        job_indices = job_tfidf.nonzero()[1]
        if len(job_indices) > 0:
            job_scores = zip(job_indices, job_tfidf.data)
            job_scores = sorted(job_scores, key=lambda x: x[1], reverse=True)
            job_keywords = [feature_names[i] for i, _ in job_scores[:20]]
        
        # Get resume keywords
        resume_tfidf = tfidf_matrix[0]
        resume_indices = resume_tfidf.nonzero()[1]
        if len(resume_indices) > 0:
            resume_scores = zip(resume_indices, resume_tfidf.data)
            resume_scores = sorted(resume_scores, key=lambda x: x[1], reverse=True)
            resume_keywords = [feature_names[i] for i, _ in resume_scores[:20]]
        
        # Find matched and missing keywords
        matched_keywords = list(set(job_keywords) & set(resume_keywords))
        missing_keywords = list(set(job_keywords) - set(resume_keywords))
        
        match_percentage = (len(matched_keywords) / len(job_keywords) * 100) if job_keywords else 0
        
        return {
            "keyword_match_score": round(keyword_match_score, 2),
            "match_percentage": round(match_percentage, 2),
            "matched_keywords": matched_keywords[:10],
            "missing_keywords": missing_keywords[:10],
            "total_job_keywords": len(job_keywords),
            "resume_keywords_count": len(resume_keywords)
        }
        
    except Exception as e:
        print(f"Error calculating keyword match: {e}")
        return {"keyword_match_score": 0, "matched_keywords": [], "missing_keywords": []}


def calculate_quantified_achievements_score(bullet_points, llm):
    """
    Calculate percentage of quantified achievements in resume
    """
    print("--- Calculating Quantified Achievements Score ---")
    
    system_message = """
    You are a resume analysis expert. Analyze bullet points and identify
    which ones contain quantified achievements (numbers, percentages, metrics).
    Return only JSON with the analysis.
    """
    
    human_prompt = f"""
    Analyze these resume bullet points and identify which contain quantified achievements:
    {json.dumps(bullet_points, indent=2)}
    
    Return JSON with:
    - total_bullet_points: total number of bullet points
    - quantified_bullet_points: list of bullet points with quantifications
    - non_quantified_bullet_points: list of bullet points without quantifications
    - quantification_percentage: percentage of bullet points that are quantified
    - suggestions: suggestions for adding quantification to non-quantified points
    """
    
    analysis = get_structured_json_output(llm, system_message, human_prompt)
    
    if analysis:
        # Calculate score based on quantification percentage
        quant_percentage = analysis.get('quantification_percentage', 0)
        quant_score = min(quant_percentage, 100)  # Cap at 100
        
        analysis['quantified_achievements_score'] = round(quant_score, 2)
    
    return analysis


def calculate_skills_relevance_score(resume_skills, job_requirements, llm):
    """
    Calculate skills relevance score between resume and job requirements
    """
    print("--- Calculating Skills Relevance Score ---")
    
    system_message = """
    You are a skills matching expert. Compare resume skills with job requirements
    and calculate a relevance score. Identify skill gaps and strengths.
    """
    
    human_prompt = f"""
    Resume Skills: {json.dumps(resume_skills, indent=2)}
    
    Job Requirements: {json.dumps(job_requirements, indent=2)}
    
    Analyze and provide:
    - matched_skills: skills that directly match job requirements
    - transferable_skills: skills that could be relevant with reframing
    - missing_skills: important skills missing from resume
    - skills_relevance_score: percentage score (0-100)
    - gap_analysis: detailed analysis of skill gaps
    - strength_analysis: analysis of strongest matching skills
    
    Return as JSON object.
    """
    
    return get_structured_json_output(llm, system_message, human_prompt)


def generate_ats_optimization_suggestions(resume_data, job_description, llm):
    """
    Generate ATS optimization suggestions for the resume
    """
    print("--- Generating ATS Optimization Suggestions ---")
    
    system_message = """
    You are an ATS (Applicant Tracking System) optimization expert.
    Analyze the resume against the job description and provide specific
    suggestions to improve ATS compatibility and ranking.
    """
    
    human_prompt = f"""
    Resume Data:
    {json.dumps(resume_data, indent=2)}
    
    Job Description:
    {job_description}
    
    Provide ATS optimization suggestions including:
    - keyword_optimization: specific keywords to add
    - section_improvements: how to improve each section
    - formatting_recommendations: ATS-friendly formatting tips
    - content_enhancements: how to better match job requirements
    - ranking_improvements: strategies to improve ATS ranking
    
    Return as JSON object.
    """
    
    return get_structured_json_output(llm, system_message, human_prompt)


def calculate_overall_resume_score(keyword_score, quant_score, skills_score):
    """
    Calculate overall resume score with weighted components
    """
    print("--- Calculating Overall Resume Score ---")
    
    # Weighted scoring (adjust weights as needed)
    weights = {
        'keyword_match': 0.4,      # 40% weight to keyword matching
        'quantified_achievements': 0.3,  # 30% weight to quantified achievements
        'skills_relevance': 0.3     # 30% weight to skills relevance
    }
    
    overall_score = (
        keyword_score * weights['keyword_match'] +
        quant_score * weights['quantified_achievements'] +
        skills_score * weights['skills_relevance']
    )
    
    return {
        "overall_score": round(overall_score, 2),
        "score_breakdown": {
            "keyword_match_score": keyword_score,
            "quantified_achievements_score": quant_score,
            "skills_relevance_score": skills_score
        },
        "weights_applied": weights,
        "grade": get_grade(overall_score)
    }


def get_grade(score):
    """Convert numerical score to letter grade"""
    if score >= 90: return "A+"
    elif score >= 85: return "A"
    elif score >= 80: return "A-"
    elif score >= 75: return "B+"
    elif score >= 70: return "B"
    elif score >= 65: return "B-"
    elif score >= 60: return "C+"
    elif score >= 55: return "C"
    else: return "Needs Improvement"


def extract_resume_text(resume_data):
    """Extract all text from resume data for keyword analysis"""
    text_parts = []
    
    # Add skills
    text_parts.extend(resume_data.get('skills', []))
    
    # Add experience
    for exp in resume_data.get('experience', []):
        text_parts.append(exp.get('role', ''))
        text_parts.append(exp.get('company', ''))
        text_parts.append(exp.get('description', ''))
        text_parts.extend(exp.get('bulletPoints', []))
    
    # Add education
    for edu in resume_data.get('education', []):
        text_parts.append(edu.get('degree', ''))
        text_parts.append(edu.get('institution', ''))
    
    return ' '.join(text_parts)


def extract_all_bullet_points(resume_data):
    """Extract all bullet points from resume"""
    bullet_points = []
    
    for exp in resume_data.get('experience', []):
        bullet_points.extend(exp.get('bulletPoints', []))
    
    return bullet_points


def extract_job_requirements(job_description):
    """Extract key requirements from job description (simplified)"""
    requirements = []
    
    # Look for common requirement indicators
    requirement_phrases = [
        "requirements:", "qualifications:", "must have", "should have", 
        "required skills", "looking for", "ideal candidate"
    ]
    
    lines = job_description.split('\n')
    for line in lines:
        if any(phrase in line.lower() for phrase in requirement_phrases):
            requirements.append(line)
    
    return requirements if requirements else [job_description]


def generate_improvement_recommendations(keyword_analysis, quant_analysis, skills_analysis):
    """Generate actionable improvement recommendations"""
    recommendations = []
    
    # Keyword recommendations
    if keyword_analysis.get('match_percentage', 0) < 80:
        recommendations.append({
            "category": "Keywords",
            "priority": "High",
            "suggestion": f"Add missing keywords: {', '.join(keyword_analysis.get('missing_keywords', [])[:5])}",
            "impact": "High"
        })
    
    # Quantification recommendations
    if quant_analysis and quant_analysis.get('quantification_percentage', 0) < 60:
        recommendations.append({
            "category": "Quantification",
            "priority": "High",
            "suggestion": "Add metrics and numbers to bullet points to show impact",
            "impact": "High"
        })
    
    # Skills recommendations
    if skills_analysis and skills_analysis.get('skills_relevance_score', 0) < 70:
        recommendations.append({
            "category": "Skills",
            "priority": "Medium",
            "suggestion": "Highlight transferable skills and consider acquiring missing high-demand skills",
            "impact": "Medium"
        })
    
    return recommendations


def perform_complete_resume_analysis(resume_data, job_description):
    """
    Perform complete resume analysis and scoring
    """
    print("=== Performing Complete Resume Analysis ===")
    
    llm = initialize_llm()
    
    # Extract text for keyword matching
    resume_text = extract_resume_text(resume_data)
    
    # Calculate individual scores
    keyword_analysis = calculate_keyword_match_score(resume_text, job_description)
    quant_analysis = calculate_quantified_achievements_score(
        extract_all_bullet_points(resume_data), llm
    )
    skills_analysis = calculate_skills_relevance_score(
        resume_data.get('skills', []), 
        extract_job_requirements(job_description),
        llm
    )
    
    # Extract scores
    keyword_score = keyword_analysis.get('keyword_match_score', 0)
    quant_score = quant_analysis.get('quantified_achievements_score', 0) if quant_analysis else 0
    skills_score = skills_analysis.get('skills_relevance_score', 0) if skills_analysis else 0
    
    # Calculate overall score
    overall_analysis = calculate_overall_resume_score(keyword_score, quant_score, skills_score)
    
    # Get ATS optimization suggestions
    ats_suggestions = generate_ats_optimization_suggestions(resume_data, job_description, llm)
    
    return {
        "overall_analysis": overall_analysis,
        "keyword_analysis": keyword_analysis,
        "quantification_analysis": quant_analysis,
        "skills_analysis": skills_analysis,
        "ats_optimization_suggestions": ats_suggestions,
        "improvement_recommendations": generate_improvement_recommendations(
            keyword_analysis, quant_analysis, skills_analysis
        )
    }

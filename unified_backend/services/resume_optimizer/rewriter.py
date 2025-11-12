"""
Resume Optimization and Rewriting Module
Parses job descriptions and rewrites resume content for better matching
"""

import json
import os
from langchain_groq import ChatGroq


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
        temperature=0.7,
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
            # Try to find array
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            
            print(f"Warning: Could not extract JSON from response: {response_text}")
            return None
            
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from LLM response: {e}")
        return None
    except Exception as e:
        print(f"Error getting structured output from LLM: {e}")
        return None


def parse_job_description(job_description, llm=None):
    """
    Parse job description to extract key requirements, skills, and responsibilities
    """
    print("--- Parsing Job Description ---")
    
    if llm is None:
        llm = initialize_llm()
    
    system_message = """
    You are an expert recruiter and career coach. Parse job descriptions to 
    extract key information that will help someone tailor their resume.
    Return only valid JSON.
    """
    
    human_prompt = f"""
    Parse this job description and extract:
    - required_skills: list of required technical skills
    - nice_to_have_skills: optional but valuable skills
    - key_responsibilities: 5-7 main job responsibilities
    - required_experience: years and type of experience needed
    - keywords: important keywords for ATS matching
    - role_title: the job title
    - seniority_level: entry/mid/senior
    
    Job Description:
    {job_description}
    
    Return as JSON object.
    """
    
    parsed_data = get_structured_json_output(llm, system_message, human_prompt)
    
    return parsed_data


def quantify_bullet_point(bullet_point, llm=None):
    """
    Rewrite a resume bullet point to be more quantified and impactful
    Returns 3 alternative versions with metrics
    """
    print("--- Quantifying Bullet Point ---")
    
    if llm is None:
        llm = initialize_llm()
    
    system_message = """
    You are an expert resume writer. Rewrite vague resume bullet points 
    to include specific metrics, percentages, and quantified results.
    You may invent reasonable metrics if none were provided.
    Return a JSON array with 3 different rewritten versions.
    """
    
    human_prompt = f"""
    Rewrite this bullet point to be more quantified and impactful.
    Provide 3 alternatives as a JSON array of strings.
    Original bullet point: "{bullet_point}"
    
    Rewrite this to show impact. Invent reasonable metrics 
    if necessary. Provide 3 alternatives as a JSON list.
    """
    
    rewrites = get_structured_json_output(llm, system_message, human_prompt)
    
    if rewrites and isinstance(rewrites, list):
        return {
            "original": bullet_point,
            "rewrites": rewrites,
            "recommendation": rewrites[0] if rewrites else None
        }
    elif rewrites and isinstance(rewrites, dict):
        return rewrites
    else:
        return {
            "original": bullet_point,
            "rewrites": [],
            "error": "Could not generate rewrites"
        }


def optimize_resume_section(section_name, section_content, job_requirements, llm=None):
    """
    Optimize a specific resume section based on job requirements
    """
    print(f"--- Optimizing {section_name} Section ---")
    
    if llm is None:
        llm = initialize_llm()
    
    system_message = f"""
    You are an expert resume writer specializing in {section_name} optimization.
    Improve this section to better match job requirements while keeping it truthful.
    Return only valid JSON.
    """
    
    human_prompt = f"""
    Section Name: {section_name}
    Current Content: {section_content}
    Job Requirements: {json.dumps(job_requirements, indent=2)}
    
    Provide:
    - improved_content: optimized version of the section
    - keywords_added: keywords that were incorporated
    - changes_made: list of specific improvements made
    - relevance_score: how well it now matches job requirements (0-100)
    
    Return as JSON object.
    """
    
    return get_structured_json_output(llm, system_message, human_prompt)


def generate_targeted_resume(resume_data, job_description, llm=None):
    """
    Generate a complete targeted resume optimized for a specific job
    """
    print("=== Generating Targeted Resume ===")
    
    if llm is None:
        llm = initialize_llm()
    
    # Parse job description
    job_parsed = parse_job_description(job_description, llm)
    
    if not job_parsed:
        return {"error": "Could not parse job description"}
    
    system_message = """
    You are an expert resume writer. Create a resume that is specifically 
    tailored to match the provided job description while staying truthful 
    to the candidate's actual experience.
    Return only valid JSON.
    """
    
    human_prompt = f"""
    Create an optimized resume for this candidate targeting this job:
    
    Candidate Resume:
    {json.dumps(resume_data, indent=2)}
    
    Target Job Requirements:
    {json.dumps(job_parsed, indent=2)}
    
    Provide an optimized resume with:
    - professional_summary: tailored professional summary (2-3 sentences)
    - experience: rewritten experience section with relevant keywords
    - skills: reorganized skills list prioritizing job requirements
    - keywords_for_ats: important keywords incorporated
    - changes_summary: key changes made to match the job
    
    Return as JSON object.
    """
    
    optimized_resume = get_structured_json_output(llm, system_message, human_prompt)
    
    if optimized_resume:
        optimized_resume["target_job_requirements"] = job_parsed
        optimized_resume["optimization_summary"] = {
            "status": "success",
            "job_description_parsed": True,
            "optimization_applied": True
        }
    
    return optimized_resume

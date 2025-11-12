"""
Interview Question Generator Module
Generates contextual interview questions based on resume, role, and skills
"""

import os
import re
from typing import List, Optional
from langchain_groq import ChatGroq

try:
    from langchain_core.messages import HumanMessage, SystemMessage
except ImportError:
    from langchain.schema import HumanMessage, SystemMessage


def initialize_llm():
    """Initialize Groq LLM for question generation"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set. Please configure it.")
    
    llm = ChatGroq(
        model="mixtral-8x7b-32768",
        temperature=0.7,
        groq_api_key=api_key
    )
    return llm


def generate_questions(
    role: str,
    experience_level: str,
    skills: Optional[List[str]] = None,
    num_questions: int = 30,
    resume_content: Optional[str] = None,
    llm=None
) -> List[str]:
    """
    Generate technical interview questions based on role and skills
    
    Args:
        role: Job role (e.g., "Senior Software Engineer")
        experience_level: Entry/Mid/Senior level
        skills: List of key technical skills
        num_questions: Number of questions to generate
        resume_content: Optional resume text for context
        llm: Optional pre-initialized LLM instance
    
    Returns:
        List of interview questions
    """
    if llm is None:
        llm = initialize_llm()
    
    # Build context
    skills_str = ", ".join(skills) if skills else "General technical skills"
    context = f"""
    Role: {role}
    Experience Level: {experience_level}
    Key Skills: {skills_str}
    """
    
    if resume_content:
        context += f"\nResume Background:\n{resume_content[:500]}"
    
    # Generate questions using LLM
    system_message = """You are an expert technical interviewer. Generate high-quality, 
    contextual interview questions that assess both technical competency and problem-solving ability.
    
    Rules:
    1. Format each question as a clean numbered list
    2. Mix technical, behavioral, and scenario-based questions
    3. Questions should be specific to the candidate's experience level
    4. Each question should be on a new line
    5. Return ONLY the questions, no numbering prefix, no explanations
    """
    
    human_prompt = f"""Generate exactly {num_questions} interview questions for:
    {context}
    
    Return the questions as a numbered list (1. Question? 2. Question? etc.)
    Only return questions, nothing else."""
    
    try:
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=human_prompt)
        ]
        
        response = llm.invoke(messages)
        content = response.content
        
        # Extract questions from response
        questions = []
        
        # Try to find numbered questions
        pattern = r'\d+\.\s*(.+?)(?=\n\d+\.|$)'
        matches = re.findall(pattern, content, re.DOTALL)
        
        if matches:
            questions = [q.strip().rstrip('?') + '?' if not q.strip().endswith('?') 
                        else q.strip() for q in matches]
        else:
            # Fallback: split by newlines and filter
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            questions = [q for q in lines if len(q) > 10]
        
        # Return requested number of questions
        return questions[:num_questions]
        
    except Exception as e:
        print(f"Error generating questions: {e}")
        return generate_default_questions(role, experience_level, skills, num_questions)


def generate_default_questions(
    role: str,
    experience_level: str,
    skills: Optional[List[str]] = None,
    num_questions: int = 30
) -> List[str]:
    """
    Generate default questions when LLM fails
    Fallback to predefined question templates
    """
    
    questions = [
        # Technical Foundation
        "Explain the difference between a stack and a queue, and when you would use each.",
        "What is time complexity and how do you calculate it for an algorithm?",
        "Describe the SOLID principles and provide an example of each.",
        "What is polymorphism and how does it differ from inheritance?",
        "Explain the concept of memoization and when it's beneficial.",
        
        # System Design
        "How would you design a URL shortening service like Bit.ly?",
        "Design a chat application that supports one-to-one messaging.",
        "How would you design a search engine like Google?",
        "Explain how you would scale a social media feed.",
        "Design a real-time notification system.",
        
        # Problem Solving
        "Given an unsorted array, find the missing number. Optimize for space complexity.",
        "Implement a function to check if a string is a valid palindrome.",
        "How would you detect a cycle in a linked list?",
        "Write code to reverse a binary tree.",
        "Implement a least recently used (LRU) cache.",
        
        # Behavioral
        "Tell me about a challenging project and how you overcame obstacles.",
        "How do you approach learning new technologies?",
        "Describe a time you had to work with a difficult team member.",
        "How do you prioritize when you have multiple tasks?",
        "Tell me about your greatest professional achievement.",
        
        # Role-Specific
        "What's your experience with microservices architecture?",
        "How do you approach database optimization?",
        "Explain CI/CD pipelines and their importance.",
        "What's your experience with containerization (Docker/Kubernetes)?",
        "How do you ensure code quality in your projects?",
        
        # Situational
        "How would you debug a slow application?",
        "Describe your approach to writing maintainable code.",
        "How do you handle technical debt?",
        "What's your experience with agile methodologies?",
        "How do you approach code reviews?"
    ]
    
    # Filter by experience level if needed
    if experience_level.lower() == "entry":
        questions = questions[:20]  # Simpler questions
    elif experience_level.lower() == "mid":
        questions = questions[5:25]  # Mix of all types
    else:  # senior
        questions = questions[10:]  # More advanced
    
    return questions[:num_questions]


def generate_mock_interview_session(
    role: str,
    experience_level: str,
    skills: Optional[List[str]] = None,
    resume_content: Optional[str] = None,
    duration_minutes: int = 60
) -> dict:
    """
    Generate a complete mock interview session plan
    
    Args:
        role: Target role
        experience_level: Experience level
        skills: Key skills
        resume_content: Resume background
        duration_minutes: Interview duration
    
    Returns:
        Dictionary with interview plan
    """
    
    # Calculate question distribution
    minutes_per_question = 3
    num_questions = min(duration_minutes // minutes_per_question, 20)
    
    # Generate questions
    questions = generate_questions(
        role, experience_level, skills, num_questions, resume_content
    )
    
    return {
        "session_id": os.urandom(8).hex(),
        "role": role,
        "experience_level": experience_level,
        "duration_minutes": duration_minutes,
        "total_questions": len(questions),
        "questions_per_section": {
            "technical": len(questions) // 3,
            "behavioral": len(questions) // 3,
            "system_design": len(questions) // 3 + (len(questions) % 3)
        },
        "questions": questions,
        "status": "ready",
        "timestamp": str(os.popen("date").read().strip())
    }

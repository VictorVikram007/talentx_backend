# Resume Parser Service
"""
Resume Parser Service Package

Exports all parser functions for resume extraction and parsing:
- file_parser: Extract text from PDF, DOCX, TXT files
- linkedin_parser: Parse LinkedIn profiles
- github_parser: Parse GitHub profiles and repositories
- ollama_parser: Parse resumes using local LLM
"""

from .file_parser import extract_text_from_file, get_text_preview, get_text_summary
from .linkedin_parser import parse_linkedin_profile, validate_linkedin_url
from .github_parser import parse_github_profile, get_user_stats
from .ollama_parser import parse_resume_with_ollama, check_ollama_available, get_available_models

__all__ = [
    "extract_text_from_file",
    "get_text_preview",
    "get_text_summary",
    "parse_linkedin_profile",
    "validate_linkedin_url",
    "parse_github_profile",
    "get_user_stats",
    "parse_resume_with_ollama",
    "check_ollama_available",
    "get_available_models"
]

"""
Ollama Resume Parser Module

This module uses a local LLM (via Ollama) to convert unstructured resume text
into structured JSON format.

You are an AI resume parser. 
Extract key details from the following text and return them as JSON with fields:
name, email, phone, education, experience, skills, and achievements.
Text:
'''<raw_text>'''

Expected output format:
{
  "name": "John Doe",
  "email": "john.doe@gmail.com",
  "phone": "+1-555-0123",
  "skills": ["Python", "Machine Learning", "FastAPI"],
  "experience": ["Software Engineer at XYZ (2021–Present)"],
  "education": ["B.Tech Computer Science - 2020"],
  "achievements": ["Developed an AI chatbot with 10,000+ users"]
}
"""

import subprocess
import json
import re
from typing import Dict, Any, Optional


def parse_resume_with_ollama(raw_text: str, model: str = "mistral") -> Dict[str, Any]:
    """
    Parse resume text using Ollama local LLM.
    
    Args:
        raw_text (str): Raw resume text to parse
        model (str): Ollama model to use (default: "mistral")
        
    Returns:
        dict: Structured resume data with keys: name, email, phone, 
              education, experience, skills, achievements
              
    Raises:
        ValueError: If Ollama is not installed or model unavailable
        json.JSONDecodeError: If model output is invalid JSON
    """
    
    if not raw_text or not raw_text.strip():
        return _get_empty_structure()
    
    # Construct the prompt
    prompt = f"""You are an AI resume parser. Extract key details from the following text and return them as valid JSON with these fields: name, email, phone, education, experience, skills, and achievements. 

Return ONLY valid JSON, no additional text.

Resume Text:
{raw_text}

JSON Output:"""
    
    try:
        # Call Ollama via subprocess
        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            raise ValueError(f"Ollama error: {error_msg}")
        
        # Extract and clean the response
        response_text = result.stdout.strip()
        
        # Parse JSON from response
        structured_data = _extract_json_from_response(response_text)
        
        # Validate and fill missing fields
        validated_data = _validate_structure(structured_data)
        
        return validated_data
        
    except FileNotFoundError:
        raise ValueError(
            "Ollama is not installed or not in PATH. "
            "Please install Ollama from https://ollama.ai"
        )
    except subprocess.TimeoutExpired:
        raise ValueError("Ollama request timed out (60 seconds)")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from Ollama: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error parsing resume with Ollama: {str(e)}")


def _extract_json_from_response(response: str) -> Dict[str, Any]:
    """
    Extract JSON from Ollama response, handling various formats.
    
    Args:
        response (str): Raw response from Ollama
        
    Returns:
        dict: Parsed JSON data
        
    Raises:
        json.JSONDecodeError: If no valid JSON found
    """
    
    # Remove common prefixes/suffixes
    cleaned = response.strip()
    
    # Remove common phrases like "Here is the JSON:" or "```json"
    phrases_to_remove = [
        "Here is the JSON:",
        "Here's the JSON:",
        "```json",
        "```",
        "json",
        "The JSON output is:",
        "The resume information in JSON format:"
    ]
    
    for phrase in phrases_to_remove:
        cleaned = cleaned.replace(phrase, "")
    
    cleaned = cleaned.strip()
    
    # Try to find JSON object in curly braces
    # Find first { and last }
    start_idx = cleaned.find('{')
    end_idx = cleaned.rfind('}')
    
    if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
        json_str = cleaned[start_idx:end_idx + 1]
    else:
        json_str = cleaned
    
    # Parse JSON
    parsed = json.loads(json_str)
    
    if not isinstance(parsed, dict):
        raise json.JSONDecodeError("Response is not a JSON object", json_str, 0)
    
    return parsed


def _validate_structure(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and normalize resume structure, filling missing fields.
    
    Args:
        data (dict): Parsed data from Ollama
        
    Returns:
        dict: Validated structure with all required fields
    """
    
    # Define expected fields with default values
    expected_fields = {
        "name": "",
        "email": "",
        "phone": "",
        "education": [],
        "experience": [],
        "skills": [],
        "achievements": []
    }
    
    # Ensure all fields exist and are correct type
    validated = {}
    
    for field, default in expected_fields.items():
        if field in data:
            value = data[field]
            
            # Normalize list fields
            if isinstance(default, list):
                if isinstance(value, list):
                    # Convert all items to strings
                    validated[field] = [str(item) for item in value if item]
                elif isinstance(value, str):
                    # Convert single string to list
                    validated[field] = [value] if value.strip() else []
                else:
                    validated[field] = []
            else:
                # String fields
                if isinstance(value, list):
                    # Join list into string
                    validated[field] = " ".join(str(item) for item in value)
                else:
                    validated[field] = str(value).strip() if value else ""
        else:
            # Use default value for missing fields
            validated[field] = default
    
    return validated


def _get_empty_structure() -> Dict[str, Any]:
    """
    Return empty resume structure with all required fields.
    
    Returns:
        dict: Empty structure
    """
    return {
        "name": "",
        "email": "",
        "phone": "",
        "education": [],
        "experience": [],
        "skills": [],
        "achievements": []
    }


def check_ollama_available() -> bool:
    """
    Check if Ollama is installed and available.
    
    Returns:
        bool: True if Ollama is available, False otherwise
    """
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def get_available_models() -> list:
    """
    Get list of available Ollama models.
    
    Returns:
        list: Available model names
    """
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return []
        
        # Parse output (format: "NAME     ID     SIZE     MODIFIED")
        models = []
        lines = result.stdout.strip().split('\n')[1:]  # Skip header
        
        for line in lines:
            if line.strip():
                parts = line.split()
                if parts:
                    models.append(parts[0])
        
        return models
        
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []

"""
LinkedIn Parser Module for Extracting Profile Information

Currently implements mock data structure for LinkedIn profiles.
In the future, this can be extended with actual web scraping or LinkedIn API integration.
"""


def parse_linkedin_profile(url: str) -> dict:
    """
    Parse LinkedIn profile information from a URL.
    
    Args:
        url (str): LinkedIn profile URL
        
    Returns:
        dict: Profile information including name, headline, skills, and experience
        
    Raises:
        ValueError: If URL is invalid or empty
    """
    if not url:
        raise ValueError("LinkedIn URL cannot be empty")
    
    if not isinstance(url, str):
        raise ValueError("LinkedIn URL must be a string")
    
    # Validate that it's a LinkedIn URL
    if "linkedin.com" not in url.lower():
        raise ValueError("Invalid LinkedIn URL. Must contain 'linkedin.com'")
    
    # Extract username or profile identifier from URL
    try:
        # Example URL: https://www.linkedin.com/in/john-doe/
        profile_identifier = _extract_linkedin_identifier(url)
    except Exception as e:
        profile_identifier = "unknown"
    
    # Return mock profile data structure
    # This serves as a placeholder for future implementation with actual LinkedIn data
    mock_profile = {
        "url": url,
        "profile_identifier": profile_identifier,
        "name": "Example Name",
        "headline": "AI Enthusiast | Machine Learning Engineer",
        "bio": "Passionate about AI and software engineering",
        "location": "San Francisco, CA",
        "skills": [
            "Python",
            "Machine Learning",
            "FastAPI",
            "Data Analysis",
            "Backend Development"
        ],
        "experience": "3+ years backend development",
        "education": "Computer Science",
        "endorsements": 0,
        "connections": 0,
        "status": "mock_data",
        "note": "This is mock data. To fetch real LinkedIn data, implement web scraping or use LinkedIn API."
    }
    
    return mock_profile


def _extract_linkedin_identifier(url: str) -> str:
    """
    Extract the profile identifier from a LinkedIn URL.
    
    Args:
        url (str): LinkedIn profile URL
        
    Returns:
        str: Extracted profile identifier
    """
    try:
        # Remove trailing slashes
        url = url.rstrip('/')
        
        # Extract the last part of the URL (profile slug)
        parts = url.split('/')
        identifier = parts[-1] if parts else "unknown"
        
        return identifier
    except Exception:
        return "unknown"


def validate_linkedin_url(url: str) -> bool:
    """
    Validate if the provided string is a valid LinkedIn URL format.
    
    Args:
        url (str): URL to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    
    url_lower = url.lower()
    
    # Check if it's a LinkedIn URL
    if "linkedin.com" not in url_lower:
        return False
    
    # Check for valid LinkedIn URL patterns
    valid_patterns = [
        "/in/",      # LinkedIn profile
        "/company/", # LinkedIn company
        "/jobs/",    # LinkedIn job
    ]
    
    return any(pattern in url_lower for pattern in valid_patterns)

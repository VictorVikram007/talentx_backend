"""
GitHub Parser Module for Extracting Profile Information

Uses the GitHub public API to fetch user profile data and repository information.
Returns user info, biography, followers, and top repositories by star count.
"""

import requests
from typing import Optional, List, Dict, Any


# GitHub API base URL
GITHUB_API_BASE = "https://api.github.com"


def parse_github_profile(username: str) -> dict:
    """
    Parse GitHub profile information for a given username.
    
    Args:
        username (str): GitHub username
        
    Returns:
        dict: Profile information including name, bio, followers, and top repositories
        
    Raises:
        ValueError: If username is invalid
        requests.exceptions.RequestException: If API request fails
    """
    if not username or not isinstance(username, str):
        raise ValueError("GitHub username must be a non-empty string")
    
    # Validate username format (GitHub usernames are alphanumeric and hyphens)
    if not _is_valid_github_username(username):
        raise ValueError(
            "Invalid GitHub username. Usernames can only contain alphanumeric characters and hyphens."
        )
    
    try:
        # Fetch user profile data
        user_data = _fetch_user_data(username)
        
        # Fetch user repositories
        repos_data = _fetch_user_repos(username)
        
        # Get top 3 repositories by star count
        top_repos = _get_top_repos(repos_data, limit=3)
        
        # Construct the response
        profile = {
            "status": "success",
            "username": username,
            "name": user_data.get("name", "N/A"),
            "bio": user_data.get("bio", "N/A"),
            "avatar_url": user_data.get("avatar_url", ""),
            "profile_url": user_data.get("html_url", ""),
            "location": user_data.get("location", "N/A"),
            "blog": user_data.get("blog", "N/A"),
            "email": user_data.get("email", "N/A"),
            "followers": user_data.get("followers", 0),
            "following": user_data.get("following", 0),
            "public_repos": user_data.get("public_repos", 0),
            "created_at": user_data.get("created_at", ""),
            "updated_at": user_data.get("updated_at", ""),
            "top_repositories": top_repos,
            "api_response_time": "N/A"
        }
        
        return profile
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise ValueError(f"GitHub user '{username}' not found")
        raise
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch GitHub profile for '{username}': {str(e)}")


def _fetch_user_data(username: str) -> dict:
    """
    Fetch user profile data from GitHub API.
    
    Args:
        username (str): GitHub username
        
    Returns:
        dict: User profile data
    """
    url = f"{GITHUB_API_BASE}/users/{username}"
    headers = _get_api_headers()
    
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    
    return response.json()


def _fetch_user_repos(username: str, per_page: int = 100) -> List[dict]:
    """
    Fetch user repositories from GitHub API.
    
    Args:
        username (str): GitHub username
        per_page (int): Number of repos per page (max 100)
        
    Returns:
        list: List of repository data
    """
    url = f"{GITHUB_API_BASE}/users/{username}/repos"
    headers = _get_api_headers()
    params = {
        "per_page": per_page,
        "sort": "updated",
        "direction": "desc"
    }
    
    response = requests.get(url, headers=headers, params=params, timeout=10)
    response.raise_for_status()
    
    return response.json()


def _get_top_repos(repos: List[dict], limit: int = 3) -> List[dict]:
    """
    Get top repositories by star count.
    
    Args:
        repos (list): List of repository data
        limit (int): Number of top repos to return
        
    Returns:
        list: Top repositories sorted by star count
    """
    # Sort by star count (descending)
    sorted_repos = sorted(repos, key=lambda x: x.get("stargazers_count", 0), reverse=True)
    
    # Extract relevant information for top repos
    top_repos = []
    for repo in sorted_repos[:limit]:
        top_repos.append({
            "name": repo.get("name", ""),
            "url": repo.get("html_url", ""),
            "description": repo.get("description", ""),
            "stars": repo.get("stargazers_count", 0),
            "forks": repo.get("forks_count", 0),
            "language": repo.get("language", "N/A"),
            "updated_at": repo.get("updated_at", "")
        })
    
    return top_repos


def _get_api_headers() -> dict:
    """
    Get headers for GitHub API requests.
    Includes User-Agent for API compatibility.
    
    Returns:
        dict: Headers for API requests
    """
    return {
        "User-Agent": "AI-Resume-Maker-Backend",
        "Accept": "application/vnd.github.v3+json"
    }


def _is_valid_github_username(username: str) -> bool:
    """
    Validate GitHub username format.
    
    GitHub usernames can contain alphanumeric characters and hyphens,
    but cannot start with a hyphen or contain consecutive hyphens.
    
    Args:
        username (str): Username to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not username or len(username) < 1:
        return False
    
    # Username must be between 1 and 39 characters
    if len(username) > 39:
        return False
    
    # Cannot start with hyphen
    if username.startswith('-'):
        return False
    
    # Cannot end with hyphen
    if username.endswith('-'):
        return False
    
    # Cannot have consecutive hyphens
    if '--' in username:
        return False
    
    # Can only contain alphanumeric and hyphens
    import re
    if not re.match(r'^[a-zA-Z0-9-]+$', username):
        return False
    
    return True


def get_user_stats(username: str) -> dict:
    """
    Get summary statistics for a GitHub user.
    
    Args:
        username (str): GitHub username
        
    Returns:
        dict: User statistics
    """
    try:
        profile = parse_github_profile(username)
        
        stats = {
            "username": username,
            "followers": profile.get("followers", 0),
            "following": profile.get("following", 0),
            "public_repos": profile.get("public_repos", 0),
            "top_repo_stars": profile.get("top_repositories", [{}])[0].get("stars", 0) if profile.get("top_repositories") else 0
        }
        
        return stats
    except Exception as e:
        raise Exception(f"Error getting GitHub user stats: {str(e)}")

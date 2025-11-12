# Configuration & Constants
import os
from pathlib import Path

# Directories
BASE_DIR = Path(__file__).parent.parent
SAMPLES_DIR = BASE_DIR / "samples"
DATA_DIR = BASE_DIR / "data"

# Create directories if they don't exist
SAMPLES_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# API Configuration
API_TITLE = "AI Talent Platform - Unified Backend"
API_VERSION = "2.0.0"
API_DESCRIPTION = "Unified backend combining resume parsing, optimization, interview generation, and audio processing"

# Supported file types
ALLOWED_RESUME_EXTENSIONS = {".pdf", ".docx", ".txt"}
ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg"}

# Pagination
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100

# File Upload Limits
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_AUDIO_SIZE = 50 * 1024 * 1024  # 50 MB

# CORS
CORS_ORIGINS = ["*"]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]

# Ollama Configuration
OLLAMA_DEFAULT_MODEL = "mistral"
OLLAMA_TIMEOUT = 60

# Resume Optimization
ATS_MIN_SCORE = 0
ATS_MAX_SCORE = 100

# Interview Configuration
DEFAULT_QUESTION_COUNT = 5
DEFAULT_DIFFICULTY = "medium"  # easy, medium, hard

# Audio Processing
AUDIO_SAMPLE_RATE = 16000
AUDIO_CHUNK_DURATION = 30  # seconds

print(f"✅ Configuration loaded")
print(f"   Base directory: {BASE_DIR}")
print(f"   Samples directory: {SAMPLES_DIR}")
print(f"   Data directory: {DATA_DIR}")

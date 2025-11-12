# 🚀 Unified Backend - AI Talent Platform

## Overview

This is a **unified FastAPI backend** combining multiple modules into a single, production-ready application:

- ✅ **Resume Parsing** - File upload (PDF/DOCX/TXT), LinkedIn scraping, GitHub profile parsing
- ✅ **Resume Optimization** - ATS scoring, resume rewriting, keyword optimization
- ✅ **Interview Engine** - AI-generated interview questions, answer evaluation
- ✅ **Audio Processing** - Audio transcription, analysis, AI scoring of verbal answers

---

## 📁 Architecture

```
unified_backend/
├── main.py                      # FastAPI entry point
├── requirements.txt             # Dependencies
├── routers/                     # HTTP Layer (routes only)
│   ├── resume.py               # Resume endpoints
│   ├── optimize.py             # Optimization endpoints
│   ├── interview.py            # Interview endpoints
│   └── audio.py                # Audio endpoints
├── services/                    # Business Logic Layer
│   ├── resume_parser/          # File, LinkedIn, GitHub parsing
│   ├── resume_optimizer/       # ATS scoring, rewriting
│   ├── interview_generator/    # Question generation, evaluation
│   └── audio_processor/        # Audio processing & scoring
├── utils/                       # Shared Utilities
│   ├── config.py               # Configuration & constants
│   └── pdf_extractor.py        # (to be copied from rag/)
├── models/                      # Pydantic Schemas
│   └── schemas.py              # Request/response models
└── data/                        # Runtime data (created automatically)
    ├── samples/                # Uploaded resumes
    └── audio_sessions/         # Audio files
```

---

## 🔧 Installation & Setup

### 1. Prerequisites
- Python 3.10 or higher
- Virtual environment (recommended)

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Optional: Install Ollama
For local LLM integration:
```bash
# Download from https://ollama.ai
ollama pull mistral
```

---

## 🏃 Running the Application

### Local Development
```bash
python main.py
```

Or using Uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Visit API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

---

## 📚 API Endpoints

### Resume Endpoints (`/resume`)

#### Upload Resume
```bash
POST /resume/upload
Content-Type: multipart/form-data

# Upload resume file (PDF, DOCX, or TXT)
curl -X POST "http://localhost:8000/resume/upload" \
  -F "file=@resume.pdf"

Response:
{
  "status": "success",
  "filename": "resume.pdf",
  "file_path": "/data/samples/resume.pdf",
  "file_size": 25000,
  "text_preview": "...",
  "text_summary": {...},
  "structured_data": {...},
  "ollama_status": "success"
}
```

#### Parse LinkedIn Profile
```bash
POST /resume/linkedin
Content-Type: application/json

{
  "profile_url": "https://linkedin.com/in/john-doe"
}

Response:
{
  "status": "success",
  "name": "John Doe",
  "headline": "Senior Software Engineer",
  "experience": [...],
  "skills": [...],
  "education": [...]
}
```

#### Parse GitHub Profile
```bash
POST /resume/github
Content-Type: application/json

{
  "github_username": "torvalds"
}

Response:
{
  "status": "success",
  "username": "torvalds",
  "repositories": [...],
  "stars": 50000,
  "followers": 5000,
  "top_languages": ["C", "Python"]
}
```

---

### Resume Optimization (`/optimize`)

#### Calculate ATS Score
```bash
POST /optimize/ats-score
Content-Type: application/json

{
  "resume_text": "Senior Software Engineer with 5+ years...",
  "job_description": "We are looking for a software engineer..."
}

Response:
{
  "score": 78,
  "match_percentage": 78.5,
  "missing_keywords": ["machine learning", "kubernetes"],
  "matched_keywords": ["python", "fastapi"],
  "recommendations": ["Add machine learning skills"]
}
```

#### Rewrite Resume
```bash
POST /optimize/rewrite
Content-Type: application/json

{
  "resume_text": "I worked at Google...",
  "job_title": "Product Manager",
  "tone": "professional"
}

Response:
{
  "status": "success",
  "original_length": 2500,
  "rewritten_length": 2650,
  "rewritten_resume": "...",
  "improvements": ["Restructured experience", "Enhanced action verbs"]
}
```

---

### Interview Endpoints (`/interview`)

#### Generate Interview Questions
```bash
POST /interview/questions
Content-Type: application/json

{
  "job_title": "Senior Software Engineer",
  "experience_level": "senior",
  "num_questions": 5
}

Response:
{
  "status": "success",
  "job_title": "Senior Software Engineer",
  "questions": [
    {
      "id": 1,
      "question": "Describe a challenging project you led",
      "category": "behavioral",
      "difficulty": "medium",
      "suggested_points": [...]
    }
  ]
}
```

#### Evaluate Answer
```bash
POST /interview/evaluate-answer
Content-Type: application/json

{
  "question": "Describe a challenging project you led",
  "candidate_answer": "I led a team to build...",
  "ideal_points": ["Challenge", "Solution", "Results"]
}

Response:
{
  "status": "success",
  "score": 82,
  "feedback": "Strong answer with good detail...",
  "strengths": ["Clear problem description"],
  "areas_for_improvement": ["More specific technical details"],
  "suggestions": ["Add team collaboration example"]
}
```

---

### Audio Endpoints (`/audio`)

#### Upload and Transcribe
```bash
POST /audio/upload-and-transcribe
Content-Type: multipart/form-data

curl -X POST "http://localhost:8000/audio/upload-and-transcribe" \
  -F "file=@interview_answer.mp3"

Response:
{
  "status": "success",
  "session_id": "audio_abc123",
  "transcription": "I have 5 years of experience...",
  "duration": 45.5,
  "confidence": 0.92
}
```

#### Analyze Audio
```bash
POST /audio/analyze?session_id=audio_abc123

Response:
{
  "status": "success",
  "session_id": "audio_abc123",
  "transcript": "...",
  "key_points": ["5 years experience", "Python expertise"],
  "sentiment": "positive",
  "clarity_score": 85
}
```

#### Score Audio Answer
```bash
POST /audio/score-answer?session_id=audio_abc123&question=Describe%20a%20project

Response:
{
  "status": "success",
  "session_id": "audio_abc123",
  "score": 78,
  "transcript": "...",
  "communication_score": 82,
  "clarity_score": 85,
  "engagement_score": 70,
  "feedback": "Good technical explanation..."
}
```

---

## 🔌 Integration Guide

### Adding Code from Teammates

1. **Resume Optimization** (from `talentx_portion-main/`)
   - Copy `resume_scoring.py` → `services/resume_optimizer/ats_scorer.py`
   - Copy `resume_optimizer.py` → `services/resume_optimizer/rewriter.py`
   - Fix imports to use relative paths

2. **Interview Engine** (from `backend--main/`)
   - Copy question generation code → `services/interview_generator/engine.py`
   - Copy answer evaluation code → `services/interview_generator/scoring.py`

3. **Audio Processing** (from `rag/backend/`)
   - Copy audio handling → `services/audio_processor/audio_handler.py`
   - Copy scoring logic → `services/audio_processor/scoring.py`

4. **Resume Parser** (copy from existing `parsers/`)
   - Copy `file_parser.py` → `services/resume_parser/file_parser.py`
   - Copy `linkedin_parser.py` → `services/resume_parser/linkedin_parser.py`
   - Copy `github_parser.py` → `services/resume_parser/github_parser.py`
   - Copy `ollama_parser.py` → `services/resume_parser/ollama_parser.py`

### Fix Imports After Integration

When copying code, update imports:

**Before (old imports):**
```python
from parsers.file_parser import extract_text_from_file
from services.resume_optimizer import calculate_ats_score
```

**After (new imports):**
```python
from ...resume_parser.file_parser import extract_text_from_file
from ...resume_optimizer.ats_scorer import calculate_ats_score
```

---

## 🧪 Testing

### Manual Testing with Swagger UI
1. Go to http://localhost:8000/docs
2. Click on an endpoint to expand it
3. Click "Try it out" button
4. Enter parameters
5. Click "Execute"

### Test with cURL
```bash
# Resume upload
curl -X POST "http://localhost:8000/resume/upload" \
  -F "file=@test_resume.pdf"

# ATS scoring
curl -X POST "http://localhost:8000/optimize/ats-score" \
  -H "Content-Type: application/json" \
  -d '{"resume_text":"...", "job_description":"..."}'

# Interview questions
curl -X POST "http://localhost:8000/interview/questions" \
  -H "Content-Type: application/json" \
  -d '{"job_title":"Engineer", "experience_level":"senior", "num_questions":5}'
```

### Health Check
```bash
curl http://localhost:8000/health

# Response:
{
  "status": "healthy",
  "version": "2.0.0",
  "services": {
    "resume": "✓ running",
    "optimize": "✓ running",
    "interview": "✓ running",
    "audio": "✓ running"
  }
}
```

---

## 📋 Checklist for Integration

### Before Running
- [ ] Python 3.10+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Ollama installed (optional, for LLM features)

### After Running
- [ ] Server starts without errors
- [ ] Swagger UI loads at `/docs`
- [ ] All endpoints respond (test via Swagger)
- [ ] No import errors in logs
- [ ] CORS enabled (can call from frontend)

### Integration Steps
- [ ] Copy resume parser files to `services/resume_parser/`
- [ ] Copy optimization files to `services/resume_optimizer/`
- [ ] Copy interview files to `services/interview_generator/`
- [ ] Copy audio files to `services/audio_processor/`
- [ ] Fix all imports to use relative paths
- [ ] Update `requirements.txt` with new dependencies
- [ ] Test each endpoint individually
- [ ] Verify JSON response format consistency

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'routers'"
**Solution**: Ensure you're running from `unified_backend/` directory:
```bash
cd unified_backend
python main.py
```

### Issue: "Port 8000 is already in use"
**Solution**: Use a different port:
```bash
python main.py --port 8001
# or
uvicorn main:app --port 8001
```

### Issue: "PermissionError" when uploading files
**Solution**: Ensure `data/` and `samples/` directories exist with write permissions:
```bash
mkdir -p data/samples
chmod 755 data/samples
```

### Issue: Ollama endpoints not working
**Solution**: Install and run Ollama locally:
```bash
# Download from https://ollama.ai
ollama pull mistral
ollama serve
```

---

## 📚 Project Structure Reference

```
unified_backend/
│
├── main.py                     ← Entry point, FastAPI app
├── requirements.txt            ← Python dependencies
│
├── routers/                    ← HTTP Routes (calls services)
│   ├── __init__.py
│   ├── resume.py              ← File upload, LinkedIn, GitHub
│   ├── optimize.py            ← ATS scoring, rewriting
│   ├── interview.py           ← Question generation, eval
│   └── audio.py               ← Audio processing
│
├── services/                   ← Business Logic
│   ├── __init__.py
│   ├── resume_parser/
│   │   ├── __init__.py
│   │   ├── file_parser.py     ← Extract text from files
│   │   ├── linkedin_parser.py ← LinkedIn scraping
│   │   ├── github_parser.py   ← GitHub API
│   │   └── ollama_parser.py   ← LLM parsing
│   ├── resume_optimizer/
│   │   ├── __init__.py
│   │   ├── ats_scorer.py      ← ATS calculation
│   │   └── rewriter.py        ← Resume rewriting
│   ├── interview_generator/
│   │   ├── __init__.py
│   │   ├── engine.py          ← Question generation
│   │   └── scoring.py         ← Answer evaluation
│   └── audio_processor/
│       ├── __init__.py
│       ├── audio_handler.py   ← Audio processing
│       └── scoring.py         ← Audio scoring
│
├── utils/                      ← Shared utilities
│   ├── __init__.py
│   └── config.py              ← Constants & config
│
├── models/                     ← Pydantic schemas
│   ├── __init__.py
│   └── schemas.py             ← Request/response models
│
└── data/                       ← Runtime data (created auto)
    ├── samples/               ← Uploaded resumes
    └── audio/                 ← Audio files
```

---

## 🚀 Deployment

### Local Development
```bash
cd unified_backend
python main.py
```

### Production with Gunicorn
```bash
gunicorn -k uvicorn.workers.UvicornWorker main:app \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker
```

### Using Docker (optional)
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

---

## 📞 Support & Next Steps

### Next Steps
1. **Copy existing parsers** to `services/resume_parser/`
2. **Extract and copy** optimization logic
3. **Extract and copy** interview generation logic
4. **Extract and copy** audio processing logic
5. **Fix all imports** to use relative paths
6. **Update requirements.txt** with additional dependencies
7. **Test each endpoint** via Swagger UI
8. **Deploy** using Render.com or similar

### Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Pydantic Documentation](https://docs.pydantic.dev)
- [Render Deployment Guide](../README_DEPLOY.md)

---

## 📝 License

This project is part of the AI Talent Platform. All components are integrated and working together.

---

**Ready to integrate? Start copying files to `services/` directories!** 🚀

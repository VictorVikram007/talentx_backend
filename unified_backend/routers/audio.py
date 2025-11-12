# Audio Processing Router - Handles audio upload, transcription, and spoken answer scoring
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from typing import Optional
import uuid

from models.schemas import (
    AudioTranscriptionResponse,
    AudioAnalysisResponse,
    AudioScoringResponse,
)

from services.audio_processor import (
    get_audio_handler,
    transcribe_audio,
    score_spoken_answer,
    generate_audio_report,
    assess_clarity,
    assess_pacing,
    extract_key_phrases,
)

from utils.config import ALLOWED_AUDIO_EXTENSIONS

router = APIRouter()


@router.post("/upload")
async def upload_audio(file: UploadFile = File(...)) -> dict:
    """
    Upload and store audio file.
    
    **Parameters:**
    - file: Audio file (.wav, .mp3, .m4a, .ogg)
    
    **Returns:**
    - status: success/error
    - message: Upload status message
    - data: {file_id, filename, size_bytes, format}
    
    **Example:**
    ```
    curl -X POST http://localhost:8000/audio/upload \\
      -F "file=@sample_answer.wav"
    
    Response:
    {
      "status": "success",
      "message": "Audio uploaded successfully",
      "data": {
        "file_id": "abc123-def456",
        "filename": "sample_answer.wav",
        "size_bytes": 125000,
        "format": "wav"
      }
    }
    ```
    """
    try:
        # Validate file
        if file.filename is None:
            raise HTTPException(status_code=400, detail="Filename is missing")
        
        # Check extension
        from pathlib import Path
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in ALLOWED_AUDIO_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format: {file_extension}. Allowed: {', '.join(ALLOWED_AUDIO_EXTENSIONS)}"
            )
        
        # Read file content
        content = await file.read()
        
        # Validate file size
        audio_handler = get_audio_handler()
        is_valid, error_msg = audio_handler.validate_audio_file(file.filename, len(content))
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Save file
        file_info = audio_handler.save_audio_file(content, file.filename)
        
        return {
            "status": "success",
            "message": "Audio uploaded successfully",
            "data": {
                "file_id": file_info["file_id"],
                "filename": file_info["filename"],
                "size_bytes": file_info["size_bytes"],
                "format": file_info["format"],
                "mime_type": file_info["mime_type"]
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/transcribe", response_model=AudioTranscriptionResponse)
async def transcribe_audio_endpoint(file: UploadFile = File(...)) -> AudioTranscriptionResponse:
    """
    Transcribe audio file using Whisper speech-to-text.
    
    **Parameters:**
    - file: Audio file (.wav, .mp3, .m4a, .ogg)
    
    **Returns:**
    - status: success/error
    - session_id: Unique session ID
    - transcription: Transcribed text
    - duration: Audio duration in seconds
    - confidence: Transcription confidence (0-1)
    
    **Example:**
    ```
    curl -X POST http://localhost:8000/audio/transcribe \\
      -F "file=@sample_answer.wav"
    
    Response:
    {
      "status": "success",
      "session_id": "sess_abc123",
      "transcription": "I have 5 years of experience...",
      "duration": 45.5,
      "confidence": 0.92
    }
    ```
    """
    try:
        # Upload and save file
        if file.filename is None:
            raise HTTPException(status_code=400, detail="Filename is missing")
        
        content = await file.read()
        
        # Validate
        audio_handler = get_audio_handler()
        is_valid, error_msg = audio_handler.validate_audio_file(file.filename, len(content))
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Save file
        file_info = audio_handler.save_audio_file(content, file.filename)
        file_path = file_info["path"]
        
        # Transcribe
        transcription_result = transcribe_audio(file_path)
        
        # Generate session ID
        session_id = f"sess_{uuid.uuid4().hex[:12]}"
        
        return AudioTranscriptionResponse(
            status="success",
            session_id=session_id,
            transcription=transcription_result.get("transcription", ""),
            duration=transcription_result.get("duration", 0.0),
            confidence=transcription_result.get("confidence", 0.0)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@router.post("/score", response_model=AudioScoringResponse)
async def score_spoken_answer_endpoint(
    question: str = Form(...),
    file: UploadFile = File(...)
) -> AudioScoringResponse:
    """
    Score a spoken answer to an interview question.
    
    **Parameters:**
    - question: Interview question (form data)
    - file: Audio file with answer (multipart file)
    
    **Returns:**
    - status: success/error
    - session_id: Unique session ID
    - score: Overall score (0-100)
    - transcript: Transcribed answer
    - communication_score: Communication quality (0-100)
    - clarity_score: Audio clarity (0-100)
    - engagement_score: Engagement level (0-100)
    - feedback: Detailed feedback
    
    **Example:**
    ```
    curl -X POST http://localhost:8000/audio/score \\
      -F "file=@sample_answer.wav" \\
      -F "question=Describe a system you designed"
    
    Response:
    {
      "status": "success",
      "session_id": "sess_abc123",
      "score": 82,
      "transcript": "I implemented a scalable...",
      "communication_score": 85,
      "clarity_score": 88,
      "engagement_score": 75,
      "feedback": "Strong technical explanation..."
    }
    ```
    """
    try:
        # Validate inputs
        if not question:
            raise HTTPException(status_code=400, detail="Question is required")
        
        if file.filename is None:
            raise HTTPException(status_code=400, detail="Audio file is required")
        
        # Upload and transcribe
        content = await file.read()
        
        audio_handler = get_audio_handler()
        is_valid, error_msg = audio_handler.validate_audio_file(file.filename, len(content))
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Save file
        file_info = audio_handler.save_audio_file(content, file.filename)
        file_path = file_info["path"]
        
        # Transcribe audio
        transcription_result = transcribe_audio(file_path)
        transcription = transcription_result.get("transcription", "")
        duration = transcription_result.get("duration", 0.0)
        
        if not transcription:
            raise HTTPException(status_code=400, detail="Could not transcribe audio")
        
        # Score the answer
        score_result = score_spoken_answer(
            transcription=transcription,
            question=question,
            duration_seconds=duration
        )
        
        # Extract scores
        overall_score = score_result.get("overall_score", 0)
        content_score = score_result.get("content_score", 0)
        delivery_score = score_result.get("delivery_score", 0)
        clarity_score = score_result.get("clarity_score", 0)
        
        # Map scores to response model
        communication_score = int(content_score)  # Content quality = communication
        engagement_score = int(delivery_score)  # Delivery quality = engagement
        
        # Generate session ID
        session_id = f"sess_{uuid.uuid4().hex[:12]}"
        
        return AudioScoringResponse(
            status="success",
            session_id=session_id,
            score=overall_score,
            transcript=transcription,
            communication_score=communication_score,
            clarity_score=clarity_score,
            engagement_score=engagement_score,
            feedback=score_result.get("feedback", "")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scoring failed: {str(e)}")


@router.post("/analyze")
async def analyze_audio_endpoint(
    file: UploadFile = File(...)
) -> dict:
    """
    Analyze audio for communication quality, clarity, and pacing.
    
    **Parameters:**
    - file: Audio file (.wav, .mp3, .m4a, .ogg)
    
    **Returns:**
    - status: success/error
    - message: Analysis summary
    - data: {clarity_score, clarity_assessment, pacing_score, pacing_assessment, key_phrases}
    
    **Example:**
    ```
    curl -X POST http://localhost:8000/audio/analyze \\
      -F "file=@sample_answer.wav"
    ```
    """
    try:
        # Upload and transcribe
        if file.filename is None:
            raise HTTPException(status_code=400, detail="Filename is missing")
        
        content = await file.read()
        
        audio_handler = get_audio_handler()
        is_valid, error_msg = audio_handler.validate_audio_file(file.filename, len(content))
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Save file
        file_info = audio_handler.save_audio_file(content, file.filename)
        file_path = file_info["path"]
        
        # Transcribe
        transcription_result = transcribe_audio(file_path)
        transcription = transcription_result.get("transcription", "")
        duration = transcription_result.get("duration", 0.0)
        
        # Analyze
        clarity_metrics = assess_clarity(transcription)
        pacing_metrics = assess_pacing(transcription, duration)
        key_phrases = extract_key_phrases(transcription)
        
        return {
            "status": "success",
            "message": "Audio analysis complete",
            "data": {
                "clarity_score": clarity_metrics.get("clarity_score", 0),
                "clarity_assessment": clarity_metrics.get("assessment", ""),
                "word_count": clarity_metrics.get("word_count", 0),
                "avg_word_length": clarity_metrics.get("avg_word_length", 0),
                "pacing_score": pacing_metrics.get("pacing_score", 0),
                "pacing_assessment": pacing_metrics.get("assessment", ""),
                "words_per_minute": pacing_metrics.get("words_per_minute", 0),
                "key_phrases": key_phrases,
                "transcription": transcription,
                "duration_seconds": duration
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/interview")
async def full_interview_endpoint(
    question: str = Form(...),
    role: str = Form(default="Software Engineer"),
    experience_level: str = Form(default="mid"),
    file: UploadFile = File(...)
) -> dict:
    """
    Complete voice interview flow: Upload → Transcribe → Score → Report.
    
    **Parameters:**
    - question: Interview question (form)
    - role: Job role (form, default: "Software Engineer")
    - experience_level: junior/mid/senior (form, default: mid)
    - file: Audio file with answer (multipart file)
    
    **Returns:**
    - status: success/error
    - message: Summary message
    - data: Complete interview report with all metrics
    
    **Example:**
    ```
    curl -X POST http://localhost:8000/audio/interview \\
      -F "file=@answer.wav" \\
      -F "question=Describe a system you designed" \\
      -F "role=Senior Backend Engineer" \\
      -F "experience_level=mid"
    ```
    """
    try:
        # Validate inputs
        if not question:
            raise HTTPException(status_code=400, detail="Question is required")
        
        if not role:
            raise HTTPException(status_code=400, detail="Role is required")
        
        if experience_level not in ["junior", "mid", "senior"]:
            raise HTTPException(status_code=400, detail="Invalid experience_level")
        
        if file.filename is None:
            raise HTTPException(status_code=400, detail="Audio file is required")
        
        # Process audio
        content = await file.read()
        
        audio_handler = get_audio_handler()
        is_valid, error_msg = audio_handler.validate_audio_file(file.filename, len(content))
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Save and transcribe
        file_info = audio_handler.save_audio_file(content, file.filename)
        file_path = file_info["path"]
        
        transcription_result = transcribe_audio(file_path)
        transcription = transcription_result.get("transcription", "")
        duration = transcription_result.get("duration", 0.0)
        
        if not transcription:
            raise HTTPException(status_code=400, detail="Could not transcribe audio")
        
        # Score answer
        score_result = score_spoken_answer(
            transcription=transcription,
            question=question,
            role=role,
            experience_level=experience_level,
            duration_seconds=duration
        )
        
        # Generate report
        report = generate_audio_report(score_result, candidate_name=None)
        
        # Generate session ID
        session_id = f"sess_{uuid.uuid4().hex[:12]}"
        
        return {
            "status": "success",
            "message": "Voice interview completed successfully",
            "data": {
                "session_id": session_id,
                "question": question,
                "role": role,
                "experience_level": experience_level,
                "report": report,
                "transcription": transcription,
                "file_id": file_info["file_id"]
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Interview processing failed: {str(e)}")

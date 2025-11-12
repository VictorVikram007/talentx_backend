"""
Audio Processor Service
- Audio file handling and storage
- Speech-to-text transcription via Whisper
- Spoken answer scoring with audio metrics
- Comprehensive audio interview workflow
"""

from .audio_handler import (
    AudioHandler,
    get_audio_handler,
)

from .whisper_transcriber import (
    initialize_whisper,
    transcribe_audio,
    extract_key_phrases,
    assess_clarity,
    assess_pacing,
)

from .scoring import (
    score_spoken_answer,
    generate_audio_report,
    compare_text_vs_audio,
)

__all__ = [
    # Audio Handler
    "AudioHandler",
    "get_audio_handler",
    # Whisper Transcriber
    "initialize_whisper",
    "transcribe_audio",
    "extract_key_phrases",
    "assess_clarity",
    "assess_pacing",
    # Scoring
    "score_spoken_answer",
    "generate_audio_report",
    "compare_text_vs_audio",
]

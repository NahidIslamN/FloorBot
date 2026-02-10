"""
Speech Service - Handles audio transcription using OpenAI Whisper
"""
import base64
import io
from typing import Optional
from openai import OpenAI
from ai_app.config import AIConfig


class SpeechService:
    """Handles speech-to-text conversion using OpenAI Whisper"""
    
    def __init__(self):
        """Initialize speech service"""
        self.client = OpenAI(api_key=AIConfig.OPENAI_API_KEY)
        self.model = AIConfig.WHISPER_MODEL
    
    def transcribe_audio(self, audio_data: bytes, audio_format: str = "wav", language: str = "en") -> str:
        """
        Transcribe audio to text
        
        Args:
            audio_data: Raw audio bytes
            audio_format: Audio format (wav, mp3, webm, m4a)
            language: Language code (default: en)
            
        Returns:
            Transcribed text
        """
        audio_file = io.BytesIO(audio_data)
        audio_file.name = f"audio.{audio_format}"
        
        transcript = self.client.audio.transcriptions.create(
            model=self.model,
            file=audio_file,
            language=language
        )
        
        return transcript.text
    
    def transcribe_base64_audio(self, base64_audio: str, audio_format: str = "wav", language: str = "en") -> str:
        """
        Transcribe base64 encoded audio
        
        Args:
            base64_audio: Base64 encoded audio string
            audio_format: Audio format
            language: Language code
            
        Returns:
            Transcribed text
        """
        audio_bytes = base64.b64decode(base64_audio)
        return self.transcribe_audio(audio_bytes, audio_format, language)

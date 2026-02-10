"""
Main API Interface for FloorBot AI
Simple interface for integration testing
"""
from ai_app.chatbot import FloorBotAI
from ai_app.speech_service import SpeechService
from ai_app.session_manager import SessionManager


class FloorBotAPI:
    """
    Simple API interface for FloorBot AI
    For direct Python integration or testing
    """
    
    def __init__(self):
        """Initialize FloorBot API"""
        self.chatbot = FloorBotAI()
        self.speech_service = SpeechService()
        self.session_manager = SessionManager()
    
    def create_session(self, user_id=None):
        """Create a new chat session"""
        return self.session_manager.create_session(user_id)
    
    def send_text_message(self, session_id, message):
        """Send text message to chatbot"""
        return self.chatbot.chat(session_id, message)
    
    def send_voice_message(self, session_id, audio_data, audio_format='wav', language='en'):
        """Send voice message to chatbot"""
        transcribed = self.speech_service.transcribe_audio(audio_data, audio_format, language)
        response = self.chatbot.chat(session_id, transcribed)
        response['transcribed_text'] = transcribed
        return response
    
    def get_history(self, session_id):
        """Get conversation history"""
        session = self.session_manager.get_session(session_id)
        if session:
            return session.get_conversation_history()
        return None
    
    def delete_session(self, session_id):
        """Delete a session"""
        self.session_manager.delete_session(session_id)

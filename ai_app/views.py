"""
AI App Views - REST API endpoints for FloorBot AI
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from ai_app.serializers import (
    TextMessageSerializer,
    VoiceMessageSerializer,
    ChatResponseSerializer,
    ConversationHistorySerializer,
    SessionSerializer,
    SessionRequestSerializer
)
from ai_app.chatbot import FloorBotAI
from ai_app.speech_service import SpeechService
from ai_app.session_manager import SessionManager


class CreateSessionView(APIView):
    """Create a new AI chat session"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Create new session"""
        session_manager = SessionManager()
        
        user_id = None
        if request.user.is_authenticated:
            user_id = str(request.user.id)
        
        session = session_manager.create_session(user_id=user_id)
        
        serializer = SessionSerializer({
            "session_id": session.session_id,
            "user_id": session.user_id,
            "created_at": session.created_at
        })
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TextChatView(APIView):
    """Handle text-based chat messages"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Send text message to AI"""
        serializer = TextMessageSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        message = serializer.validated_data['message']
        session_id = serializer.validated_data.get('session_id')
        
        chatbot = FloorBotAI()
        
        if not session_id:
            session = chatbot.session_manager.create_session()
            session_id = session.session_id
        
        response_data = chatbot.chat(session_id, message)
        
        response_serializer = ChatResponseSerializer(response_data)
        
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class VoiceChatView(APIView):
    """Handle voice-based chat messages"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Send voice message to AI"""
        serializer = VoiceMessageSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        audio_data = serializer.validated_data['audio_data']
        audio_format = serializer.validated_data['audio_format']
        session_id = serializer.validated_data.get('session_id')
        language = serializer.validated_data['language']
        
        try:
            speech_service = SpeechService()
            transcribed_text = speech_service.transcribe_base64_audio(
                audio_data, 
                audio_format, 
                language
            )
            
            chatbot = FloorBotAI()
            
            if not session_id:
                session = chatbot.session_manager.create_session()
                session_id = session.session_id
            
            response_data = chatbot.chat(session_id, transcribed_text)
            response_data['transcribed_text'] = transcribed_text
            
            response_serializer = ChatResponseSerializer(response_data)
            
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                "session_id": session_id,
                "response": f"Failed to process voice message: {str(e)}",
                "success": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConversationHistoryView(APIView):
    """Get conversation history for a session"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Get conversation history"""
        serializer = SessionRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        session_id = serializer.validated_data['session_id']
        
        session_manager = SessionManager()
        session = session_manager.get_session(session_id)
        
        if not session:
            return Response({
                "session_id": session_id,
                "success": False,
                "message": "Session not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        response_data = {
            "session_id": session_id,
            "messages": session.get_conversation_history(),
            "success": True
        }
        
        response_serializer = ConversationHistorySerializer(response_data)
        
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class DeleteSessionView(APIView):
    """Delete a session"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Delete session"""
        serializer = SessionRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        session_id = serializer.validated_data['session_id']
        
        session_manager = SessionManager()
        session_manager.delete_session(session_id)
        
        return Response({
            "message": "Session deleted successfully",
            "success": True
        }, status=status.HTTP_200_OK)

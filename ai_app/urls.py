"""
URL Configuration for AI App
"""
from django.urls import path
from ai_app.views import (
    CreateSessionView,
    TextChatView,
    VoiceChatView,
    VoiceFileChatView,
    ConversationHistoryView,
    DeleteSessionView
)

urlpatterns = [
    path('session/create/', CreateSessionView.as_view(), name='ai_create_session'),
    path('chat/text/', TextChatView.as_view(), name='ai_text_chat'),
    path('chat/voice/', VoiceChatView.as_view(), name='ai_voice_chat'),
    path('chat/voice-file/', VoiceFileChatView.as_view(), name='ai_voice_file_chat'),
    path('session/history/', ConversationHistoryView.as_view(), name='ai_conversation_history'),
    path('session/delete/', DeleteSessionView.as_view(), name='ai_delete_session'),
]

"""
Serializers for AI App API
"""
from rest_framework import serializers


class TextMessageSerializer(serializers.Serializer):
    """Serializer for text message input"""
    message = serializers.CharField(required=True, max_length=2000)
    session_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class VoiceMessageSerializer(serializers.Serializer):
    """Serializer for voice message input"""
    audio_data = serializers.CharField(required=True, help_text="Base64 encoded audio")
    audio_format = serializers.ChoiceField(
        choices=['wav', 'mp3', 'webm', 'm4a'],
        default='wav'
    )
    session_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    language = serializers.CharField(default='en', max_length=10)


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for chat response output"""
    session_id = serializers.CharField()
    response = serializers.CharField()
    success = serializers.BooleanField()
    error = serializers.CharField(required=False, allow_null=True)
    transcribed_text = serializers.CharField(required=False, allow_null=True)


class SessionSerializer(serializers.Serializer):
    """Serializer for session information"""
    session_id = serializers.CharField()
    user_id = serializers.CharField(required=False, allow_null=True)
    created_at = serializers.DateTimeField()


class ConversationHistorySerializer(serializers.Serializer):
    """Serializer for conversation history"""
    session_id = serializers.CharField()
    messages = serializers.ListField()
    success = serializers.BooleanField()
    message = serializers.CharField(required=False, allow_null=True)


class SessionRequestSerializer(serializers.Serializer):
    """Serializer for session ID in request"""
    session_id = serializers.CharField(required=True)

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name','last_name', 'image']

class ChatListSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    invitee = UserSerializer()

    class Meta:
        model = Chat
        fields = ['id', 'chat_type', 'name', 'participants', 'invitee', 'is_accepted_invitee']


class Message_List_Serializer(serializers.ModelSerializer):
    sender = UserSerializer()
    seen_users = UserSerializer(many=True)
    class Meta:
        model = Message
        exclude = ["chat"]
        depth = 1


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model=NoteModel
        fields = ["id","title","content"]
        




class Chat_or_Group_CreateSerializer(serializers.Serializer):
    user_list = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )
    group_name = serializers.CharField(
        required=False,
        allow_blank=True,
        default=""
    )



class Add_People_Group_CreateSerializer(serializers.Serializer):
    user_list = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )
    

class Send_Message_Serializer(serializers.Serializer):
    message = serializers.CharField(
        required=False,
        allow_blank=True,
        default=""
    )
    files = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        allow_empty=True
    )
  
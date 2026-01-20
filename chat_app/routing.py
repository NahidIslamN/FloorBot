from django.urls import path
from chat_app import consumers

websocket_urlpatterns = [
    path(r'ws/asc/notifications/', consumers.NotificationConsumer.as_asgi()),
    path(r'ws/asc/update_chat_messages/', consumers.ChatConsumer.as_asgi()),
   
]

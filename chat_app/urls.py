from django.urls import path
from .views import *

urlpatterns = [
    path('supports/', User_Suport_Message.as_view(), name="chat-create-list"),
    path('notifications/', Notifications.as_view(), name='notifications'),
    path('unseen-notifications-count/', Unseen_Notifications_count.as_view(), name='unseen-notifications-count'),

    path('suport-inbox-lists/', SuperAdminSuportChatList.as_view(), name="chat-lists"),
    path('message-lists/<int:inbox_id>/', MessageList_Chats.as_view(), name="chat-lists"),




    path("sent-message/<int:pk>/", Sent_Message_Chats.as_view(), name="send-message"),


]

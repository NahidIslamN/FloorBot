import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import  Chat, Message, NoteModel
from channels.consumer import AsyncConsumer
from channels.exceptions import StopConsumer


# sent notification to user
class NotificationConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        user = self.scope.get("user")

        if user.is_anonymous:
            await self.close()   # unauthorized হলে বন্ধ
            return
        else:
            self.room_group_name = f"notification_{user.id}"
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.send({
                "type": "websocket.accept"
            })

    async def websocket_receive(self, event):

        text_data = event['text']
        try:
            message = json.loads(text_data)
        except json.JSONDecodeError:
            message = {"text": text_data}

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "sent.note",
                "message": message,
            }
        )

    async def sent_note(self, event):
        data = event['message']
        user = self.scope.get("user")
      
        if not event.get('saved', False):
            await self.save_notification(user=user, data=data)

        await self.send({
            "type": "websocket.send",
            "text": json.dumps(event['message']),
        })

    async def success(self, event):
        await self.sent_note(event)

    async def warning(self, event):
        await self.sent_note(event)

    async def normal(self, event):
        await self.sent_note(event)

    @database_sync_to_async
    def save_notification(self, user, data):        
        return NoteModel.objects.create(
            user=user,
            title=data.get('title'),
            content=data.get('content'),
            note_type = data.get('note_type')
        )

    async def websocket_disconnect(self, event):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        raise StopConsumer()
    



class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope.get("user")

        if not self.user or self.user.is_anonymous:
            await self.close(code=4001)
            return

        # USER PERSONAL GROUP
        self.user_group = f"chats_{self.user.id}"

        await self.channel_layer.group_add(
            self.user_group,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "user_group"):
            await self.channel_layer.group_discard(
                self.user_group,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)

        chat_id = data.get("chat_id")
        message_text = data.get("message", "").strip()

        if not chat_id or not message_text:
            await self.send(json.dumps({
                "error": "chat_id and message are required"
            }))
            return

        # CHECK PERMISSION
        if not await self.is_participant(chat_id):
            await self.send(json.dumps({
                "error": "not allowed"
            }))
            return

        # SAVE MESSAGE
        message = await self.create_message(chat_id, message_text)

        # SEND TO ALL PARTICIPANTS (USER GROUPS)
        await self.send_to_chat_users(chat_id, message)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event["message"]))

    # ---------------- DB & HELPERS ---------------- #

    @database_sync_to_async
    def is_participant(self, chat_id):
        try:
            chat = Chat.objects.get(id=chat_id)
            return self.user in chat.participants.all()
        except Chat.DoesNotExist:
            return False

    @database_sync_to_async
    def create_message(self, chat_id, text):
        chat = Chat.objects.get(id=chat_id)
        chat.save()
        return Message.objects.create(
            chat=chat,
            sender=self.user,
            text=text
        )

    @database_sync_to_async
    def get_chat_users(self, chat_id):
        chat = Chat.objects.get(id=chat_id)
        # chat.save()
        return list(chat.participants.all())

    async def send_to_chat_users(self, chat_id, message):
        users = await self.get_chat_users(chat_id)

        payload = {
            "id": message.id,
            "chat_id": chat_id,
            "sender_id": message.sender_id,
            "message": message.text,
        }

        for user in users:
            await self.channel_layer.group_send(
                f"chats_{user.id}",
                {
                    "type": "chat_message",
                    "message": payload
                }
            )





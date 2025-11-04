import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from chat.models import Message, Room
from django.contrib.auth.models import AnonymousUser
from chat.auth_middleware import get_user_from_token


class ChatConsumer(AsyncWebsocketConsumer):

    @database_sync_to_async
    def save_message(self,room_name, user, message):
        room, created = Room.objects.get_or_create(name = room_name)
        return Message.objects.create(room = room, user = user, content = message)

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        #join room group
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )
        await self.accept()
        self.authenticated = False

    async def disconnect(self, close_code):
        # Leave room group
        if self.scope['user'].is_authenticated:
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if not getattr(self, 'authenticated', False):
            token = text_data_json.get('token', None)
            if not token:
                await self.send(json.dumps({"error": "Token is required for the first-time connection"}))
                await self.close(code=4001)
                return
            user_obj = await get_user_from_token(token)
            if not user_obj.is_authenticated:
                await self.send(json.dumps({"error": "Invalid token"}))
                await self.close(code=4001)
                return

            self.scope['user'] = user_obj
            self.authenticated = True
            await self.send(json.dumps({"success": f"Authenticated as {user_obj.username}"}))
            return

        #if user is authenticated
        message = text_data_json.get("message")
        user = self.scope['user']
        saved_msg = await self.save_message(self.room_name, user, message)
        timestamp = saved_msg.timestamp.isoformat()

        # send message to the room group
        await self.channel_layer.group_send(
            self.room_group_name, {
                'type': 'chat.message',
                'message': message,
                'username': user.username,
                'timestamp': timestamp
            }
        )

    # Receive message from the group
    async def chat_message(self, event):

        # send message to Websocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'timestamp': event.get('timestamp')
        }))




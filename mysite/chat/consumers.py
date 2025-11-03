import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from chat.models import Message, Room
from django.contrib.auth.models import AnonymousUser


class ChatConsumer(AsyncWebsocketConsumer):

    @database_sync_to_async
    def save_message(self,room_name, user, message):
        room, created = Room.objects.get_or_create(name = room_name)
        return Message.objects.create(room = room, user = user, content = message)

    async def connect(self):
        print(f"!!! CONSUMER DEBUG: User is authenticated: {self.scope['user'].is_authenticated} !!!")
        if self.scope['user'].is_authenticated:
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.room_group_name = f'chat_{self.room_name}'

            #join room group
            await self.channel_layer.group_add(
                self.room_group_name, self.channel_name
            )
            await self.accept()
            print(f"--- SUCCESS: User {self.scope['user'].username} accepted. ---")

        else:
            print("--- FAILURE: Anonymous user rejected. ---")
            await self.close(code=4001)

    async def disconnect(self, close_code):
        # Leave room group
        if self.scope['user'].is_authenticated:
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )



    async def receive(self, text_data):
        if not self.scope['user'].is_authenticated:
            return
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
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

    def now(self):
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")


# # chat/consumers.py (TEMPORARY CODE FOR DEBUGGING)
# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
#
#
# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         # 1. New Debug Print (Must appear if middleware is running)
#         print(f"!!! CONSUMER DEBUG: User is authenticated: {self.scope['user'].is_authenticated} !!!")
#
#         # 2. Check Authentication ONLY (No room name logic)
#         if self.scope['user'].is_authenticated:
#             await self.accept()
#             print(f"--- SUCCESS: User {self.scope['user'].username} accepted. ---")
#         else:
#             print("--- FAILURE: Anonymous user rejected. ---")
#             await self.close(code=4001)
#
#     async def disconnect(self, close_code):
#         pass
#
#     async def receive(self, text_data):
#         if self.scope['user'].is_authenticated:
#             await self.send(
#                 text_data=json.dumps({'message': 'Authenticated Echo: ' + json.loads(text_data)['message']}))
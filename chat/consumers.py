import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Message

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    
    async def disconnect(self,close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )


    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        if self.scope['user'].is_authenticated:
            username = self.scope['user'].username
        else:
            await self.close()
            return
        #save msg to db
        msg_obj=await sync_to_async(Message.objects.create)(
            room_name = self.room_name,
            user = username,
            message = message
        )


       # send msg to websocket group with timestamp
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message':msg_obj.message,
                'username': username,
                'timestamp': msg_obj.timestamp.strftime('%H:%M:%S'),
            }
        )


    async def chat_message(self, event):

        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'timestamp': event['timestamp'],
        }))
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatModel
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        #if ChatConsumer.objects.get(users=)
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
 
        await self.accept()

    

    async def disconnect(self, close_code):
        # Leave room group

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        print('1')
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        print('2', self.room_name)
        completed = await self.edit_text_log(int(self.room_name), text_data)
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    @database_sync_to_async
    def edit_text_log(self, id, text_data):
        chat_model = ChatModel.objects.get(id=int(self.room_name))
        chat_model.messages.append(text_data)
        chat_model.save()
        return True
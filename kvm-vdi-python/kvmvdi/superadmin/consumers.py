# chat/consumers.py
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async
from channels.auth import login, logout, get_user
import fileinput
from datetime import datetime
from datetime import timedelta

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'videochat'
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()        

    async def disconnect(self, close_code):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': 'out',
                'who': str(self.room_name),
                'stt': 'out'
            }
        )
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logout(self.scope)
        


    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        who = text_data_json['who']
        stt = text_data_json['stt']
        # print(message)
        await login(self.scope, self.scope["user"])
        # save the session (if the session backend does not access the db you can use `sync_to_async`)
        await database_sync_to_async(self.scope["session"].save)()
        # print(self.scope)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'who': who,
                'stt': stt
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        who = event['who']
        stt = event['stt']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'who': who,
            'stt': stt

        }))
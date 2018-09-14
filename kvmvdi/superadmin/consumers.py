# chat/consumers.py
# from asgiref.sync import async_to_sync
# from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import Ops
from .views import VmThread, check_ping
# from channels.layers import get_channel_layer
# from channels.db import database_sync_to_async
# from channels.auth import login, logout, get_user
# import fileinput
# from datetime import datetime
# from datetime import timedelta

class adminConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.admin_name = self.scope['url_route']['kwargs']['admin_name']
        self.room_group_name = 'superadmin'
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
        print(message)
        if Ops.objects.get(ip=message):
            thread = check_ping(host=message)
            if thread.run():
                ops = Ops.objects.get(ip=message)
                auth_url = "http://"+ops.ip+":5000/v3"
                username = ops.username
                password = ops.password
                project_name = ops.project
                user_domain_id = ops.userdomain
                project_domain_id = ops.projectdomain
                thread = VmThread(auth_url=auth_url, username=username, password=password, project_name=project_name, user_domain_id=user_domain_id, project_domain_id=project_domain_id)

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': thread.list_images(),
                        'network': thread.list_networks(),
                    }
                )
        else:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                }
            )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        try:
            network = event['network']
            # Send message to WebSocket
            await self.send(text_data=json.dumps({
                'message': message,
                'network': network,
            }))
        except:
            # Send message to WebSocket
            await self.send(text_data=json.dumps({
                'message': message,
            }))

        
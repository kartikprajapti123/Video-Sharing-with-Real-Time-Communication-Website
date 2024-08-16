from channels.generic.websocket import AsyncWebsocketConsumer
import json

class NotificationConsumer(AsyncWebsocketConsumer):
    
    
    async def connect(self):
        self.user_uuid = self.scope['url_route']['kwargs']['uuid']
        self.group_name = f'user_{self.user_uuid}'

        # Join the notification group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave the notification group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_notification(self, event):
        # Send notification message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            "notification_id":event['notification_id'],
            'message': event['message'],
            'notification_type': event['notification_type'],
            'timestamp': event['timestamp'],
            'link': event['link'],
            'sender':event['sender'],
            'sender_profile_picture':event['sender_profile_picture'],
            'sender_username':event['sender_username'],
            # 'common_uuid':event['common_uuid'],
            
            'count':event['count'],
            # 'sender_id':event['sender_id'],
            'sender_type':event['sender_type']
            
        }))
        
    async def send_main_notification(self, event):
        # Send notification message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'main_notification',
            "notification_id":event['notification_id'],
            'message': event['message'],
            'timestamp': event['timestamp'],
            'link': event['link'],
            # 'common_uuid':event['common_uuid'],
            
        }))
        
    
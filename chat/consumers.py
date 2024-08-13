from channels.generic.websocket import AsyncWebsocketConsumer
import json
from chat.models import Conversation, Message
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from notification.models import Notification
from user.models import User
from django.utils import timezone
from django.db.models import Q
from asgiref.sync import sync_to_async

class MyChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['id']
        self.group_name = f'chat_{self.conversation_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')

        if message_type == 'chat':
            conversation_id = text_data_json['conversation']
            sender_id = text_data_json['sender']
            content = text_data_json['content']
            profile_picture = text_data_json.get('profile_picture', '')
            username = text_data_json['username']
            file_url = text_data_json.get('file_url')
            
            # Save the message to the database
            message = await self.save_message(conversation_id, sender_id, content, file_url)
            print("message",message)
            
            if message:
                timestamp_str = message.timestamp.isoformat() 

                # Determine the recipient user
                
                    
                    # Create a notification for the recipient
                notification=await self.create_notification(conversation_id,sender_id, content, 'Chat Notification', message.id)
                print(notification)
                # Send message to room group
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'chat_message',
                        'conversation': conversation_id,
                        'sender': sender_id,
                        'content': content,
                        'profile_picture': profile_picture,
                        'username': username,
                        'file_url': file_url,
                        'timestamp': timestamp_str,
                        'message_id': message.id,
                        "notification_id":notification.id
                    }
                )
        elif message_type == 'typingstart':
            await self.channel_layer.group_send(self.group_name, {
                'type': "typing_start",
                'conversation': text_data_json['conversation'],
                'sender': text_data_json['sender'],
                'content': text_data_json['content'],
                'profile_picture': text_data_json['profile_picture'],
                'username': text_data_json['username'],
                'timestamp': ""
            })
        elif message_type == 'typingend':
            await self.channel_layer.group_send(self.group_name, {
                'type': "typing_end",
                'conversation': text_data_json['conversation'],
                'sender': text_data_json['sender'],
                'content': text_data_json['content'],
                'profile_picture': text_data_json['profile_picture'],
                'username': text_data_json['username'],
                'timestamp': ""
            })

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat',
            'conversation': event['conversation'],
            'sender': event['sender'],
            'content': event['content'],
            'username': event['username'],
            'profile_picture': event['profile_picture'],
            'file_url': event['file_url'],
            'timestamp': event['timestamp'],
            "message_id": event['message_id'],
            "notification_id": event['notification_id'],
            
        }))

    async def typing_start(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typingstart',
            'conversation': event['conversation'],
            'sender': event['sender'],
            'content': event['content'],
            'username': event['username'],
            'profile_picture': event['profile_picture'],
            'timestamp': event['timestamp']
        }))

    async def typing_end(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typingend',
            'conversation': event['conversation'],
            'sender': event['sender'],
            'content': event['content'],
            'username': event['username'],
            'profile_picture': event['profile_picture'],
            'timestamp': event['timestamp']
        }))

    @sync_to_async
    def save_message(self, conversation_id, sender_id, content, file_url):
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            sender = User.objects.get(id=sender_id)
            message = Message(
                conversation=conversation,
                sender=sender,
                content=content,
                file_url=file_url,
                is_read_by_user1=(sender == conversation.user1),
                is_read_by_user2=(sender == conversation.user2),
                deleted=0
            )
            message.save()
            
            conversation.last_message_timestamp = message.timestamp
            conversation.save(update_fields=['last_message_timestamp'])
            
            return message
        except Conversation.DoesNotExist:
            print(f"Conversation with id {conversation_id} does not exist.")
            return None
        except User.DoesNotExist:
            print(f"User with id {sender_id} does not exist.")
            return None

    # @sync_to_async
    # def create_notification(self, conversation_id, sender_id,message, notification_type, message_id):
        
    #     try:
    #         conversation = Conversation.objects.get(id=conversation_id)
    #         if conversation:
    #             if sender_id==conversation.user1.id:
    #                 user=conversation.user2.id
    #                 sender=conversation.user1.id
    #             else:
    #                 user=conversation.user1.id
    #                 sender=conversation.user2.id
                    
                
    #             print(user)
    #         user = User.objects.get(id=user)
    #         sender = User.objects.get(id=sender)
            
            
    #         notification = Notification(
    #             user=user,
    #             message=f"You have received a new message from {user.username}",
    #             notification_type=notification_type,
    #             link=f'/contact-list/?conversation_id={conversation.id}',
    #             sender=sender,
    #             sender_type='user',
    #             common_uuid=conversation.id
    #         )
    #         notification.save()
    #         return notification
    #     except User.DoesNotExist:
    #         print(f"User with id {user} does not exist.")
    
    @sync_to_async
    def create_notification(self, conversation_id, sender_id, message, notification_type, message_id):
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            if conversation:
                if sender_id == conversation.user1.id:
                    user = conversation.user2.id
                    sender = conversation.user1.id
                else:
                    user = conversation.user1.id
                    sender = conversation.user2.id

                print(user)
            user = User.objects.get(id=user)
            sender = User.objects.get(id=sender)
            print(user ,sender)
            # Check for an existing notification with similar details for the same user
            existing_notification = Notification.objects.filter(
                Q(user=user) &
                Q(sender=sender) &
                # Q(message=message) &
                # Q(common_uuid=conversation.id) &
                
                
                Q(is_read=False) &
                Q(notification_type=notification_type)
            ).first()
            print(existing_notification)
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                    f'global_{user.uuid}',  # WebSocket group name
                    {
                        'type': 'send_global_message',
                        "message":"working",
                        "conversation_id":str(conversation.id)
                    }
                )
            if existing_notification:
                print("Updating existing notification")
                if len(message)<25:
                    notification_message=message
                    
                else:
                    notification_message=f"{message[0:25]}..."
                # Update the existing notification
                existing_notification.count += 1
                existing_notification.message=notification_message
                existing_notification.timestamp = timezone.now()  # Update timestamp
                existing_notification.link = f'/contact-list/?conversation_id={conversation.id}'  # Update link if provided
                existing_notification.save()

                # Send the updated notification via WebSocket
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'user_{existing_notification.user.uuid}',  # WebSocket group name
                    {
                        'type': 'send_notification',
                        # "common_uuid":existing_notification.common_uuid,
                        'notification_id': existing_notification.id,
                        'message': existing_notification.message,
                        'notification_type': existing_notification.notification_type,
                        'timestamp': existing_notification.timestamp.isoformat(),
                        'sender': existing_notification.sender.id if existing_notification.sender else None,
                        'sender_profile_picture':str(existing_notification.sender.profile_picture),
                        
                        'link': existing_notification.link,
                        'count': existing_notification.count,
                        'sender_type': existing_notification.sender_type,
                        'sender_username': str(existing_notification.sender.username),
                        
                    }
                )
                print("Existing notification updated and sent")
                return existing_notification
            else:
                print("Creating new notification")
                if len(message)<25:
                    notification_message=message
                    
                else:
                    notification_message=f"{message[0:25]}..."
                # Create a new notification
                notification = Notification(
                    user=user,
                    message=notification_message,
                    notification_type=notification_type,
                    link=f'/contact-list/?conversation_id={conversation.id}',
                    sender=sender,
                    sender_type='user',
                    common_uuid=conversation.id
                )
                notification.save()

                # Send the new notification via WebSocket
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'user_{notification.user.uuid}',  # WebSocket group name
                    {
                        'type': 'send_notification',
                        'notification_id': notification.id,
                        # "common_uuid":notification.common_uuid,
                        'message': notification.message,
                        'notification_type': notification.notification_type,
                        'timestamp': notification.timestamp.isoformat(),
                        'sender': notification.sender.id if notification.sender else None,
                        'sender_profile_picture':str(notification.sender.profile_picture),
                        'link': notification.link,
                        'count': notification.count,
                        'sender_type': notification.sender_type,
                        'sender_username': str(notification.sender.username),
                        
                        
                    }
                )
                print("New notification created and sent")
                
                return notification

        except User.DoesNotExist:
            print(f"User with id {user} does not exist.")

    # @sync_to_async
    # def get_conversation(self, conversation_id):
    #     try:
    #         return Conversation.objects.get(id=conversation_id)
    #     except Conversation.DoesNotExist:
    #         return None


class GlobalChatConsumer(AsyncWebsocketConsumer):
    
    
    async def connect(self):
        self.user_uuid = self.scope['url_route']['kwargs']['uuid']
        self.group_name = f'global_{self.user_uuid}'

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

    async def send_global_message(self, event):
        # Send notification message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'global_message',
            "message":event["message"],
            "conversation_id":event['conversation_id']
            
            
        }))
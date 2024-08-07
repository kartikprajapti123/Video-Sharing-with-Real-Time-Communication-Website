from channels.generic.websocket import AsyncWebsocketConsumer
import json
from chat.models import Conversation, Message
from notification.models import Notification
from user.models import User
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

    @sync_to_async
    def create_notification(self, conversation_id, sender_id,message, notification_type, message_id):
        
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            if conversation:
                if sender_id==conversation.user1.id:
                    user=conversation.user2.id
                else:
                    user=conversation.user1.id
                
                print(user)
            user = User.objects.get(id=user)
            
            notification = Notification(
                user=user,
                message=f"You have received a new message from {user.username}",
                notification_type=notification_type,
                link=f'/contact-list/'
            )
            notification.save()
            return notification
        except User.DoesNotExist:
            print(f"User with id {user} does not exist.")

    # @sync_to_async
    # def get_conversation(self, conversation_id):
    #     try:
    #         return Conversation.objects.get(id=conversation_id)
    #     except Conversation.DoesNotExist:
    #         return None

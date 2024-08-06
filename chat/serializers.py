from chat.models import Conversation,Message,UploadedImage
from rest_framework import serializers

class ConversationsSerializer(serializers.ModelSerializer):
    user1_profile_picture=serializers.CharField(source='user1.profile_picture',required=False)
    user2_profile_picture=serializers.CharField(source='user2.profile_picture',required=False)
    user1_username=serializers.CharField(source='user1.username',required=False)
    user2_username=serializers.CharField(source='user2.username',required=False)
    
    class Meta:
        model=Conversation
        fields=[
            'id',
            'user1',
            'user1_profile_picture',
            "user1_username",
            'user2',
            "user2_profile_picture",
            "user2_username",
            'created_at',
            'updated_at',
            "last_message_timestamp",
        ]
        
class MessageSerializer(serializers.ModelSerializer):
    sender1_profile_picture=serializers.CharField(source='sender.profile_picture',required=False)
    sender1_username=serializers.CharField(source='sender.username',required=False)
    
    class Meta:
        model=Message
        fields=[
            'id',
            'conversation',
            'sender',
            'sender1_profile_picture',
            'sender1_username',
            'content',
            'file_url',
            'timestamp',
            'is_read_by_user1',
            'is_read_by_user2',
            
            ]
        
class UploadedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedImage
        fields = ['image', 'uploaded_at']
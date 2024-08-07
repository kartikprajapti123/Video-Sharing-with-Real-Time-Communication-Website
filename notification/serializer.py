from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_profile_picture = serializers.CharField(source='user.profile_picture', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'common_uuid',
            'id',
            'user',
            'user_username',
            'user_profile_picture',
            'message',
            'notification_type',
            'timestamp',
            'is_read',
            'link'
        ]

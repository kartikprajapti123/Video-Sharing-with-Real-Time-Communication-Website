# models.py
from django.db import models
from user.models import User
import uuid
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
# Create your models here.

class Notification(models.Model):
    common_uuid = models.UUIDField(default=uuid.uuid4, editable=False)  # Common UUID for a group
    id = models.AutoField(primary_key=True)  # Auto-incrementing ID for unique identification
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    message = models.TextField()
    notification_type = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    link = models.URLField(blank=True, null=True)
    deleted=models.IntegerField(default=0)

    def __str__(self):
        return f'Notification {self.id} for {self.user.username} - {self.notification_type}'

    def save(self, *args, **kwargs):
        super(Notification, self).save(*args, **kwargs)
        # Send notification via WebSocket
        channel_layer = get_channel_layer()
        print(channel_layer)
        print("uuid==",self.user.uuid)
        async_to_sync(channel_layer.group_send)(
            f'user_{self.user.uuid}',  # WebSocket group name
            {
                'type': 'send_notification',
                'message': self.message,
                'notification_type': self.notification_type,
                'timestamp': self.timestamp.isoformat(),
                'link': self.link
            }
        )
        print("notification is sended ")
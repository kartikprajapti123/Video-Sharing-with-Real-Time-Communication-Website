import uuid
from django.db import models
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone

class Notification(models.Model):
    common_uuid = models.UUIDField(default=uuid.uuid4, editable=False)  # Common UUID for a group of notifications
    id = models.AutoField(primary_key=True)  # Auto-incrementing ID for unique identification
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='notifications', on_delete=models.CASCADE)
    sender_type = models.CharField(max_length=10, choices=[('user', 'User'), ('admin', 'Admin')], default='user')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_notifications', on_delete=models.CASCADE, null=True, blank=True)  # The actual sender
    message = models.TextField()
    notification_type = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    link = models.URLField(blank=True, null=True)
    deleted = models.IntegerField(default=0)
    count = models.IntegerField(default=1)  # To track multiple similar messages

    def __str__(self):
        return f'Notification {self.id} for {self.user.username} - {self.notification_type}'


    class Meta:
        ordering = ['-timestamp']
        
        
class MainNotification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='main_notifications', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    link = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    deleted = models.IntegerField(default=0)
    
    def __str__(self):
        return f'main Notification for {self.user.username} '

        

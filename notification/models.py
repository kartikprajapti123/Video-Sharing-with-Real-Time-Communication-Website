import uuid
from django.db import models
from django.utils.timezone import now

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
        verbose_name="Chat Message Notification"
        
        
class MainNotification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='main_notifications', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    link = models.CharField(
    blank=True,
    null=True,
    default="#",
    max_length=100,
    verbose_name="Redirect Link",
    help_text="Example: https://www.bmy.fan/page/policy/ - The user will be redirected to the specified page upon clicking."
)

    is_read = models.BooleanField(default=False)
    deleted = models.IntegerField(default=0)
    
    def __str__(self):
        return f'main Notification for {self.user.username} '
    
        
    def save(self, *args, **kwargs):
        # Check if it's a new instance (i.e., no primary key set yet)
        if self.pk is None:
            print("creating and send_ing maeeaa")
            # This is a new notification, perform your custom action here
            message_content=self.message
            channel_layer=get_channel_layer()
            
            async_to_sync(channel_layer.group_send)(
                f"user_{self.user.uuid}",
                {
                    'type': 'send_main_notification',
                'notification_id': self.id,
                'message': message_content,
                'timestamp': str(now()),
                'link': self.link,
                }
            )

        # Call the original save method to save the object
        super(MainNotification, self).save(*args, **kwargs)
        
    
    class Meta:
        verbose_name="Send Notification To User"
        

    
        

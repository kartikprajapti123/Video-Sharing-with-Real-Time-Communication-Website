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

    # def save(self, *args, **kwargs):
    #     # Debugging: Print the user's UUID
    #     print(f"User UUID: {self.user.uuid}")

    #     # Check for an existing notification with similar details for the same user
    #     existing_notification = Notification.objects.filter(
    #         user=self.user,
    #         sender=self.sender,
    #         message=self.message,
    #         is_read=False,
    #         notification_type=self.notification_type
    #     ).first()

    #     if existing_notification:
    #         print("if")
    #         # Update the existing notification
    #         existing_notification.count += 1
    #         existing_notification.timestamp = timezone.now()  # Update timestamp
    #         existing_notification.link = self.link  # Update link if provided
    #         existing_notification.save()

    #         # Send the updated notification via WebSocket
    #         channel_layer = get_channel_layer()
    #         async_to_sync(channel_layer.group_send)(
    #             f'user_{existing_notification.user.uuid}',  # WebSocket group name
    #             {
    #                 'type': 'send_notification',
    #                 'notification_id': existing_notification.id,
    #                 'message': existing_notification.message,
    #                 'notification_type': existing_notification.notification_type,
    #                 'timestamp': existing_notification.timestamp.isoformat(),
    #                 'sender': existing_notification.sender.id if existing_notification.sender else None,
    #                 'link': existing_notification.link,
    #                 'count': existing_notification.count,
    #                 'sender_type': existing_notification.sender_type,
    #             }
    #         )
    #         print("Existing notification updated and sent")
    #         return
    #     else:
    #         print("else")
    #         # Save the new notification
    #         super().save(*args, **kwargs)

    #         # Send the new notification via WebSocket
    #         channel_layer = get_channel_layer()
    #         async_to_sync(channel_layer.group_send)(
    #             f'user_{self.user.uuid}',  # WebSocket group name
    #             {
    #                 'type': 'send_notification',
    #                 'notification_id': self.id,
    #                 'message': self.message,
    #                 'notification_type': self.notification_type,
    #                 'timestamp': self.timestamp.isoformat(),
    #                 'sender': self.sender.id if self.sender else None,
    #                 'link': self.link,
    #                 'count': self.count,
    #                 'sender_type': self.sender_type,
    #             }
    #         )
    #         print("New notification created and sent")

    class Meta:
        ordering = ['-timestamp']

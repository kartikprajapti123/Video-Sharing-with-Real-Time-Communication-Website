from django.db import models

# Create your models here.
from django.db import models
from user.models import User
from django.utils.timezone import now

from notification.models import MainNotification
from jerry_project import settings

class Post(models.Model):
    STATUS_CHOICE=[
        ("pending","pending"),
        ("approved","approved"),
        ("canceled","canceled")
        
        
    ]
    
    title = models.CharField(max_length=255,null=True,blank=True)
    video = models.FileField(upload_to='videos/', null=True, blank=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True)
    preview = models.FileField(upload_to='previews/', null=True, blank=True)  # Short video for preview
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_posts')
    description = models.TextField(null=True, blank=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_posts')
    deleted = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status=models.CharField(choices=STATUS_CHOICE,default="pending",null=True)

    def __str__(self):
        return self.title
    
    
    def create_notification_and_send_message(self, admin_user):
        # Create a notification for the user
        
        if self.status == "pending":
            return
        if (self.status=="canceled"):
            notification_message =f"<b style='color:black;'>Post Update:</b> Your post titled <b>{self.title}</b> has been <b>Rejected</b>. Please contact support if you have any questions."
            
        
        elif (self.status=="approved"):
            notification_message = f"<b style='color:black;'>Post Update:</b>Your post <b>{self.title}</b> has been <b>Approved</b>."
            
        
        
        mainnotification=MainNotification.objects.create(
            user=self.user,
            message=notification_message,
            link="/upload-post/"
        )
        
        print(mainnotification)

        # Send WebSocket notification
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{self.user.uuid}",
            {
                'type': 'send_main_notification',
                'notification_id': mainnotification.id,
                'message': notification_message,
                'timestamp': str(now()),
                'link': "/upload-post/",
            }
        )

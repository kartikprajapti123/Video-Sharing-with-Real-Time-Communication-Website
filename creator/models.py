from django.db import models
from django.utils.timezone import now

from jerry_project import settings
from user.models import User
from notification.models import MainNotification
# Create your models here.

class CreatorApproval(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('canceled', 'Canceled'),
    ]
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    gender = models.CharField( choices=GENDER_CHOICES, verbose_name="Gender",max_length=255,null=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='creator_approvals')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending',null=True)
    age = models.BooleanField(default=False, verbose_name="Age Above 21",null=True)
    terms_of_service = models.BooleanField(default=False, verbose_name="Terms and Conditions Accepted",null=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="creator_approval_created",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="creator_approval_updated",
    )
    deleted = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)
    
    def __str__(self) :
        return f"{self.user.email}--{self.status}"
    

    def create_notification_and_send_message(self, admin_user):
        # Create a notification for the user
        if (self.status=="canceled"):
            notification_message = f" <b style='color:black;'> Rejected !</b> Your creator approval has been rejected - Apply again"
            
        
        elif (self.status=="approved"):
            notification_message = f"<b style='color:black;'> Success !</b> Your creator approval has been acccepted - go to dashbored "
            
        
        
        mainnotification=MainNotification.objects.create(
            user=self.user,
            message=notification_message,
            link="/creator/"  # Update with the relevant link if necessary
        )

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
                'link': "/creator/",
            }
        )
from django.db import models
from user.models import User
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from notification.models import MainNotification
from django.utils.timezone import now


class Support_ticket(models.Model):
    priority_choices = [
        ("High", "High"),
        ("Medium", "Medium"),
        ("Low", "Low"),
    ]
    status_choices = [
        ("Open", "Open"),
        ("InProgress", "InProgress"),
        ("Closed", "Closed"),
    ]
    CATEGORY_CHOICES = [
        ("Technical", "Technical"),            
        ("Billing", "Billing"),                
        ("Account", "Account"),                
        ("Creator Approval", "Creator Approval"),
        ("Creator Onboarding", "Creator Onboarding"),
        ("Purchasing", "Purchasing"),          
        ("Refund", "Refund"),                  
        ("Video Approval", "Video Approval"),  
        ("Policy Violations", "Policy Violations"), 
        ("General", "General"),                
    ]
    title=models.CharField(max_length=100,null=True)
    ticket_id = models.CharField(max_length=50, unique=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="user_supoort_ticket")
    # subject = models.CharField(max_length=255)
    priority = models.CharField(choices=priority_choices, max_length=100, default="Low")
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=100, default="General")
    status=models.CharField(choices=status_choices,default="Open")
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.ticket_id} - {self.title} "
    

    def create_notification_and_send_message(self, admin_user):
        # Create a notification for the user
        notification_message=""
        if self.status == "Open":
            return
        if self.status == "Closed":
            notification_message = f"<b>Support Ticket Update:</b> Your Ticket {self.ticket_id} has been <b>Closed</b>."

        elif self.status == "InProgress":
            notification_message = f"<b>Support Ticket Update:</b> Your Ticket {self.ticket_id} has been <b>InProgress</b>."

        
        mainnotification=MainNotification.objects.create(
            user=self.user,
            message=notification_message,
            link="/support-ticket/"  # Update with the relevant link if necessary
        )
        print(mainnotification)
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{self.user.uuid}",
            {
                'type': 'send_main_notification',
                'notification_id': mainnotification.id,
                'message': notification_message,
                'timestamp': str(now()),
                'link': "/support-ticket/",
            }
        )

class Attachment(models.Model):
    support_ticket = models.ForeignKey(Support_ticket, related_name="attachments", on_delete=models.CASCADE)
    file = models.FileField(upload_to="attachments/")

    def __str__(self):
        return f"Attachment for {self.support_ticket.ticket_id}"

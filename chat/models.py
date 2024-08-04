from django.db import models
from user.models import User
import uuid
# Create your models here.
class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user1 = models.ForeignKey(User, related_name='conversations_as_user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='conversations_as_user2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted=models.IntegerField(default=0)
    last_message_timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversation {self.id} between {self.user1} and {self.user2}"
    
class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read_by_user1 = models.BooleanField(default=False)
    is_read_by_user2 = models.BooleanField(default=False)
    deleted=models.IntegerField(default=0)
    

    def __str__(self):
        return f"Message {self.id} from {self.sender} in Conversation {self.conversation.id}"
    
    # def save(self, *args, **kwargs):
    #     # Ensure the sender cannot mark a message as read for the other user
    #     if self.sender == self.conversation.user1:
    #         self.is_read_by_user2 = False
    #     elif self.sender == self.conversation.user2:
    #         self.is_read_by_user1 = False
    #     super().save(*args, **kwargs)
        

    def save(self, *args, **kwargs):
        # Update the last_message_timestamp of the conversation
        self.conversation.last_message_timestamp = self.timestamp
        self.conversation.save(update_fields=['last_message_timestamp'])
        super(Message, self).save(*args, **kwargs)
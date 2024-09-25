from django.db import models
from user.models import User
import uuid
import os

class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user1 = models.ForeignKey(User, related_name='conversations_as_user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='conversations_as_user2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.IntegerField(default=0)
    last_message_timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversation between {self.user1} and {self.user2} (Last message at {self.last_message_timestamp})"

    class Meta:
        verbose_name="Conversation Thread Between User"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    file_url = models.URLField(blank=True, null=True) 
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read_by_user1 = models.BooleanField(default=False)
    is_read_by_user2 = models.BooleanField(default=False)
    deleted = models.IntegerField(default=0)

    def __str__(self):
        return f"Message from {self.sender} in Conversation {self.conversation.id} at {self.timestamp}"

    def save(self, *args, **kwargs):
        # Update the last_message_timestamp of the conversation
        self.conversation.last_message_timestamp = self.timestamp
        self.conversation.save(update_fields=['last_message_timestamp'])
        super(Message, self).save(*args, **kwargs)
        
    class Meta:
        verbose_name="Conversation Messages (Here you will see all the messages of all conversations)"
        verbose_name_plural="Conversation Messages (Here you will see all the messages of all conversations)"
        


class UploadedImage(models.Model):
    image = models.ImageField(upload_to='profile_pictures/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return os.path.basename(self.image.name)  # Only returns the file name

    @property
    def upload_time(self):
        return self.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')  # Format the upload time

    class Meta:
        verbose_name = "Uploaded Image "
        verbose_name_plural = "Uploaded Images"

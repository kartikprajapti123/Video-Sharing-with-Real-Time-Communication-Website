from django.db import models
from user.models import User
from django.utils.timezone import now

class Follow(models.Model):
    FOLLOW_STATUS = (
        ('follow', 'Follow'),
        ('unfollow', 'Unfollow'),
    )
    
    by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_by_follow")
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_to_follow")
    status = models.CharField(max_length=8, choices=FOLLOW_STATUS, default='follow')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.by_user.username} {self.status}ed {self.to_user.username}'

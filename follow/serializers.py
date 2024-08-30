from rest_framework import serializers
from .models import Follow

class FollowSerializer(serializers.ModelSerializer):
    by_user_username = serializers.CharField(source='by_user.username', read_only=True)
    to_user_username = serializers.CharField(source='to_user.username', read_only=True)
    to_user_uuid = serializers.CharField(source='to_user.uuid', read_only=True)
    
    to_user_profile_picture = serializers.CharField(source='to_user.profile_picture', read_only=True)
    by_user_profile_picture = serializers.CharField(source='by_user.profile_picture', read_only=True)
    by_user_uuid = serializers.CharField(source='by_user.uuid', read_only=True)

    
    class Meta:
        model = Follow
        fields = [
            'id',
            'by_user',
            'by_user_uuid',
            
            'by_user_username',
            'by_user_profile_picture',
            'to_user',
            'to_user_uuid',
            
            'to_user_username',
            'to_user_profile_picture',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate(self, data):
        by_user = data.get('by_user')
        to_user = data.get('to_user')
        
        # Ensure that a user cannot follow themselves
        if by_user == to_user:
            raise serializers.ValidationError("A user cannot follow themselves.")
        
        # Additional validation checks can be added here if necessary
        
        return data
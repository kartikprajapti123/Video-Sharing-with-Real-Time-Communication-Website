from rest_framework import serializers
from .models import CreatorApproval

class CreatorApprovalSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', required=False)
    
    class Meta:
        model = CreatorApproval
        fields = [
            'id',
            'user',
            'user_email',
            'gender',
            'status',
            'age',
            'gender',
            'terms_of_service',
            'created_by',
            'updated_by',
            'deleted',
            'created_at',
            'updated_at'
        ]

    def validate(self, data):
        print(data)
        age = data.get('age')
        print(age)
        gender = data.get('gender')
        terms_of_service = data.get('terms_of_service')
        
        # Ensure that all required fields are provided and not empty
        if terms_of_service is None or not terms_of_service:
            raise serializers.ValidationError("The 'Terms_of_service' should be accepted")
        
        if age is None:
            raise serializers.ValidationError("The 'Age' field is required.")
        
        if gender is None:
            raise serializers.ValidationError("The 'Gender' field is required.")
        
        return data
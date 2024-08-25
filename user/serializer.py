from rest_framework import serializers
from user.models import User
from utils.generate_otp import generate_otp
import re

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    email=serializers.EmailField(required=True)
    phone =serializers.CharField(required=False)
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email', 'phone', 'password', 'password2','otp','profile_picture'
        ]
        
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        password2 = attrs.get('password2')
        email=attrs.get('email')
        
        if username and User.objects.filter(username=username,email_verified=True).exists():
            raise serializers.ValidationError("Username is already registered! Try another.")
        
        if email and User.objects.filter(email=email,email_verified=True).exists():
            raise serializers.ValidationError("Email is already registered! Try another.")
        
        if password and (len(password) < 8 or len(password) > 14):
            raise serializers.ValidationError("Password length should be between 8 to 14 characters.")
        
        if password and password2 and password != password2:
            raise serializers.ValidationError("Password and Re-Password is not matching.")
        
        return attrs
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        password2 = validated_data.pop('password2')

        user = User.objects.create(**validated_data)
        user.is_active = True
        user.otp = generate_otp()
        user.set_password(password)
        user.save()
        
        return user


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    email=serializers.EmailField(required=True)
    
    class Meta:
        model=User
        fields=['id', 'username', 'first_name', 'last_name', 'email', 'password', 'password2','profile_picture','bio','uuid']
        
        
class UserMyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username', 'first_name', 'last_name', 'email', 'profile_picture', 'phone', 'bio','uuid']
        
    def validate(self, attrs):
        if not attrs.get('username'):
            raise serializers.ValidationError("Username cannot be empty.")
        
        
        user_id = self.instance.id if self.instance else None
        
        # Validate unique username
        if User.objects.filter(username=attrs['username']).exclude(id=user_id).exists():
            raise serializers.ValidationError("This username is already taken.")
        
        # Validate unique email
        phone = attrs.get('phone')
        if phone:
            phone_regex = re.compile(r'^\+?1?\d{9,15}$')
            if not phone_regex.match(phone):
                raise serializers.ValidationError({"phone": "Invalid phone number format."})

            # Check if phone number already exists for another user
            if User.objects.filter(phone=phone).exclude(id=user_id).exists():
                raise serializers.ValidationError({"phone": "A user with this phone number already exists."})

        # Validate unique phone
        profile_picture = attrs.get('profile_picture')
        if profile_picture:
            valid_extensions = ['jpg', 'jpeg', 'png']
            file_extension = profile_picture.name.split('.')[-1].lower()
            if file_extension not in valid_extensions:
                raise serializers.ValidationError("Profile picture must be in jpg, jpeg, or png format.")
        
        # Profile picture validation (add any custom validation if needed)
        bio = attrs.get('bio')
        if bio and len(bio) < 50:
            raise serializers.ValidationError("Bio must be at least 50 characters long.")
        
        return attrs
class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username', 'first_name', 'last_name', 'profile_picture', 'bio','uuid','email']
        

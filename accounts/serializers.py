from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import EmployeeProfile

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'role', 'phone_number', 'profile_picture', 'face_shape', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Password encryption is important
        user = User.objects.create_user(**validated_data)
        return user

class EmployeeProfileSerializer(serializers.ModelSerializer):
    # Flatten user details for easy access
    email = serializers.ReadOnlyField(source='user.email')
    name = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = EmployeeProfile
        fields = ['id', 'user', 'email', 'name', 'expertise', 'commission_rate', 'is_available']
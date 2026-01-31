from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import EmployeeProfile

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # profile_picture ഇതിൽ ഉണ്ടെന്ന് ഉറപ്പാക്കുന്നു
        fields = ['id', 'email', 'username', 'role', 'phone_number', 'profile_picture', 'face_shape', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class EmployeeProfileSerializer(serializers.ModelSerializer):
    # 👇 യൂസറുടെ ഫോട്ടോയും പേരും കിട്ടാൻ ഇത് ഉപയോഗിക്കുന്നു (Nested Serializer)
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = EmployeeProfile
        fields = [
            'id', 
            'user_details', # ഇതിലൂടെ പേരും ഫോട്ടോയും കിട്ടും
            'job_title', 
            'years_of_experience', 
            'rating', 
            'bio', 
            'is_available'
        ]
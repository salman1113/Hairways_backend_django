from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from .models import EmployeeProfile, Attendance, Payroll

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    # Customer Profile Fields (Writable)
    face_shape = serializers.CharField(source='customer_profile.face_shape', required=False, allow_null=True, allow_blank=True)
    points = serializers.IntegerField(source='customer_profile.points', read_only=True) # Keep points read-only
    tier = serializers.CharField(source='customer_profile.tier', read_only=True) # Keep tier read-only
    
    bio = serializers.CharField(source='customer_profile.bio', required=False, allow_blank=True)
    preferences = serializers.CharField(source='customer_profile.preferences', required=False, allow_blank=True)
    birth_date = serializers.DateField(source='customer_profile.birth_date', required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'role', 'phone_number', 'profile_picture', 
            'face_shape', 'points', 'tier', 'bio', 'preferences', 'birth_date'
        ]
        read_only_fields = ['role', 'points', 'tier']

    def update(self, instance, validated_data):
        # 1. Extract Nested Data (if any)
        profile_data = {}
        for field in ['customer_profile']:
            if field in validated_data:
                profile_data_nested = validated_data.pop(field)
                if isinstance(profile_data_nested, dict):
                    profile_data.update(profile_data_nested)

        # 2. Update User Fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 3. Update CustomerProfile Fields
        if hasattr(instance, 'customer_profile') and profile_data:
            profile = instance.customer_profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'phone_number']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class AttendanceSerializer(serializers.ModelSerializer):
    date = serializers.DateField(read_only=True)  # Explicitly define to avoid Swagger datetime error
    
    class Meta:
        model = Attendance
        fields = '__all__'

class PayrollSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.username', read_only=True)
    month = serializers.DateField(format="%Y-%m-%d")

    class Meta:
        model = Payroll
        fields = '__all__'
class EmployeeProfileSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    attendance_today = serializers.SerializerMethodField()
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    phone_number = serializers.CharField(source='user.phone_number')

    class Meta:
        model = EmployeeProfile
        fields = [
            'id', 'user_details', 
            'username', 'email', 'phone_number', 
            'job_title', 'years_of_experience', 'bio', 
            'rating', 'review_count', 'commission_rate', 'wallet_balance', 
            'is_available', 'shift_start', 'shift_end', 
            'attendance_today'
        ]

    def get_attendance_today(self, obj):
        today = timezone.now().date()
        attendance = obj.attendance.filter(date=today).first()
        return AttendanceSerializer(attendance).data if attendance else None

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user
        if user_data:
            user.username = user_data.get('username', user.username)
            user.email = user_data.get('email', user.email)
            user.phone_number = user_data.get('phone_number', user.phone_number)
            user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

# CREATION SERIALIZER
class EmployeeCreationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(write_only=True)

    # Optional Fields
    job_title = serializers.CharField(required=False, default="Stylist")
    years_of_experience = serializers.IntegerField(required=False, default=0)
    bio = serializers.CharField(required=False, allow_blank=True, default="")
    rating = serializers.DecimalField(max_digits=3, decimal_places=1, required=False, default=5.0)
    review_count = serializers.IntegerField(required=False, default=0)
    wallet_balance = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0.00)
    commission_rate = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, default=0.00)
    shift_start = serializers.TimeField(required=False, allow_null=True)
    shift_end = serializers.TimeField(required=False, allow_null=True)
    is_available = serializers.BooleanField(required=False, default=True)

    class Meta:
        model = EmployeeProfile
        fields = [
            'username', 'email', 'password', 'phone_number', 
            'job_title', 'commission_rate', 'shift_start', 'shift_end', 
            'is_available', 'years_of_experience', 'bio', 'rating', 'review_count', 'wallet_balance'
        ]

    def validate(self, attrs):
        if User.objects.filter(email=attrs.get('email')).exists():
            raise serializers.ValidationError({"email": "This email is already registered."})
        if User.objects.filter(username=attrs.get('username')).exists():
            raise serializers.ValidationError({"username": "This username is already taken."})
        return attrs

    def create(self, validated_data):
        try:
            with transaction.atomic():
                # 1. Extract User Data
                user_data = {
                    k: validated_data.pop(k) 
                    for k in ['username', 'email', 'password', 'phone_number']
                }
                
                # 2. Create User (Triggers Signal)
                user = User.objects.create_user(**user_data, role='EMPLOYEE')
                
                # 3. Get auto-created profile
                if hasattr(user, 'employee_profile'):
                    employee = user.employee_profile
                else:
                    # Fallback (Safety)
                    employee = EmployeeProfile.objects.create(user=user)

                # 4. Update the profile with form data
                for attr, value in validated_data.items():
                    setattr(employee, attr, value)
                
                employee.save()
                return employee


        except Exception as e:
            raise serializers.ValidationError({"error": str(e)})

class GoogleLoginSerializer(serializers.Serializer):
    id_token = serializers.CharField(required=True)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()
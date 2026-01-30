from rest_framework import serializers
from .models import Booking, BookingItem, BarberQueue
from accounts.serializers import UserSerializer, EmployeeProfileSerializer
from services.serializers import ServiceSerializer

class BookingItemSerializer(serializers.ModelSerializer):
    # Service details will be fetched automatically via prefetch_related in views
    service_name = serializers.ReadOnlyField(source='service.name')
    service_duration = serializers.ReadOnlyField(source='service.duration_minutes')

    class Meta:
        model = BookingItem
        fields = ['id', 'service', 'service_name', 'service_duration', 'price']

class BookingSerializer(serializers.ModelSerializer):
    # Nested Serializers for detailed info (Optimized in View)
    items = BookingItemSerializer(many=True, read_only=True)
    customer_name = serializers.SerializerMethodField()

    # If customer is null (Walk-in), show guest name
    display_name = serializers.SerializerMethodField()

    def get_customer_name(self, obj):
        # കസ്റ്റമർ ഉണ്ടെങ്കിൽ മാത്രം ഇമെയിൽ കൊടുക്കും, ഇല്ലെങ്കിൽ None
        return obj.customer.email if obj.customer else None

    def get_display_name(self, obj):
        if obj.customer:
            return obj.customer.email
        return f"{obj.guest_name} (Guest)"

    class Meta:
        model = Booking
        fields = [
            'id', 'token_number', 'booking_date', 'status', 
            'customer', 'customer_name', 'display_name', 
            'guest_name', 'guest_phone', 'is_walk_in',
            'estimated_start_time', 'total_price', 'items'
        ]
        extra_kwargs = {
            'customer': {'read_only': True}, # കസ്റ്റമറെ മാറ്റാൻ പറ്റില്ല
            'is_walk_in': {'read_only': True} # ഇത് ബാക്കെൻഡ് തീരുമാനിക്കും
        }

    def get_display_name(self, obj):
        if obj.customer:
            return obj.customer.email
        return f"{obj.guest_name} (Guest)"

class BarberQueueSerializer(serializers.ModelSerializer):
    employee_name = serializers.ReadOnlyField(source='employee.user.email')

    class Meta:
        model = BarberQueue
        fields = ['id', 'employee', 'employee_name', 'joined_at']
from rest_framework import serializers
from .models import Booking, BookingItem, BarberQueue
from accounts.serializers import UserSerializer, EmployeeProfileSerializer
from services.serializers import ServiceSerializer
from services.models import Service # Import Service model
from datetime import datetime, timedelta, date

class BookingItemSerializer(serializers.ModelSerializer):
    service_name = serializers.ReadOnlyField(source='service.name')
    service_duration = serializers.ReadOnlyField(source='service.duration_minutes')
    
    # Service ID accept cheyyan PrimaryKeyRelatedField venam
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all())

    class Meta:
        model = BookingItem
        fields = ['id', 'service', 'service_name', 'service_duration', 'price']

class BookingSerializer(serializers.ModelSerializer):
    # items write cheyyanum pattanam (read_only maatti)
    items = BookingItemSerializer(many=True) 
    
    customer_name = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()

    def get_customer_name(self, obj):
        return obj.customer.email if obj.customer else None

    def get_display_name(self, obj):
        if obj.customer:
            return obj.customer.email
        return f"{obj.guest_name} (Guest)"

    class Meta:
        model = Booking
        fields = [
            'id', 'token_number', 'booking_date', 'booking_time', # booking_time added
            'status', 'employee', # employee added
            'customer', 'customer_name', 'display_name', 
            'guest_name', 'guest_phone', 'is_walk_in',
            'estimated_start_time', 'total_price', 'items'
        ]
        extra_kwargs = {
            'customer': {'read_only': True},
            'is_walk_in': {'read_only': True},
            'token_number': {'read_only': True} # Token auto-generate aanu
        }

    # 🔥 CRITICAL: Items save cheyyanulla function
    def create(self, validated_data):
        # 1. Items separate cheyyunnu
        items_data = validated_data.pop('items')
        
        # 2. User login cheythittundengil customer aayi set cheyyum
        user = self.context['request'].user
        if user.is_authenticated:
            validated_data['customer'] = user
            validated_data['is_walk_in'] = False
        
        # 3. Booking create cheyyunnu
        booking = Booking.objects.create(**validated_data)
        
        # 4. Items loop cheythu save cheyyunnu
        for item in items_data:
            BookingItem.objects.create(booking=booking, **item)
            
        return booking
    

    def validate(self, data):
        employee = data.get('employee')
        booking_date = data.get('booking_date')
        booking_time = data.get('booking_time')

        if employee and booking_date and booking_time:
            # Start checking from the requested time
            current_time_check = booking_time
            
            # Loop to find the next free slot
            # (Limit to 10 checks to avoid infinite loops if whole day is busy)
            for _ in range(10): 
                conflicting_booking = Booking.objects.filter(
                    employee=employee,
                    booking_date=booking_date,
                    booking_time=current_time_check,
                    status__in=['PENDING', 'CONFIRMED', 'IN_PROGRESS']
                ).first()

                if conflicting_booking:
                    # If busy, add duration (default 30 mins) to jump to next slot
                    duration = 30 
                    if conflicting_booking.items.exists():
                        duration = conflicting_booking.items.first().service.duration_minutes
                    
                    # Calculate next slot
                    dummy_date = datetime.combine(date.today(), current_time_check)
                    next_slot = dummy_date + timedelta(minutes=duration)
                    current_time_check = next_slot.time() # Update time for next loop check
                else:
                    # Found a free slot!
                    # If this free slot is NOT the original requested time, raise error
                    if current_time_check != booking_time:
                         raise serializers.ValidationError({
                            "error": "Slot Taken",
                            "message": f"Stylist is busy until {current_time_check.strftime('%H:%M')}.",
                            "suggested_time": current_time_check.strftime("%H:%M")
                        })
                    # If it IS the requested time, loop breaks and validation passes
                    break 

        return data
    
    
class BarberQueueSerializer(serializers.ModelSerializer):
    employee_name = serializers.ReadOnlyField(source='employee.user.email')

    class Meta:
        model = BarberQueue
        fields = ['id', 'employee', 'employee_name', 'joined_at']
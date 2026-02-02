from rest_framework import serializers
from .models import Booking, BookingItem, BarberQueue
from services.models import Service
from accounts.serializers import UserSerializer, EmployeeProfileSerializer
from datetime import datetime, timedelta, date

class BookingItemSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    service_duration = serializers.IntegerField(source='service.duration_minutes', read_only=True)
    
    class Meta:
        model = BookingItem
        fields = ['id', 'service', 'service_name', 'service_duration', 'price']

class BookingSerializer(serializers.ModelSerializer):
    items = BookingItemSerializer(many=True, read_only=True)
    customer_details = UserSerializer(source='customer', read_only=True)
    employee_details = EmployeeProfileSerializer(source='employee', read_only=True)

    service_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )

    class Meta:
        model = Booking
        fields = [
            'id', 'token_number', 
            'customer', 'customer_details', 
            'guest_name', 'guest_phone', 'is_walk_in',
            'employee', 'employee_details',
            'booking_date', 'booking_time', 'status',
            'estimated_start_time', 'actual_start_time', 'actual_end_time',
            'total_price', 'created_at',
            'items', 'service_ids'
        ]
        read_only_fields = ['token_number', 'total_price', 'created_at', 'status', 'actual_start_time', 'actual_end_time']

    # 🔥 FIXED: Time Overlap Validation (ഇടയിലുള്ള സമയം ബ്ലോക്ക് ചെയ്യുന്നു)
    def validate(self, data):
        employee = data.get('employee')
        booking_date = data.get('booking_date')
        booking_time = data.get('booking_time')
        service_ids = data.get('service_ids', [])

        if employee and booking_date and booking_time:
            # 1. പുതിയ ബുക്കിംഗിന്റെ ദൈർഘ്യം (Duration) കണക്കാക്കുന്നു
            req_duration = 0
            if service_ids:
                services = Service.objects.filter(id__in=service_ids)
                req_duration = sum(s.duration_minutes for s in services)
            
            if req_duration == 0: req_duration = 30 # Default safety
            
            # 2. പുതിയ ബുക്കിംഗിന്റെ Start & End Time കണ്ടുപിടിക്കുന്നു
            req_start_dt = datetime.combine(booking_date, booking_time)
            req_end_dt = req_start_dt + timedelta(minutes=req_duration)

            # 3. ആ ബാർബർക്ക് അന്നേ ദിവസമുള്ള എല്ലാ ബുക്കിംഗുകളും എടുക്കുന്നു
            day_bookings = Booking.objects.filter(
                employee=employee,
                booking_date=booking_date,
                status__in=['PENDING', 'CONFIRMED', 'IN_PROGRESS']
            ).prefetch_related('items__service')

            # 4. ഓരോ ബുക്കിംഗുമായും കൂട്ടിമുട്ടുന്നുണ്ടോ (Overlap) എന്ന് നോക്കുന്നു
            for booking in day_bookings:
                # നിലവിലുള്ള ബുക്കിംഗിന്റെ ദൈർഘ്യം
                exist_duration = sum(item.service.duration_minutes for item in booking.items.all())
                if exist_duration == 0: exist_duration = 30
                
                # നിലവിലുള്ള ബുക്കിംഗിന്റെ Start & End Time
                exist_start_dt = datetime.combine(booking.booking_date, booking.booking_time)
                exist_end_dt = exist_start_dt + timedelta(minutes=exist_duration)

                # 🔥 OVERLAP CHECK FORMULA:
                # (NewStart < OldEnd) AND (NewEnd > OldStart)
                if req_start_dt < exist_end_dt and req_end_dt > exist_start_dt:
                    
                    # Conflict കണ്ടെത്തി! ആ ബുക്കിംഗ് തീരുന്ന സമയം സജസ്റ്റ് ചെയ്യുന്നു.
                    suggested_time = exist_end_dt.time()
                    
                    raise serializers.ValidationError({
                        "error": "Slot Taken",
                        "message": f"Stylist is busy until {suggested_time.strftime('%H:%M')}.",
                        "suggested_time": suggested_time.strftime("%H:%M")
                    })

        return data

    def create(self, validated_data):
        service_ids = validated_data.pop('service_ids', [])
        booking = Booking.objects.create(**validated_data)
        
        total_price = 0
        for service_id in service_ids:
            try:
                service = Service.objects.get(id=service_id)
                BookingItem.objects.create(booking=booking, service=service, price=service.price)
                total_price += service.price
            except Service.DoesNotExist:
                continue
            
        booking.total_price = total_price
        booking.save()
        return booking

class BarberQueueSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.username', read_only=True)
    employee_image = serializers.ImageField(source='employee.user.profile_picture', read_only=True)
    
    class Meta:
        model = BarberQueue
        fields = ['id', 'employee', 'employee_name', 'employee_image', 'joined_at']
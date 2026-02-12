import pytest
from datetime import date, time
from django.contrib.auth import get_user_model
from bookings.models import Booking
from bookings.serializers import BookingSerializer
from services.models import Service, Category
from accounts.models import EmployeeProfile

User = get_user_model()

@pytest.mark.django_db
def test_prevent_booking_overlap():
    # 1. Setup Data
    stylist_user = User.objects.create_user(email='stylist@test.com', username='stylist', password='password')
    stylist = EmployeeProfile.objects.create(user=stylist_user, job_title="Expert Stylist")

    customer_user = User.objects.create_user(email='customer@test.com', username='customer', password='password')
    
    category = Category.objects.create(name="Hair Services")
    service = Service.objects.create(name="Haircut", price=50.00, duration_minutes=30, category=category)

    # 2. Create First Valid Booking (10:00 - 10:30)
    booking_date = date(2025, 1, 1)
    Booking.objects.create(
        customer=customer_user,
        employee=stylist,
        booking_date=booking_date,
        booking_time=time(10, 0),
        status='CONFIRMED'
    )
    
    # Manually create the related BookingItem for the first booking to ensure duration calc works if logic depends on it
    # Note: The serializer validation checks `day_bookings` items.
    first_booking = Booking.objects.get(booking_time=time(10, 0))
    first_booking.items.create(service=service, price=service.price)

    # 3. Attempt Overlapping Booking (10:15 - 10:45)
    data = {
        'customer': customer_user.id,
        'employee': stylist.id,
        'booking_date': booking_date,
        'booking_time': time(10, 15), # Overlaps!
        'service_ids': [service.id]
    }

    serializer = BookingSerializer(data=data)
    
    # 4. Assert Validation Fails
    with pytest.raises(Exception) as e:
        serializer.is_valid(raise_exception=True)
    
    assert "Slot Taken" in str(e.value)

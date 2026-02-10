
import os
import django
from datetime import date

# Setup Django first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saloon_core.settings')
django.setup()

from django.conf import settings
from rest_framework.test import APIRequestFactory, force_authenticate
from bookings.views import BookingViewSet
from bookings.models import Booking
from django.contrib.auth import get_user_model

User = get_user_model()

def test_cancellation():
    print("Testing cancellation...")
    
    # helper to create user
    user, _ = User.objects.get_or_create(username='admin_tester', email='admin@test.com', defaults={'role': 'ADMIN', 'is_staff': True})
    
    # Create a booking
    booking = Booking.objects.create(
        customer=user,
        booking_date=date.today(),
        booking_time='12:00:00',
        token_number='T-TEST-CANCEL',
        status='PENDING'
    )
    print(f"Created Booking: {booking.id} - {booking.status}")

    # Use ViewSet to cancel
    factory = APIRequestFactory()
    view = BookingViewSet.as_view({'post': 'cancel_booking'})
    
    request = factory.post(f'/api/v1/bookings/bookings/{booking.id}/cancel_booking/')
    force_authenticate(request, user=user)
    
    response = view(request, pk=booking.id)
    print(f"Cancellation Response: {response.status_code} {response.data}")
    
    booking.refresh_from_db()
    print(f"Booking Status After: {booking.status}")

if __name__ == "__main__":
    test_cancellation()

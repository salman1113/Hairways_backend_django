
import os
import django
from datetime import date
from rest_framework.test import APIRequestFactory, force_authenticate

# Setup Django 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saloon_core.settings')
django.setup()

from bookings.views import BookingViewSet
from bookings.models import Booking
from django.contrib.auth import get_user_model

User = get_user_model()

def verify_fetch():
    print("--- Verifying Admin Fetch ---")
    
    # 1. Get Admin User
    admin_user = User.objects.filter(role='ADMIN').first()
    if not admin_user:
        print("No Admin user found! Creating temp admin.")
        admin_user = User.objects.create(username='temp_admin', email='temp_admin@test.com', role='ADMIN', is_staff=True)
    else:
        print(f"Using Admin: {admin_user.email} (Role: {admin_user.role})")

    # 2. Check DB for ANY bookings
    all_bookings = Booking.objects.all().order_by('-created_at')
    print(f"Total Bookings in DB: {all_bookings.count()}")
    if all_bookings.exists():
        latest = all_bookings.first()
        print(f"Latest Booking: ID={latest.id}, Date={latest.booking_date}, Token={latest.token_number}")
    else:
        print("No bookings in DB to fetch.")
        return

    # 3. Simulate API Call: GET /api/v1/bookings/bookings/ (No params -> All)
    factory = APIRequestFactory()
    view = BookingViewSet.as_view({'get': 'list'})

    print("\nTest 1: Fetch ALL (no date param)")
    req_all = factory.get('/api/v1/bookings/bookings/')
    force_authenticate(req_all, user=admin_user)
    res_all = view(req_all)
    print(f"Status: {res_all.status_code}")
    print(f"Count returned: {len(res_all.data)}")
    
    # 4. Simulate API Call: GET /api/v1/bookings/bookings/?date=TODAY
    today = date.today()
    print(f"\nTest 2: Fetch TODAY ({today})")
    req_today = factory.get(f'/api/v1/bookings/bookings/?date={today}')
    force_authenticate(req_today, user=admin_user)
    res_today = view(req_today)
    print(f"Status: {res_today.status_code}")
    print(f"Count returned: {len(res_today.data)}")
    if len(res_today.data) > 0:
        print(f"Sample: {res_today.data[0]['token_number']}")

    # 5. Simulate API Call: GET /api/v1/bookings/bookings/?date=LATEST_BOOKING_DATE
    if all_bookings.exists():
        latest_date = all_bookings.first().booking_date
        print(f"\nTest 3: Fetch Latest Date ({latest_date})")
        req_latest = factory.get(f'/api/v1/bookings/bookings/?date={latest_date}')
        force_authenticate(req_latest, user=admin_user)
        res_latest = view(req_latest)
        print(f"Status: {res_latest.status_code}")
        print(f"Count returned: {len(res_latest.data)}")

if __name__ == "__main__":
    verify_fetch()

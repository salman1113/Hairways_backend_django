
import os
import django
from django.conf import settings
from datetime import date

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saloon_core.settings')
django.setup()

from bookings.models import Booking
from django.db import connection

def debug_db():
    print("--- Database Debug ---")
    db_settings = settings.DATABASES['default']
    print(f"Engine: {db_settings['ENGINE']}")
    print(f"Name: {db_settings['NAME']}")
    # print(f"Host: {db_settings['HOST']}") # safe to print usually

    print(f"Connection Vendor: {connection.vendor}")
    
    today = date.today()
    count = Booking.objects.filter(booking_date=today).count()
    print(f"Bookings for Today ({today}): {count}")
    
    # Create one to test persistence
    print("Creating a test booking...")
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.first()
        if user:
            b = Booking.objects.create(
                customer=user,
                booking_date=today,
                booking_time='14:00:00',
                token_number='T-DEBUG'
            )
            print(f"Created: {b.id} - {b.token_number}")
        else:
            print("No user found to create booking.")
    except Exception as e:
        print(f"Creation Failed: {e}")

if __name__ == "__main__":
    debug_db()

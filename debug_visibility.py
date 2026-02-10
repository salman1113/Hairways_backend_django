
import os
import django
from datetime import date

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saloon_core.settings')
django.setup()

from bookings.models import Booking
from django.contrib.auth import get_user_model

User = get_user_model()

def debug_visibility():
    print("--- Debugging Visibility ---")
    
    # 1. Check Date
    today = date.today()
    print(f"Server Date: {today}")
    
    # 2. Check ALL Bookings
    bookings = Booking.objects.all()
    print(f"Total Bookings count: {bookings.count()}")
    for b in bookings:
        print(f" - ID: {b.id}, Date: {b.booking_date}, Token: {b.token_number}, Status: {b.status}")

    # 3. Check All Users
    print("\n--- Users & Roles ---")
    for u in User.objects.all():
        print(f"User: {u.email}, Role: {u.role}, IsStaff: {u.is_staff}, ID: {u.id}")

    # 4. Check Filtering Logic Simulation
    print("\n--- Simulation ---")
    # Simulate an Admin user (find one)
    admin_user = User.objects.filter(role='ADMIN').first()
    if not admin_user:
        admin_user = User.objects.filter(is_staff=True).first()
    
    if admin_user:
        print(f"Simulating request for Admin: {admin_user.email}")
        queryset = Booking.objects.all()
        if admin_user.is_authenticated and not (admin_user.is_staff or admin_user.role in ['ADMIN', 'MANAGER', 'EMPLOYEE']):
             queryset = queryset.filter(customer=admin_user)
             print(" -> Filtered by customer (RESTRICTED)")
        else:
             print(" -> NOT Filtered (VISIBLE)")
        
        count = queryset.filter(booking_date=today).count()
        print(f" -> Visible bookings for today: {count}")
    else:
        print("No Admin user found to simulate.")

if __name__ == "__main__":
    debug_visibility()

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saloon_core.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# email = input("Enter the admin email to fix: ") 
# Hardcoding for now or finding the superuser
users = User.objects.filter(is_superuser=True)

print(f"Found {users.count()} superusers.")

for user in users:
    print(f"Fixing user: {user.email}")
    if user.role != 'ADMIN':
        user.role = 'ADMIN'
        print(f"  - Set role to ADMIN")
    
    if not user.is_email_verified:
        user.is_email_verified = True
        print(f"  - Set is_email_verified to True")
        
    user.save()
    print("  - Saved.")

print("Done.")

from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom User Model:
    - Replaces default Django User.
    - Uses 'email' as the unique identifier for login.
    - Includes 'role' to distinguish between Admin, Manager, Employee, and Customer.
    """
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('MANAGER', 'Manager'),
        ('EMPLOYEE', 'Employee'),
        ('CUSTOMER', 'Customer'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='CUSTOMER')
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    face_shape = models.CharField(max_length=20, null=True, blank=True)
    
    # 🌟 NEW: Gamified Loyalty System [PDF Module 2.3]
    points = models.PositiveIntegerField(default=0, help_text="Loyalty Points (1 Haircut = 10 Points)")
    tier = models.CharField(max_length=20, default="Silver", choices=[("Silver", "Silver"), ("Gold", "Gold"), ("Platinum", "Platinum")])

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone_number']

    def __str__(self):
        return self.email

class EmployeeProfile(models.Model):
    """
    Extended Profile for Employees:
    - Linked one-to-one with the User model.
    - Stores professional details like Job Title, Experience, and Commission Rate.
    - Tracks shift timings and wallet balance.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    
    # Professional Details
    job_title = models.CharField(max_length=50, default="Stylist")
    years_of_experience = models.PositiveIntegerField(default=1)
    expertise = models.CharField(max_length=255, default="General")
    
    # Public Info
    bio = models.TextField(blank=True, max_length=300)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)
    review_count = models.PositiveIntegerField(default=0)

    # Admin / Internal
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Commission percentage per service")
    is_available = models.BooleanField(default=True)

    # 🌟 NEW: Shift Management [PDF Module 5]
    shift_start = models.TimeField(null=True, blank=True, help_text="Shift Start Time")
    shift_end = models.TimeField(null=True, blank=True, help_text="Shift End Time")
    
    # 🌟 NEW: Personal Earnings Tracker [PDF Module 3.3]
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Accumulated Commission")

    def __str__(self):
        return f"{self.user.email} - {self.job_title}"

class Attendance(models.Model):
    """
    🌟 NEW: Biometric HR & Payroll System [PDF Module 1.2]
    Tracks daily check-in/check-out for payroll calculation.
    """
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, related_name='attendance')
    date = models.DateField(auto_now_add=True)
    check_in = models.TimeField(auto_now_add=True)
    check_out = models.TimeField(null=True, blank=True)
    is_late = models.BooleanField(default=False)

    class Meta:
        unique_together = ('employee', 'date')

    def __str__(self):
        return f"{self.employee.user.username} - {self.date}"
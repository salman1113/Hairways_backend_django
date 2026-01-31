from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('MANAGER', 'Manager'),
        ('EMPLOYEE', 'Employee'),
        ('CUSTOMER', 'Customer'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='CUSTOMER')
    email = models.EmailField(unique=True)  # Primary identifier for authentication
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    face_shape = models.CharField(max_length=20, null=True, blank=True)  # AI detected shape

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone_number']

    def __str__(self):
        return self.email

class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    
    # Professional Details
    job_title = models.CharField(max_length=50, default="Stylist") # e.g., Senior Barber
    years_of_experience = models.PositiveIntegerField(default=1) # e.g., 5 Years
    expertise = models.CharField(max_length=255, default="General", help_text="Comma separated skills")
    
    # Public Info
    bio = models.TextField(blank=True, max_length=300, help_text="Short intro for customers")
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0) # e.g., 4.8
    review_count = models.PositiveIntegerField(default=0) # Total reviews received

    # Admin / Internal
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.email} - {self.job_title}"
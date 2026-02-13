from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN') # Auto-set role to ADMIN
        extra_fields.setdefault('is_email_verified', True) # Auto-verify email
        
        return self.create_user(email, password, **extra_fields)

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

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='CUSTOMER', db_index=True)  # Indexed for filtering users by role (e.g., finding all employees)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    # Auth & Security
    is_email_verified = models.BooleanField(default=False)
    is_first_login_done = models.BooleanField(default=False, help_text="For Admins to force password reset or OTP on first login")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone_number']

    objects = CustomUserManager()

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
    job_title = models.CharField(max_length=50, default="Stylist", db_index=True)  # Indexed for searching employees by title
    years_of_experience = models.PositiveIntegerField(default=1)
    expertise = models.CharField(max_length=255, default="General")
    
    # Public Info
    bio = models.TextField(blank=True, max_length=300)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)
    review_count = models.PositiveIntegerField(default=0)

    # Admin / Internal
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Commission percentage per service")
    is_available = models.BooleanField(default=True)

    shift_start = models.TimeField(null=True, blank=True, help_text="Shift Start Time")
    shift_end = models.TimeField(null=True, blank=True, help_text="Shift End Time")
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Accumulated Commission")
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, default=15000.00, help_text="Fixed Monthly Salary")

    def __str__(self):
        return f"{self.user.email} - {self.job_title}"

class CustomerProfile(models.Model):
    """
    Extended Profile for Customers:
    - Default profile logic for regular users.
    - Stores loyalty info and preferences.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    
    face_shape = models.CharField(max_length=20, null=True, blank=True)
    points = models.PositiveIntegerField(default=0, help_text="Loyalty Points (1 Haircut = 10 Points)")
    tier = models.CharField(max_length=20, default="Silver", choices=[("Silver", "Silver"), ("Gold", "Gold"), ("Platinum", "Platinum")])
    
    # New Details
    bio = models.TextField(blank=True, help_text="Customer notes or bio")
    preferences = models.TextField(blank=True, help_text="Styling preferences (JSON or Text)")
    birth_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.tier}"

class Attendance(models.Model):
    """
    NEW: Biometric HR & Payroll System
    Tracks daily check-in/check-out for payroll calculation.
    """
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, related_name='attendance')
    date = models.DateField(auto_now_add=True, db_index=True)  # Indexed for daily attendance reports
    check_in = models.TimeField(auto_now_add=True)
    check_out = models.TimeField(null=True, blank=True)
    is_late = models.BooleanField(default=False)

    class Meta:
        unique_together = ('employee', 'date')

    def __str__(self):
        return f"{self.employee.user.username} - {self.date}"

class Payroll(models.Model):
    """
    Monthly Payroll Record
    - Stores the snapshot of salary for a specific month.
    """
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, related_name='payrolls')
    month = models.DateField(help_text="First day of the month (e.g. 2023-10-01)")
    
    # Financial Components
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    commission_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    total_salary = models.DecimalField(max_digits=10, decimal_places=2)
    
    status = models.CharField(
        max_length=10, 
        choices=[('PENDING', 'Pending'), ('PAID', 'Paid')], 
        default='PENDING'
    )
    generated_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('employee', 'month')

    def __str__(self):
        return f"Payroll {self.employee.user.username} - {self.month.strftime('%B %Y')}"
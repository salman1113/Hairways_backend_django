from django.db import models
from django.conf import settings
from services.models import Service
from accounts.models import EmployeeProfile

class BarberQueue(models.Model):
    """
    Manages the 'Rotation List' of employees waiting for customers.
    Logic: First person in this table gets the next 'Any Barber' customer.
    """
    employee = models.OneToOneField(EmployeeProfile, on_delete=models.CASCADE, related_name='queue_position')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['joined_at'] 
        verbose_name = "Barber Queue Position"

    def __str__(self):
        return f"{self.employee.user.email} - Joined at {self.joined_at}"

class Booking(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )

    # 1. Customer Link (Optional to allow Walk-ins)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
    related_name='bookings', null=True, blank=True)
    
    # 2. Walk-in Details (For non-registered guests)
    guest_name = models.CharField(max_length=100, blank=True, null=True, default="Walk-in Guest")
    guest_phone = models.CharField(max_length=15, blank=True, null=True)
    
    # 3. Flag (To identify if this is a walk-in booking)
    is_walk_in = models.BooleanField(default=False)

    employee = models.ForeignKey(EmployeeProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_bookings')
    
    token_number = models.PositiveIntegerField()
    booking_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    # Time Tracking (Critical for AI & Queue Logic)
    estimated_start_time = models.DateTimeField(null=True, blank=True)
    actual_start_time = models.DateTimeField(null=True, blank=True)
    actual_end_time = models.DateTimeField(null=True, blank=True)

    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        if self.customer:
            return f"Token #{self.token_number} - {self.customer.email}"
        return f"Token #{self.token_number} - {self.guest_name} (Walk-in)"

class BookingItem(models.Model):
    """
    Specific services selected within a booking.
    """
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='items')
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.service.name} for Token #{self.booking.token_number}"
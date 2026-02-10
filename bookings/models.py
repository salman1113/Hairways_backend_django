from django.db import models
from django.conf import settings
from services.models import Service
from accounts.models import EmployeeProfile

class BarberQueue(models.Model):
    employee = models.OneToOneField(EmployeeProfile, on_delete=models.CASCADE, related_name='queue_position')
    joined_at = models.DateTimeField(auto_now_add=True, db_index=True)  # Indexed for FIFO ordering

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

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)
    guest_name = models.CharField(max_length=100, blank=True, null=True, default="Walk-in Guest")
    guest_phone = models.CharField(max_length=15, blank=True, null=True)
    is_walk_in = models.BooleanField(default=False)
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_bookings')
    token_number = models.CharField(max_length=20, null=True, blank=True)
    booking_date = models.DateField(db_index=True)  # Indexed as it's the primary filter for daily views
    booking_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', db_index=True)  # Indexed for efficient status filtering
    estimated_start_time = models.DateTimeField(null=True, blank=True)
    actual_start_time = models.DateTimeField(null=True, blank=True)
    actual_end_time = models.DateTimeField(null=True, blank=True)
    
    # Reschedule Tracking
    is_rescheduled = models.BooleanField(default=False, help_text="Can only reschedule once")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)  # Indexed for recent bookings list

    class Meta:
        ordering = ['-created_at']
        unique_together = [
            ('booking_date', 'token_number'),
            ('employee', 'booking_date', 'booking_time')  # Prevent double-booking: An employee cannot have two bookings at the same time
        ]

    def __str__(self):
        return f"Token #{self.token_number} - {self.status}"

class BookingItem(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='items')
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.service.name} for Token #{self.booking.token_number}"
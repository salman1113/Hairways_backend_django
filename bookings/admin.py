from django.contrib import admin
from .models import Booking, BookingItem, BarberQueue

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('token_number', 'customer', 'guest_name', 'status', 'booking_date')
    list_filter = ('status', 'booking_date')

admin.site.register(BookingItem)
admin.site.register(BarberQueue)
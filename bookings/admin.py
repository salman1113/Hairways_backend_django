from django.contrib import admin
from .models import Booking, BookingItem, BarberQueue

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('token_number', 'customer', 'guest_name', 'status', 'booking_date')
    list_filter = ('status', 'booking_date')
    actions = ['cancel_bookings']

    @admin.action(description='Cancel selected bookings')
    def cancel_bookings(self, request, queryset):
        # Filter out already completed/cancelled
        updated_count = queryset.exclude(status__in=['COMPLETED', 'CANCELLED']).update(status='CANCELLED')
        self.message_user(request, f"{updated_count} bookings successfully cancelled.")

admin.site.register(BookingItem)
admin.site.register(BarberQueue)
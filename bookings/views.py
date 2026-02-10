from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Prefetch
from django.utils import timezone
from .models import Booking, BookingItem, BarberQueue
from .serializers import BookingSerializer, BarberQueueSerializer

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Booking.objects.select_related(
            'customer', 'employee', 'employee__user'
        ).prefetch_related(
            Prefetch('items', queryset=BookingItem.objects.select_related('service'))
        ).order_by('-created_at')

        date_param = self.request.query_params.get('date')
        if date_param:
            queryset = queryset.filter(booking_date=date_param)

        """
        Custom Queryset Filter:
        - Admin/Staff: Can see ALL bookings.
        - Customers: Can strictly see ONLY their own bookings.
        - Also supports filtering by ?date=YYYY-MM-DD
        """
        user = self.request.user
        if user.is_authenticated and not (user.is_staff or user.role in ['ADMIN', 'MANAGER', 'EMPLOYEE']):
             return queryset.filter(customer=user)
        return queryset
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # Sequential Token Generation (Reset Daily)
    # Sequential Token Generation (Reset Daily)
    def perform_create(self, serializer):
        """
        Sequential Token Generation:
        - Generates a daily resetting token (e.g., T-1, T-2).
        - format: T-{max + 1}
        """
        booking_date = serializer.validated_data.get('booking_date')
        
        # Robust way to find the next token number for this date
        daily_bookings = Booking.objects.filter(booking_date=booking_date).values_list('token_number', flat=True)
        max_number = 0
        for token_str in daily_bookings:
            if token_str and token_str.startswith('T-'):
                try:
                    num = int(token_str.split('-')[1])
                    if num > max_number:
                        max_number = num
                except (IndexError, ValueError):
                    continue
        
        next_token = max_number + 1
        token = f"T-{next_token}"

        if self.request.user.is_authenticated:
            serializer.save(customer=self.request.user, is_walk_in=False, token_number=token)
        else:
            serializer.save(token_number=token)

    # --- Other Actions (Cancel, Reschedule, Job Timer) ---

    @action(detail=True, methods=['post'])
    def cancel_booking(self, request, pk=None):
        """
        Cancels a booking if it is not already completed or cancelled.
        """
        booking = self.get_object()
        if booking.status in ['COMPLETED', 'CANCELLED']:
            return Response({'error': 'Cannot cancel this booking'}, status=400)
        booking.status = 'CANCELLED'
        booking.save()
        return Response({'status': 'Booking cancelled'})

    @action(detail=True, methods=['post'])
    def reschedule(self, request, pk=None):
        """
        Reschedules a booking by shifting it forward by 15 minutes.
        - Allowed only once per booking.
        """
        booking = self.get_object()
        if booking.is_rescheduled: return Response({"error": "Reschedule limit reached"}, status=400)
        
        from datetime import timedelta, datetime, date
        # Add 15 mins logic
        current_datetime = datetime.combine(date.today(), booking.booking_time)
        new_time = (current_datetime + timedelta(minutes=15)).time()
        
        booking.booking_time = new_time
        booking.is_rescheduled = True
        booking.save()
        return Response({"status": "Rescheduled", "new_time": new_time})

    @action(detail=True, methods=['post'])
    def start_job(self, request, pk=None):
        """
        Marks booking as IN_PROGRESS and records the actual start time.
        """
        booking = self.get_object()
        booking.status = 'IN_PROGRESS'
        booking.actual_start_time = timezone.now()
        booking.save()
        return Response({"status": "Job Started"})

    @action(detail=True, methods=['post'])
    def finish_job(self, request, pk=None):
        """
        Marks booking as COMPLETED, records end time, and calculates employee commission.
        """
        booking = self.get_object()
        if booking.status == 'COMPLETED': return Response({"status": "Already Completed"}, status=400)
        
        booking.status = 'COMPLETED'
        booking.actual_end_time = timezone.now()
        booking.save()
        
        # Commission Calculation
        if booking.employee and booking.employee.commission_rate > 0:
            commission = (booking.total_price * booking.employee.commission_rate) / 100
            booking.employee.wallet_balance += commission
            booking.employee.save()
            
        return Response({"status": "Job Finished"})

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Admin Dashboard Stats:
        - Total Revenue (Today)
        - Active Customers
        - Queue Length
        """
        if request.user.role != 'ADMIN': return Response({"error": "Admin only"}, status=403)
        today = timezone.now().date()
        todays_bookings = Booking.objects.filter(booking_date=today)
        return Response({
            "total_revenue": sum(b.total_price for b in todays_bookings),
            "active_customers": todays_bookings.filter(status='IN_PROGRESS').count(),
            "pending_queue": todays_bookings.filter(status='PENDING').count(),
            "completed_today": todays_bookings.filter(status='COMPLETED').count()
        })

class BarberQueueViewSet(viewsets.ModelViewSet):
    serializer_class = BarberQueueSerializer
    queryset = BarberQueue.objects.select_related('employee', 'employee__user').order_by('joined_at')
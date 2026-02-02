from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Prefetch
from django.utils import timezone
from .models import Booking, BookingItem, BarberQueue
from .serializers import BookingSerializer, BarberQueueSerializer
import random 

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Booking.objects.select_related(
            'customer', 'employee', 'employee__user'
        ).prefetch_related(
            Prefetch('items', queryset=BookingItem.objects.select_related('service'))
        ).order_by('-created_at')

        user = self.request.user
        # Admin & Employees see all, Customers see only theirs
        if user.is_authenticated and not (user.is_staff or user.role in ['ADMIN', 'MANAGER', 'EMPLOYEE']):
             return queryset.filter(customer=user)
        return queryset
    
    # 🔥 Create Method with Better Error Handling
    def create(self, request, *args, **kwargs):
        print(f"📥 Booking Request from {request.user}: {request.data}") 
        
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            print("❌ Booking Failed:", serializer.errors)
            # If validation fails (e.g., Slot Taken), send the error details clearly
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        token = f"T-{random.randint(1000, 9999)}"
        if self.request.user.is_authenticated:
            serializer.save(customer=self.request.user, is_walk_in=False, token_number=token)
        else:
            serializer.save(token_number=token)

    # --- Other Actions (Cancel, Reschedule, Job Timer) ---

    @action(detail=True, methods=['post'])
    def cancel_booking(self, request, pk=None):
        booking = self.get_object()
        if booking.status in ['COMPLETED', 'CANCELLED']:
            return Response({'error': 'Cannot cancel this booking'}, status=400)
        booking.status = 'CANCELLED'
        booking.save()
        return Response({'status': 'Booking cancelled'})

    @action(detail=True, methods=['post'])
    def reschedule(self, request, pk=None):
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
        booking = self.get_object()
        booking.status = 'IN_PROGRESS'
        booking.actual_start_time = timezone.now()
        booking.save()
        return Response({"status": "Job Started"})

    @action(detail=True, methods=['post'])
    def finish_job(self, request, pk=None):
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
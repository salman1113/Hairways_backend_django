from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Prefetch
from .models import Booking, BookingItem, BarberQueue
from .serializers import BookingSerializer, BarberQueueSerializer
import random # 👈 For Token Generation

class BookingViewSet(viewsets.ModelViewSet):
    """
    Highly Optimized ViewSet for Bookings.
    Solves N+1 Query Problem using select_related & prefetch_related.
    """
    serializer_class = BookingSerializer

    def get_queryset(self):
        # 🚀 OPTIMIZATION STRATEGY:
        # 1. select_related: Fetch 'customer' and 'employee' in the SAME query.
        # 2. prefetch_related: Fetch all 'items' and their 'services' efficiently.
        
        queryset = Booking.objects.select_related(
            'customer', 
            'employee', 
            'employee__user'  # To get employee name without extra query
        ).prefetch_related(
            Prefetch('items', queryset=BookingItem.objects.select_related('service'))
        ).order_by('-created_at')

        # Admin can see all, Customer sees only theirs
        user = self.request.user
        if user.is_authenticated and not (user.is_staff or user.role in ['ADMIN', 'MANAGER']):
             return queryset.filter(customer=user)
        
        return queryset
    
    def perform_create(self, serializer):
        # 🔥 Generate Token (e.g., T-4592)
        token = f"T-{random.randint(1000, 9999)}"
        
        # Save with User (if logged in) and Token
        if self.request.user.is_authenticated:
            serializer.save(customer=self.request.user, is_walk_in=False, token_number=token)
        else:
            serializer.save(token_number=token)

    
    @action(detail=True, methods=['post'])
    def cancel_booking(self, request, pk=None):
        try:
            booking = self.get_object()
            
            # ഇതിനകം കഴിഞ്ഞതോ ക്യാൻസൽ ആയതോ മാറ്റാൻ സമ്മതിക്കരുത്
            if booking.status in ['COMPLETED', 'CANCELLED']:
                return Response({'error': 'Cannot cancel this booking'}, status=status.HTTP_400_BAD_REQUEST)

            booking.status = 'CANCELLED'
            booking.save()
            return Response({'status': 'Booking cancelled successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class BarberQueueViewSet(viewsets.ModelViewSet):
    """
    Manages the waiting list of barbers.
    """
    serializer_class = BarberQueueSerializer
    queryset = BarberQueue.objects.select_related(
        'employee', 
        'employee__user'
    ).order_by('joined_at')
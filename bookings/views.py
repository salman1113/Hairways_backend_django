from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Prefetch
from .models import Booking, BookingItem, BarberQueue
from .serializers import BookingSerializer, BarberQueueSerializer

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
        return Booking.objects.select_related(
            'customer', 
            'employee', 
            'employee__user'  # To get employee name without extra query
        ).prefetch_related(
            Prefetch('items', queryset=BookingItem.objects.select_related('service'))
        ).order_by('-created_at')
    
    def perform_create(self, serializer):
        # ലോഗിൻ ചെയ്ത യൂസർ ആണെങ്കിൽ, അവരെ കസ്റ്റമർ ആയി സെറ്റ് ചെയ്യുക
        if self.request.user.is_authenticated:
            serializer.save(customer=self.request.user, is_walk_in=False)
        else:
            # ലോഗിൻ ചെയ്യാത്തവർ (Walk-in) ആണെങ്കിൽ മാത്രം സേവ് ചെയ്യുക
            serializer.save()

class BarberQueueViewSet(viewsets.ModelViewSet):
    """
    Manages the waiting list of barbers.
    """
    serializer_class = BarberQueueSerializer
    queryset = BarberQueue.objects.select_related(
        'employee', 
        'employee__user'
    ).order_by('joined_at')
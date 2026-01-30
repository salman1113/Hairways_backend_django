from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookingViewSet, BarberQueueViewSet

router = DefaultRouter()
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'queue', BarberQueueViewSet, basename='queue')

urlpatterns = [
    path('', include(router.urls)),
]
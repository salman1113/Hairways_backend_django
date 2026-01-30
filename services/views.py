from rest_framework import viewsets
from .models import Service, Category
from .serializers import ServiceSerializer, CategorySerializer
from rest_framework import viewsets, permissions

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Optimized API: Uses 'prefetch_related' to fetch services in a single query.
    """
    # Best Way:
    queryset = Category.objects.prefetch_related('services').all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Optimized API: Uses 'select_related' to fetch category details instantly.
    """
    # Best Way:
    queryset = Service.objects.select_related('category').filter(is_active=True)
    serializer_class = ServiceSerializer
    permission_classes = [permissions.AllowAny]
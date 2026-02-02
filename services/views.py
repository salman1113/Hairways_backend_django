from rest_framework import viewsets, permissions
from rest_framework import serializers
from .models import Service, Category, Product
from .serializers import ServiceSerializer, CategorySerializer

# Simple Serializer for Product
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

# Custom Permission
class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'ADMIN'

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.prefetch_related('services').all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.select_related('category').filter(is_active=True)
    serializer_class = ServiceSerializer
    permission_classes = [IsAdminOrReadOnly]

class ProductViewSet(viewsets.ModelViewSet):
    """
    API for Inventory Management [PDF Module 1.4]
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
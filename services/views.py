from rest_framework import viewsets, permissions
from rest_framework import serializers
from .models import Service, Category, Product
from .serializers import ServiceSerializer, CategorySerializer

from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from .serializers import ServiceSerializer, CategorySerializer, BulkServiceSerializer


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

    @swagger_auto_schema(request_body=BulkServiceSerializer(many=True))
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        Bulk create categories and services.
        Expected JSON:
        [
            {
                "category_name": "Cutting",
                "services": [
                    {"name": "Zero Slope", "price": 150, "duration": 30},
                    ...
                ]
            },
            ...
        ]
        """
        serializer = BulkServiceSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                created_count = 0
                for item in serializer.validated_data:
                    category_name = item['category_name']
                    services_data = item['services']

                    category, _ = Category.objects.get_or_create(name=category_name)

                    for service_data in services_data:
                        Service.objects.update_or_create(
                            name=service_data['name'],
                            category=category,
                            defaults={
                                'price': service_data['price'],
                                'duration_minutes': service_data.get('duration', 30), # Default 30 min
                                'description': service_data.get('description', ''),
                                'is_active': True
                            }
                        )
                        created_count += 1
                
                return Response({"status": "success", "message": f"{created_count} services processed."})
        except Exception as e:
            return Response({"error": str(e)}, status=400)

class ProductViewSet(viewsets.ModelViewSet):
    """
    API for Inventory Management [PDF Module 1.4]
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
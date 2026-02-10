from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from .models import Service, Category, Product
from .serializers import (
    ServiceSerializer, CategorySerializer, ProductSerializer, 
    BulkServiceSerializer
)

# --- PERMISSIONS ---

from accounts.permissions import IsAdminOrReadOnly

# --- CATEGORY APIS ---

class CategoryListCreateApi(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        queryset = Category.objects.prefetch_related('services').all()
        serializer = CategorySerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryDetailApi(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(Category, pk=pk)

    def get(self, request, pk):
        category = self.get_object(pk)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    def put(self, request, pk):
        category = self.get_object(pk)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        category = self.get_object(pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# --- SERVICE APIS ---

class ServiceListApi(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        queryset = Service.objects.select_related('category').filter(is_active=True)
        # Optional: Filter by Category
        category_id = request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        serializer = ServiceSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ServiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ServiceDetailApi(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(Service, pk=pk)

    def get(self, request, pk):
        service = self.get_object(pk)
        serializer = ServiceSerializer(service)
        return Response(serializer.data)

    def put(self, request, pk):
        service = self.get_object(pk)
        serializer = ServiceSerializer(service, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        service = self.get_object(pk)
        service.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class BulkServiceCreateApi(APIView):
    permission_classes = [IsAdminOrReadOnly]

    @swagger_auto_schema(request_body=BulkServiceSerializer(many=True))
    def post(self, request):
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
            }
        ]
        """
        serializer = BulkServiceSerializer(data=request.data, many=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
                                'duration_minutes': service_data.get('duration', 30),
                                'description': service_data.get('description', ''),
                                'is_active': True
                            }
                        )
                        created_count += 1
                
                return Response({"status": "success", "message": f"{created_count} services processed."})
        except Exception as e:
            return Response({"error": str(e)}, status=400)

# --- PRODUCT APIS ---

class ProductListCreateApi(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        queryset = Product.objects.all()
        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductDetailApi(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(Product, pk=pk)

    def get(self, request, pk):
        product = self.get_object(pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, pk):
        product = self.get_object(pk)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        product = self.get_object(pk)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
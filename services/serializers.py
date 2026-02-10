from rest_framework import serializers
from .models import Service, Category, Product

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):

    # To display category name in API response (Read Only)
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = Service
        fields = [
            'id', 
            'name', 
            'description', 
            'price', 
            'duration_minutes', 
            'image', 
            'is_active', 
            'category',
            'category_name'
        ]

class ProductSerializer(serializers.ModelSerializer):
    """
    Inventory Management Serializer
    """
    class Meta:
        model = Product
        fields = '__all__'

class BulkServiceSerializer(serializers.Serializer):
    """
    Serializer to handle bulk creation of services under a category
    """
    category_name = serializers.CharField(max_length=50)
    services = serializers.ListField(
        child=serializers.DictField() 
    )
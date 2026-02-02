from rest_framework import serializers
from .models import Service, Category, Product

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    # കാണുമ്പോൾ കാറ്റഗറിയുടെ പേര് കിട്ടാൻ (Read Only)
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
            'category',       # 👈 പ്രധാനം: ഇത് വഴി കാറ്റഗറി ID സേവ് ചെയ്യാം
            'category_name'   # 👈 ഇത് വഴി കാറ്റഗറി പേര് കാണാം
        ]

class ProductSerializer(serializers.ModelSerializer):
    """
    Inventory Management Serializer
    """
    class Meta:
        model = Product
        fields = '__all__'
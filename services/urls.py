from django.urls import path
from .views import (
    CategoryListCreateApi, CategoryDetailApi,
    ServiceListApi, ServiceDetailApi, BulkServiceCreateApi,
    ProductListCreateApi, ProductDetailApi
)

urlpatterns = [
    # Categories
    path('categories/', CategoryListCreateApi.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetailApi.as_view(), name='category-detail'),

    # Services
    path('services/', ServiceListApi.as_view(), name='service-list'),
    path('services/<int:pk>/', ServiceDetailApi.as_view(), name='service-detail'),
    path('services/bulk_create/', BulkServiceCreateApi.as_view(), name='service-bulk-create'),

    # Products
    path('products/', ProductListCreateApi.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetailApi.as_view(), name='product-detail'),
]
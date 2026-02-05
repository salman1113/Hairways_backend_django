from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiceViewSet, CategoryViewSet, ProductViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
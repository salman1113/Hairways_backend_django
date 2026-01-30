from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiceViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'services', ServiceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
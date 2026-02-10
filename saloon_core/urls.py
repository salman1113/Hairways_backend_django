from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static

# Swagger Imports
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger Schema View Configuration
schema_view = get_schema_view(
   openapi.Info(
      title="Hair Ways API",
      default_version='v1',
      description="Detailed API documentation for Hair Ways Salon Booking Application",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="support@hairways.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Services API Link
    path('api/v1/services/', include('services.urls')),

    # Bookings API Link
    path('api/v1/bookings/', include('bookings.urls')),

    # Accounts Link
    path('api/v1/accounts/', include('accounts.urls')),
    
    # DRF Login/Logout (Session Auth)
    path('api-auth/', include('rest_framework.urls')),
    
    # Handle Django default login/logout URLs used by Swagger/Admin
    path('accounts/', include('rest_framework.urls')),

    #  Swagger and Redoc URLs
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# (Media URL Setting):
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
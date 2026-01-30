from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Services API Link
    path('api/v1/services/', include('services.urls')),

    # Bookings API Link
    path('api/v1/bookings/', include('bookings.urls')),

    # Accounts Link
    path('api/v1/accounts/', include('accounts.urls')),
]

# (Media URL Setting):
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
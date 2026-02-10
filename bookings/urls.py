from django.urls import path
from .views import (
    BookingListCreateApi, BookingDetailApi, BookingCancelApi, 
    BookingRescheduleApi, StartJobApi, FinishJobApi, 
    BookingTrackApi, EmployeeDashboardApi, AdminStatsApi
)

urlpatterns = [
    # Core Booking CRUD
    path('bookings/', BookingListCreateApi.as_view(), name='booking-list-create'),
    path('bookings/<int:pk>/', BookingDetailApi.as_view(), name='booking-detail'),

    # Actions
    path('bookings/<int:pk>/cancel/', BookingCancelApi.as_view(), name='booking-cancel'),
    path('bookings/<int:pk>/reschedule/', BookingRescheduleApi.as_view(), name='booking-reschedule'),
    path('bookings/<int:pk>/track/', BookingTrackApi.as_view(), name='booking-track'),
    
    # Employee Operations
    path('bookings/<int:pk>/start_job/', StartJobApi.as_view(), name='start-job'),
    path('bookings/<int:pk>/finish_job/', FinishJobApi.as_view(), name='finish-job'),
    path('employee/dashboard/', EmployeeDashboardApi.as_view(), name='employee-dashboard'),

    # Admin
    path('admin/stats/', AdminStatsApi.as_view(), name='admin-stats'),
]
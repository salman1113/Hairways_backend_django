from django.urls import path, include
from .views import (
    RegisterApi, UserProfileApi, 
    EmployeeListCreateApi, EmployeeDetailApi,
    AttendanceListApi, AttendancePunchApi,
    PayrollListApi, GeneratePayrollApi,
    GoogleLoginApi, UserListApi
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # Auth & User
    path('register/', RegisterApi.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/google/', GoogleLoginApi.as_view(), name='google-login'),
    path('me/', UserProfileApi.as_view(), name='user-profile'),
    path('users/', UserListApi.as_view(), name='user-list'),
        
    # Employees
    path('employees/', EmployeeListCreateApi.as_view(), name='employee-list'),
    path('employees/<int:pk>/', EmployeeDetailApi.as_view(), name='employee-detail'),
    
    # Attendance
    path('attendance/', AttendanceListApi.as_view(), name='attendance-list'),
    path('attendance/punch/', AttendancePunchApi.as_view(), name='attendance-punch'),

    # Payroll
    path('payroll/', PayrollListApi.as_view(), name='payroll-list'),
    path('payroll/generate/', GeneratePayrollApi.as_view(), name='payroll-generate'),
]
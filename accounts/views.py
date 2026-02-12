from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, filters
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import EmployeeProfile, Attendance, Payroll
from .serializers import (
    UserSerializer, EmployeeProfileSerializer, AttendanceSerializer, 
    EmployeeCreationSerializer, UserRegistrationSerializer, PayrollSerializer,
    GoogleLoginSerializer
)
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from django.db.models import Sum
from datetime import datetime, date
from django.conf import settings
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.utils.crypto import get_random_string

User = get_user_model()
from .permissions import IsAdminOrReadOnly, IsEmployeeOwnerOrReadOnly, IsSelfOrAdmin

# --- USER APIS ---

class RegisterApi(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "user": UserSerializer(user).data,
                "message": "User created successfully. Please login."
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileApi(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get current user profile"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        """Update current user profile"""
        print(f"DEBUG: PATCH /me/ payload: {request.data}")
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        print(f"DEBUG: Serializer Errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserListApi(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Admin only: List all users"""
        if request.user.role != 'ADMIN':
            return Response({"error": "Admin only"}, status=status.HTTP_403_FORBIDDEN)
        
        queryset = User.objects.all().order_by('-date_joined')
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

# --- EMPLOYEE APIS ---

class EmployeeListCreateApi(APIView):
    permission_classes = [IsAdminOrReadOnly] 

    def get(self, request):
        queryset = EmployeeProfile.objects.select_related('user').all()
        # Search functionality
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(job_title__icontains=search)
        
        serializer = EmployeeProfileSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Admin creates employee (User + Profile)"""
        if request.user.role != 'ADMIN':
             return Response({"error": "Admin only"}, status=403)
             
        serializer = EmployeeCreationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmployeeDetailApi(APIView):
    permission_classes = [IsEmployeeOwnerOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(EmployeeProfile, pk=pk)

    def get(self, request, pk):
        profile = self.get_object(pk)
        serializer = EmployeeProfileSerializer(profile)
        return Response(serializer.data)

    def patch(self, request, pk):
        profile = self.get_object(pk)
        self.check_object_permissions(request, profile)
        
        serializer = EmployeeProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        profile = self.get_object(pk)
        if request.user.role != 'ADMIN': return Response({"error": "Admin only"}, status=403)
        user = profile.user
        user.delete() # Hard delete user
        return Response(status=status.HTTP_204_NO_CONTENT)

# --- ATTENDANCE APIS ---

class AttendanceListApi(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = Attendance.objects.all().order_by('-date', '-check_in')
        
        # Filter by employee
        employee_id = request.query_params.get('employee')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
            
        serializer = AttendanceSerializer(queryset, many=True)
        return Response(serializer.data)

class AttendancePunchApi(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        if not hasattr(user, 'employee_profile'):
             return Response({"error": "Not an employee"}, status=403)
        
        profile = user.employee_profile
        today = timezone.now().date()
        now_time = timezone.now().time()
        
        # Check for existing record today
        attendance, created = Attendance.objects.get_or_create(employee=profile, date=today)
        
        if created:
            # First punch = Check In
            attendance.check_in = now_time
            # Late Logic (e.g., after 10 AM)
            if profile.shift_start and now_time > profile.shift_start:
                attendance.is_late = True
            attendance.save()
            return Response({"status": "Checked In", "time": now_time})
        else:
            # Second punch = Check Out
            if attendance.check_out:
                return Response({"status": "Already Checked Out"}, status=400)
            
            attendance.check_out = now_time
            attendance.save()
            return Response({"status": "Checked Out", "time": now_time})

# --- PAYROLL APIS ---

class PayrollListApi(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == 'ADMIN':
            queryset = Payroll.objects.select_related('employee__user').all().order_by('-month')
        elif hasattr(user, 'employee_profile'):
            queryset = Payroll.objects.filter(employee=user.employee_profile).order_by('-month')
        else:
            return Response({"error": "Not authorized"}, status=403)
        
        serializer = PayrollSerializer(queryset, many=True)
        return Response(serializer.data)

class GeneratePayrollApi(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def post(self, request):
        if request.user.role != 'ADMIN':
            return Response({"error": "Admin only"}, status=403)

        month_str = request.data.get('month') # expected 'YYYY-MM-DD' (e.g., '2023-10-01')
        if not month_str:
            return Response({"error": "Month is required (YYYY-MM-DD)"}, status=400)
            
        try:
            month_date = datetime.strptime(month_str, '%Y-%m-%d').date()
            # Normalize to first of month
            month_start = date(month_date.year, month_date.month, 1)
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=400)

        employees = EmployeeProfile.objects.all()
        generated_count = 0

        with transaction.atomic():
            for emp in employees:
                # 1. Check if payroll already exists
                if Payroll.objects.filter(employee=emp, month=month_start).exists():
                    continue

                # 2. Calculate Components
                base = emp.base_salary
                commission = emp.wallet_balance # Commission Paid Out
                
                deductions = 0 
                # Simple logic: Deduct 100 per late arrival in this month
                late_count = Attendance.objects.filter(
                    employee=emp, 
                    date__year=month_start.year, 
                    date__month=month_start.month,
                    is_late=True
                ).count()
                deductions = late_count * 100

                # Ensure total is not negative
                total = max(0, base + commission - deductions)

                # 3. Create Payroll Record
                Payroll.objects.create(
                    employee=emp,
                    month=month_start,
                    base_salary=base,
                    commission_earned=commission,
                    deductions=deductions,
                    total_salary=total,
                    status='PENDING'
                )
                
                # 4. Reset Wallet (Commission Paid Out)
                emp.wallet_balance = 0
                emp.save()
                
                generated_count += 1

        return Response({
            "status": "success", 
            "message": f"Generated payroll for {generated_count} employees for {month_start.strftime('%B %Y')}"
        })

class GoogleLoginApi(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = GoogleLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        token = serializer.validated_data['id_token']
        try:
            print(f"DEBUG: Received Google Token: {token[:20]}...")
            
            # Verify Token
            # Verify Token
            id_info = id_token.verify_oauth2_token(
                token, 
                google_requests.Request(), 
                settings.GOOGLE_CLIENT_ID,
                clock_skew_in_seconds=10
            )


            email = id_info['email']
            print(f"DEBUG: Email from token: {email}")
            
            try:
                user = User.objects.get(email=email)

            except User.DoesNotExist:

                username = email.split('@')[0]
                if User.objects.filter(username=username).exists():
                    username = f"{username}_{int(datetime.now().timestamp())}"
                


                user = User.objects.create_user(
                    email=email,
                    username=username,
                    role='CUSTOMER',
                    password=get_random_string(length=32)
                )


            refresh = RefreshToken.for_user(user)
            
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
        except ValueError as e:
            print(f"DEBUG: ValueError: {e}")
            return Response({"error": "Invalid Google Token", "details": str(e)}, status=400)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"DEBUG: Exception: {e}")
            return Response({"error": str(e), "trace": traceback.format_exc()}, status=500)
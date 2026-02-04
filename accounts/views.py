from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend # 🔥 For Filtering Attendance
from .models import EmployeeProfile, Attendance
from .serializers import UserSerializer, EmployeeProfileSerializer, AttendanceSerializer, EmployeeCreationSerializer

User = get_user_model()

# --- PERMISSIONS ---

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS: return True
        return request.user.is_authenticated and request.user.role == 'ADMIN'

class IsSelfOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'ADMIN': return True
        return obj == request.user

# --- VIEWSETS ---

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create': 
            return [permissions.AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsSelfOrAdmin()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Retrieves the profile of the currently authenticated user.
        """
        if request.user.is_authenticated:
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        return Response({"error": "Not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = EmployeeProfile.objects.select_related('user').all()
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = EmployeeProfileSerializer 

    # 🔥 ENABLE SEARCH (Name, Email, Job Title)
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__username', 'user__email', 'user__phone_number', 'job_title']

    # Use Custom Serializer only for Creating Employees
    def get_serializer_class(self):
        """
        Selects the serializer based on the action:
        - create: EmployeeCreationSerializer (Handles User + Profile creation)
        - others: EmployeeProfileSerializer (Read/Update Profile only)
        """
        if self.action == 'create':
            return EmployeeCreationSerializer
        return EmployeeProfileSerializer

    # 🔥 CRITICAL FIX: Delete the User when Employee is deleted
    def perform_destroy(self, instance):
        """
        Hard Delete: Deletes the associated User object when the EmployeeProfile is deleted.
        Django's on_delete=CASCADE mechanism handles the profile deletion automatically.
        """
        user = instance.user
        user.delete() # This deletes the User AND the Profile (Cascade)

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all().order_by('-date', '-check_in')
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    # 🔥 ENABLE FILTERING (Get attendance for specific employee)
    # URL Example: /api/v1/accounts/attendance/?employee=5
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['employee']

    @action(detail=False, methods=['post'])
    def punch(self, request):
        """
        Attendance Punch Logic:
        - Logic: First punch of the day -> Check-In.
        - Second punch of the day -> Check-Out.
        """
        user = request.user
        if not hasattr(user, 'employee_profile'):
            return Response({"error": "Only employees can punch attendance"}, status=403)
        
        employee = user.employee_profile
        today = timezone.now().date()
        now_time = timezone.now().time()

        attendance = Attendance.objects.filter(employee=employee, date=today).first()

        if not attendance:
            # Punch In
            Attendance.objects.create(employee=employee, check_in=now_time)
            return Response({"status": "Punched In", "time": now_time})
        else:
            # Punch Out
            if attendance.check_out:
                return Response({"error": "Already punched out for today"}, status=400)
            
            attendance.check_out = now_time
            attendance.save()
            return Response({"status": "Punched Out", "time": now_time})
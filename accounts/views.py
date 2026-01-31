from rest_framework import viewsets, permissions
from django.contrib.auth import get_user_model
from .models import EmployeeProfile
from .serializers import UserSerializer, EmployeeProfileSerializer
from rest_framework.decorators import action  # 👈 Import 1
from rest_framework.response import Response  # 👈 Import 2

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """
    API for creating and managing users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create': 
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    # 👇 ഈ ഭാഗം പുതിയതായി ചേർക്കുക (To fix 404 Error)
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class EmployeeViewSet(viewsets.ModelViewSet):
    """
    API for managing Employees.
    """
    queryset = EmployeeProfile.objects.select_related('user').all()
    serializer_class = EmployeeProfileSerializer
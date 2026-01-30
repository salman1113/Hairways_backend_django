from rest_framework import viewsets, permissions  # permissions നിർബന്ധമാണ്
from django.contrib.auth import get_user_model
from .models import EmployeeProfile
from .serializers import UserSerializer, EmployeeProfileSerializer

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """
    API for creating and managing users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # 🟢 ഇതാണ് പ്രശ്നക്കാരൻ! ഇത് കൃത്യമായി ഉണ്ടെന്ന് ഉറപ്പാക്കുക.
    def get_permissions(self):
        if self.action == 'create': 
            # രജിസ്റ്റർ ചെയ്യാൻ വരുന്നവർക്ക് പാസ്സ് വേണ്ട (AllowAny)
            return [permissions.AllowAny()]
        # ബാക്കി കാര്യങ്ങൾക്ക് ലോഗിൻ വേണം
        return [permissions.IsAuthenticated()]

class EmployeeViewSet(viewsets.ModelViewSet):
    """
    API for managing Employees.
    """
    queryset = EmployeeProfile.objects.select_related('user').all()
    serializer_class = EmployeeProfileSerializer
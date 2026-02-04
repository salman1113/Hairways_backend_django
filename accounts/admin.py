from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, EmployeeProfile
from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    

    list_display = ('email', 'username', 'role', 'is_staff', 'is_active')
    ordering = ('email',)


    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('username', 'phone_number', 'profile_picture', 'face_shape')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'role', 'phone_number', 'password_1', 'password_2'),
        }),
    )

admin.site.register(User, CustomUserAdmin)

@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'expertise', 'is_available', 'commission_rate')
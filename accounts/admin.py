from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, EmployeeProfile, CustomerProfile, Payroll, Attendance
from .forms import CustomUserCreationForm, CustomUserChangeForm

class EmployeeProfileInline(admin.StackedInline):
    model = EmployeeProfile
    can_delete = False
    verbose_name_plural = 'Employee Profile'

class CustomerProfileInline(admin.StackedInline):
    model = CustomerProfile
    can_delete = False
    verbose_name_plural = 'Customer Profile'

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    
    list_display = ('email', 'username', 'role', 'is_staff', 'is_active')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('username', 'phone_number', 'profile_picture')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'role', 'phone_number'),
        }),
    )
    
    inlines = [EmployeeProfileInline, CustomerProfileInline]

admin.site.register(User, CustomUserAdmin)

@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'job_title', 'is_available', 'commission_rate')

@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ('employee', 'month', 'total_salary', 'status')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'check_in', 'check_out', 'is_late')
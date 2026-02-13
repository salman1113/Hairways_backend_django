
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.core.cache import cache
from django.urls import reverse

User = get_user_model()

@pytest.mark.django_db
class TestAuthFlows:
    def setup_method(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.register_verify_url = reverse('register-verify')
        self.login_url = reverse('login')
        self.admin_verify_url = reverse('admin-login-verify')

    def test_customer_registration_flow(self):
        # 1. Register
        payload = {
            "email": "customer@example.com",
            "password": "strongpassword123",
            "username": "customer",
            "phone_number": "1234567890"
        }
        response = self.client.post(self.register_url, payload)
        assert response.status_code == 201
        
        user = User.objects.get(email="customer@example.com")
        assert user.is_active is False
        assert user.is_email_verified is False
        assert user.role == 'CUSTOMER'

        # 2. Verify OTP
        # Fetch OTP from cache
        cache_key = f"reg_otp_{user.id}"
        otp = cache.get(cache_key)
        assert otp is not None

        verify_payload = {
            "email": "customer@example.com",
            "otp": otp
        }
        response = self.client.post(self.register_verify_url, verify_payload)
        assert response.status_code == 200
        assert "access" in response.data
        
        user.refresh_from_db()
        assert user.is_active is True
        assert user.is_email_verified is True

        # 3. Login
        login_payload = {
            "email": "customer@example.com",
            "password": "strongpassword123"
        }
        response = self.client.post(self.login_url, login_payload)
        assert response.status_code == 200
        assert "access" in response.data

    def test_admin_login_flow(self):
        # 1. Create Admin
        admin = User.objects.create_superuser(
            email="admin@example.com",
            username="admin",
            password="adminpassword",
            role='ADMIN',
            is_first_login_done=False
        )

        # 2. Login (First Time)
        login_payload = {
            "email": "admin@example.com",
            "password": "adminpassword"
        }
        response = self.client.post(self.login_url, login_payload)
        assert response.status_code == 200
        assert response.data.get("require_otp") is True

        # 3. Verify OTP
        cache_key = f"admin_otp_{admin.id}"
        otp = cache.get(cache_key)
        assert otp is not None

        verify_payload = {
            "email": "admin@example.com",
            "otp": otp
        }
        response = self.client.post(self.admin_verify_url, verify_payload)
        assert response.status_code == 200
        assert "access" in response.data
        
        admin.refresh_from_db()
        assert admin.is_first_login_done is True

        # 4. Login (Subsequent)
        response = self.client.post(self.login_url, login_payload)
        assert response.status_code == 200
        assert "access" in response.data
        assert "require_otp" not in response.data

    def test_employee_login_flow(self):
        # 1. Create Employee
        employee = User.objects.create_user(
            email="employee@example.com",
            username="employee",
            password="employeepassword",
            role='EMPLOYEE'
        )

        # 2. Login
        login_payload = {
            "email": "employee@example.com",
            "password": "employeepassword"
        }
        response = self.client.post(self.login_url, login_payload)
        assert response.status_code == 200
        assert "access" in response.data

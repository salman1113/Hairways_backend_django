import pytest
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime

User = get_user_model()

@pytest.mark.django_db
class TestAdditionalAuthFlows:
    def setup_method(self):
        self.client = APIClient()
        self.google_login_url = reverse('google-login')
        self.token_refresh_url = reverse('token_refresh')
        self.login_url = reverse('login')
        self.register_url = reverse('register')

    @patch('accounts.views.id_token.verify_oauth2_token')
    def test_google_login_success(self, mock_verify):
        # Mock Google Response
        mock_verify.return_value = {
            'email': 'googleuser@example.com',
            'iss': 'accounts.google.com'
        }

        payload = {'id_token': 'fake_valid_token'}
        response = self.client.post(self.google_login_url, payload)

        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data
        
        # Verify user created
        user = User.objects.get(email='googleuser@example.com')
        assert user.role == 'CUSTOMER'

    @patch('accounts.views.id_token.verify_oauth2_token')
    def test_google_login_invalid_token(self, mock_verify):
        mock_verify.side_effect = ValueError("Invalid token")

        payload = {'id_token': 'invalid_token'}
        response = self.client.post(self.google_login_url, payload)

        assert response.status_code == 400
        assert 'error' in response.data

    def test_token_refresh_success(self):
        user = User.objects.create_user(
            email="refresh@example.com", 
            password="password",
            role='CUSTOMER',
            is_email_verified=True
        )
        refresh = RefreshToken.for_user(user)
        
        payload = {'refresh': str(refresh)}
        response = self.client.post(self.token_refresh_url, payload)
        
        assert response.status_code == 200
        assert 'access' in response.data

    def test_token_refresh_user_does_not_exist(self):
        # 1. Create User
        user = User.objects.create_user(
            email="todelete@example.com", 
            password="password",
            role='CUSTOMER'
        )
        # 2. Get Refresh Token
        refresh = RefreshToken.for_user(user)
        refresh_token_str = str(refresh)
        
        # 3. Delete User
        user.delete()
        
        # 4. Try Refresh (Should fail gracefully with 401, NOT 500)
        payload = {'refresh': refresh_token_str}
        response = self.client.post(self.token_refresh_url, payload)
        
        assert response.status_code == 401
        assert 'detail' in response.data or 'error' in response.data

    def test_customer_unverified_login(self):
        # Create unverified user
        user = User.objects.create_user(
            email="unverified@example.com", 
            password="password",
            role='CUSTOMER',
            is_email_verified=False
        )
        
        payload = {
            "email": "unverified@example.com",
            "password": "password"
        }
        response = self.client.post(self.login_url, payload)
        
        assert response.status_code == 403
        assert response.data['error'] == "Email not verified"

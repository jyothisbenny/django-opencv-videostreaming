from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserAPITestCase(APITestCase):
    def setUp(self):
        self.register_url = reverse('user-register')
        self.login_url = reverse('user-login')
        self.user_data = {'email': 'test@jyothis.com', 'password': 'testpassword'}

    def test_register_user(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login_user(self):
        # Register a user
        self.client.post(self.register_url, self.user_data, format='json')
        # Login
        response = self.client.post(self.login_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)

    def test_login_invalid_credentials(self):
        # Try with invalid credentials
        invalid_data = {'email': 'test@example.com', 'password': 'wrongpassword'}
        response = self.client.post(self.login_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

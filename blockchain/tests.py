from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from authentication.models import User


class BlockchainAPITestCase(APITestCase):
    """Test cases for Blockchain API endpoints"""
    
    def setUp(self):
        """Set up test user"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_network_info_requires_authentication(self):
        """Test that network info endpoint requires authentication"""
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse('blockchain:network-info'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_audit_logs_requires_authentication(self):
        """Test that audit logs endpoint requires authentication"""
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse('blockchain:audit-logs'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

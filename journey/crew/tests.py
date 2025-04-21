from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Crew, CrewMembership, CrewMembershipRole, CrewMembershipStatus
from user_manager.models import User
from django.urls import reverse

class CrewModelTests(TestCase):
    def setUp(self):
        # Create a test user
        self.test_user = User.objects.create_user(
            email="test@example.com",
            username="TestUser",
            password="testpassword123"
        )
        
        # Create a test crew
        self.test_crew = Crew.objects.create(
            crew_name="Test Crew",
            crew_description="This is a test crew"
        )
    
    def test_crew_creation(self):
        # Test that crew is saved to database
        self.assertEqual(Crew.objects.count(), 1)
        saved_crew = Crew.objects.first()
        self.assertEqual(saved_crew.crew_name, "Test Crew")
        self.assertEqual(saved_crew.crew_description, "This is a test crew")
        self.assertEqual(saved_crew.member_count, 0)
    
    def test_crew_membership(self):
        # Test creating a crew membership
        membership = CrewMembership.objects.create(
            user=self.test_user,
            crew=self.test_crew,
            role=CrewMembershipRole.CREATOR,
            status=CrewMembershipStatus.ACCEPTED
        )
        
        self.assertEqual(CrewMembership.objects.count(), 1)
        saved_membership = CrewMembership.objects.first()
        self.assertEqual(saved_membership.user, self.test_user)
        self.assertEqual(saved_membership.crew, self.test_crew)
        self.assertEqual(saved_membership.role, CrewMembershipRole.CREATOR)

class CrewAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create a test user
        self.test_user = User.objects.create_user(
            email="test@example.com",
            username="TestUser",
            password="testpassword123"
        )
        
        # Get JWT token
        response = self.client.post(
            '/api/token/',
            {'email': 'test@example.com', 'password': 'testpassword123'},
            format='json'
        )
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        # Create a test crew
        self.test_crew = Crew.objects.create(
            crew_name="Test Crew",
            crew_description="This is a test crew"
        )
    
    def test_create_crew(self):
        url = reverse('crew-list')
        data = {
            'crew_name': 'New Test Crew',
            'crew_description': 'This is a new test crew'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Crew.objects.count(), 2)
        new_crew = Crew.objects.get(crew_name='New Test Crew')
        self.assertEqual(new_crew.crew_description, 'This is a new test crew')
    
    def test_join_crew(self):
        url = reverse('crew-join-crew', kwargs={'pk': self.test_crew.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CrewMembership.objects.count(), 1)
        membership = CrewMembership.objects.first()
        self.assertEqual(membership.user, self.test_user)
        self.assertEqual(membership.crew, self.test_crew)
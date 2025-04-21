from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Plan, Template, Challenge, Retrospect
from .models import TemplateOwnerType, ChallengeOwnerType, RetrospectOwnerType, ChallengeStatus
from user_manager.models import User
from crew.models import Crew
from django.urls import reverse
import json
from datetime import datetime, timedelta

class RetrospectModelTests(TestCase):
    def setUp(self):
        # Create test user
        self.test_user = User.objects.create_user(
            email="test@example.com",
            username="TestUser",
            password="testpassword123"
        )
        
        # Create test crew
        self.test_crew = Crew.objects.create(
            crew_name="Test Crew",
            crew_description="This is a test crew"
        )
        
        # Create test plan
        self.test_plan = Plan.objects.create(
            plan_list=json.dumps(["Step 1", "Step 2", "Step 3"])
        )
        
        # Create test template
        self.test_template = Template.objects.create(
            user=self.test_user,
            owner_type=TemplateOwnerType.USER,
            name="Test Template",
            steps=json.dumps(["What went well?", "What could be improved?", "Action items"])
        )
        
        # Create test challenge
        self.test_challenge = Challenge.objects.create(
            plan=self.test_plan,
            user=self.test_user,
            challenge_name="Test Challenge",
            deadline=datetime.now() + timedelta(days=7),
            kpi_description="Test KPI description",
            owner_type=ChallengeOwnerType.USER
        )
    
    def test_retrospect_creation(self):
        # Test creating a retrospect
        retrospect = Retrospect.objects.create(
            challenge=self.test_challenge,
            template=self.test_template,
            user=self.test_user,
            content="Test retrospect content",
            kpi_result=85.5,
            owner_type=RetrospectOwnerType.USER
        )
        
        self.assertEqual(Retrospect.objects.count(), 1)
        saved_retrospect = Retrospect.objects.first()
        self.assertEqual(saved_retrospect.challenge, self.test_challenge)
        self.assertEqual(saved_retrospect.template, self.test_template)
        self.assertEqual(saved_retrospect.content, "Test retrospect content")
        self.assertEqual(saved_retrospect.kpi_result, 85.5)

class RetrospectAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create test user
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
        
        # Create test plan
        self.test_plan = Plan.objects.create(
            plan_list=json.dumps(["Step 1", "Step 2", "Step 3"])
        )
        
        # Create test template
        self.test_template = Template.objects.create(
            user=self.test_user,
            owner_type=TemplateOwnerType.USER,
            name="Test Template",
            steps=json.dumps(["What went well?", "What could be improved?", "Action items"])
        )
    
    def test_create_challenge(self):
        url = reverse('challenge-list')
        data = {
            'plan': self.test_plan.id,
            'challenge_name': 'API Test Challenge',
            'deadline': (datetime.now() + timedelta(days=7)).isoformat(),
            'kpi_description': 'API Test KPI description',
            'owner_type': ChallengeOwnerType.USER,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Challenge.objects.count(), 1)
        challenge = Challenge.objects.first()
        self.assertEqual(challenge.challenge_name, 'API Test Challenge')
        self.assertEqual(challenge.user, self.test_user)
    
    def test_create_retrospect(self):
        # First create a challenge
        challenge = Challenge.objects.create(
            plan=self.test_plan,
            user=self.test_user,
            challenge_name="Test Challenge",
            deadline=datetime.now() + timedelta(days=7),
            kpi_description="Test KPI description",
            owner_type=ChallengeOwnerType.USER
        )
        
        url = reverse('retrospect-list')
        data = {
            'challenge': challenge.id,
            'template': self.test_template.id,
            'content': 'API Test retrospect content',
            'kpi_result': 90.5,
            'visibility': 'PRIVATE',
            'owner_type': RetrospectOwnerType.USER,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Retrospect.objects.count(), 1)
        retrospect = Retrospect.objects.first()
        self.assertEqual(retrospect.content, 'API Test retrospect content')
        self.assertEqual(retrospect.user, self.test_user)
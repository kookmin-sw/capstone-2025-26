from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
from .models import Crew, CrewMembership, CrewMembershipRole, CrewMembershipStatus
from .serializers import CrewSerializer, CrewMembershipSerializer

User = get_user_model()

class CrewModelTest(TestCase):
    def setUp(self):
        self.crew = Crew.objects.create(
            crew_name='TestCrew',
            crew_description='Desc',
            crew_image='http://example.com/img.png'
        )

    def test_str_representation(self):
        self.assertEqual(str(self.crew), 'TestCrew')

    def test_default_member_count(self):
        self.assertEqual(self.crew.member_count, 0)

class CrewMembershipModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='memberuser', password='pass')
        self.crew = Crew.objects.create(
            crew_name='Crew2',
            crew_description='',
            crew_image=''
        )
        self.membership = CrewMembership.objects.create(user=self.user, crew=self.crew)

    def test_str_representation(self):
        expected = f"{self.user} - {self.crew} ({self.membership.get_status_display()})"
        self.assertEqual(str(self.membership), expected)

    def test_default_values(self):
        self.assertEqual(self.membership.role, CrewMembershipRole.PARTICIPANT)
        self.assertEqual(self.membership.status, CrewMembershipStatus.PENDING)

    def test_unique_together_constraint(self):
        with self.assertRaises(Exception):
            CrewMembership.objects.create(user=self.user, crew=self.crew)

class CrewSerializerTest(TestCase):
    def setUp(self):
        self.crew = Crew.objects.create(
            crew_name='SerializerCrew',
            crew_description='Desc',
            crew_image='http://img'
        )

    def test_serialization_fields(self):
        serializer = CrewSerializer(self.crew)
        data = serializer.data
        self.assertEqual(data['id'], self.crew.id)
        self.assertEqual(data['crew_name'], self.crew.crew_name)
        self.assertEqual(data['crew_description'], self.crew.crew_description)
        self.assertEqual(data['member_count'], self.crew.member_count)
        self.assertEqual(data['crew_image'], self.crew.crew_image)

    def test_deserialization(self):
        payload = {
            'crew_name': 'NewCrew',
            'crew_description': 'NewDesc',
            'crew_image': 'http://new'
        }
        serializer = CrewSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        self.assertEqual(instance.crew_name, 'NewCrew')
        self.assertEqual(instance.crew_description, 'NewDesc')
        self.assertEqual(instance.crew_image, 'http://new')
        self.assertEqual(instance.member_count, 0)

class CrewMembershipSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='seruser', password='pass')
        self.crew = Crew.objects.create(
            crew_name='Crew3',
            crew_description='',
            crew_image=''
        )
        self.membership = CrewMembership.objects.create(user=self.user, crew=self.crew)

    def test_serialization_fields(self):
        serializer = CrewMembershipSerializer(self.membership)
        data = serializer.data
        self.assertEqual(data['id'], self.membership.id)
        self.assertEqual(data['user']['id'], self.user.id)
        self.assertEqual(data['crew'], self.crew.id)
        self.assertEqual(data['role'], self.membership.role)
        self.assertEqual(data['status'], self.membership.status)
        self.assertIn('joined_at', data)

class CrewViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='creator', password='pass')
        self.user2 = User.objects.create_user(username='member', password='pass')
        self.client.force_authenticate(user=self.user1)
        # create crew
        payload = {
            'crew_name': 'CrewTest',
            'crew_description': 'TestDesc',
            'crew_image': 'http://img'
        }
        response = self.client.post(reverse('crew-list'), payload)
        self.assertEqual(response.status_code, 201)
        self.crew = Crew.objects.get(crew_name='CrewTest')

    def test_list_crews(self):
        response = self.client.get(reverse('crew-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_join_creates_membership_and_counts(self):
        url = reverse('crew-join', args=[self.crew.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 201)
        self.crew.refresh_from_db()
        self.assertEqual(self.crew.member_count, 1)
        membership = CrewMembership.objects.get(user=self.user1, crew=self.crew)
        self.assertEqual(membership.role, CrewMembershipRole.CREATOR)
        self.assertEqual(membership.status, CrewMembershipStatus.ACCEPTED)

    def test_my_crews_endpoint(self):
        self.client.post(reverse('crew-join', args=[self.crew.pk]))
        response = self.client.get(reverse('crew-my-crews'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.crew.id)

    def test_request_join_and_leave(self):
        self.client.force_authenticate(user=self.user2)
        # request join
        resp = self.client.post(reverse('crew-request-join', args=[self.crew.pk]))
        self.assertEqual(resp.status_code, 201)
        membership = CrewMembership.objects.get(user=self.user2, crew=self.crew)
        self.assertEqual(membership.status, CrewMembershipStatus.PENDING)
        self.assertEqual(membership.role, CrewMembershipRole.PARTICIPANT)
        # leave
        resp = self.client.delete(reverse('crew-leave', args=[self.crew.pk]))
        self.assertEqual(resp.status_code, 204)
        self.assertFalse(CrewMembership.objects.filter(user=self.user2, crew=self.crew).exists())

    def test_list_members(self):
        # creator joins
        self.client.post(reverse('crew-join', args=[self.crew.pk]))
        # add accepted member manually
        CrewMembership.objects.create(
            user=self.user2,
            crew=self.crew,
            role=CrewMembershipRole.PARTICIPANT,
            status=CrewMembershipStatus.ACCEPTED
        )
        resp = self.client.get(reverse('crew-members', args=[self.crew.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 2)

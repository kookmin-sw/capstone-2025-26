from django.test import TestCase, Client
from django.urls import reverse
from django.db import IntegrityError, transaction
from django.db.utils import DataError
from rest_framework.test import APIClient
from rest_framework import status
from .models import User, Provider, Notification, NotificationType
from django.contrib.contenttypes.models import ContentType

class UserManagerModelTests(TestCase):
    def setUp(self):
        # Create a provider
        self.client = APIClient()
        self.provider = Provider.objects.create(domain="example.com", name="Example Provider")
        
        # Create a test user
        self.test_user = User.objects.create_user(
            email="test@example.com",
            username="TestUser",
            password="testpassword123"
        )
        self.test_user.provider = self.provider
        self.test_user.save()

        # # 로그인 및 토큰 획득
        # response = self.client.post(
        #     reverse('token_obtain_pair'),
        #     {'email': 'test1@example.com', 'password': 'test1password'},
        #     format='json'
        # )
        # self.token = response.data['access']
        
        # # 인증 설정
        # self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        # # 인증 설정이 제대로 되었는지 확인
        # print(f"Authentication token: {self.token}")
        # print(f"Client credentials: {self.client.credentials}")
    
    def test_user_creation(self):
        # Test that we can create a user and it's saved to the database
        self.assertEqual(User.objects.count(), 1)
        saved_user = User.objects.get(email="test@example.com")
        self.assertEqual(saved_user.username, "TestUser")
        self.assertEqual(saved_user.provider, self.provider)
    
    def test_notification_creation(self):
        # Test notification creation
        notification = Notification.objects.create(
            user=self.test_user,
            type=NotificationType.ETC,
            content="Test notification content"
        )
        self.assertEqual(Notification.objects.count(), 1)
        saved_notification = Notification.objects.first()
        self.assertEqual(saved_notification.content, "Test notification content")
        self.assertEqual(saved_notification.user, self.test_user)
        self.assertEqual(saved_notification.is_read, False)
        
    def test_user_uid_generation(self):
        """Test that a UID is automatically generated for a new user"""
        # 1. CREATE: 새로운 사용자 생성
        new_user = User.objects.create_user(
            email="uid_test@example.com",
            username="UidTestUser",
            password="testpassword123"
        )
        
        # 2. READ: 데이터베이스에서 사용자 정보 조회
        created_user = User.objects.get(email="uid_test@example.com")
        
        # 3. ASSERT: 사용자의 uid가 자동으로 생성되었는지 확인
        self.assertIsNotNone(created_user.uid)
        self.assertEqual(len(created_user.uid), 4)  # 4자리 uid 체크
        self.assertTrue(created_user.uid.isdigit())  # uid가 숫자로만 구성되었는지 체크
    
    def test_duplicate_email_prevention(self):
        """Test that users with duplicate emails cannot be created"""
        # 1. SETUP: 이미 존재하는 이메일 설정
        email = "test@example.com"
        
        # 2. EXECUTE & VERIFY: 중복 이메일로 사용자 생성 시 예외 발생 확인
        with self.assertRaises(IntegrityError):
        # savepoint 생성 → 예외 시 블록 롤백
            with transaction.atomic():
                User.objects.create(
                email=email,
                username="Another User",
                password="password456"
            )
                
        # 3. READ & ASSERT: 사용자 수가 1명으로 유지되는지 확인
        # 트랜잭션이 롤백되었으므로 사용자 수는 여전히 1명이어야 함
        self.assertEqual(User.objects.count(), 1)
    
    def test_user_update(self):
        """Test updating user information"""
        # 1. SETUP: 업데이트할 사용자 데이터 준비
        self.test_user.username = "UpdatedUsername"
        self.test_user.profile_image = "https://example.com/image.jpg"
        
        # 2. EXECUTE: 변경사항 저장
        self.test_user.save()
        
        # 3. READ: 데이터베이스에서 최신 사용자 정보 조회
        updated_user = User.objects.get(id=self.test_user.id)
        
        # 4. ASSERT: 변경사항이 제대로 저장되었는지 확인
        self.assertEqual(updated_user.username, "UpdatedUsername")
        self.assertEqual(updated_user.profile_image, "https://example.com/image.jpg")

class UserManagerAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.provider = Provider.objects.create(domain="example.com", name="Example Provider")
        
        # Create a test user
        self.test_user = User.objects.create_user(
            email="test@example.com",
            username="TestUser",
            password="testpassword123"
        )
        
        # Get JWT token for authentication
        response = self.client.post(
            '/api/token/',
            {'email': 'test@example.com', 'password': 'testpassword123'},
            format='json'
        )
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_get_user_profile(self):
        # Test retrieving user profile via API
        url = reverse('user-detail', kwargs={'pk': self.test_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['username'], 'TestUser')
        
    def test_user_registration(self):
        """Test user registration API"""
        # 1. SETUP: 등록에 필요한 사용자 데이터 준비
        self.client.credentials()  # 인증 헤더 제거
        url = reverse('user-register')
        data = {
            'email': 'new_user@example.com',
            'username': 'NewUser',
            'password': 'newpassword123'
        }
        
        # 2. EXECUTE: 회원가입 API 호출
        response = self.client.post(url, data, format='json')
        
        # 3. ASSERT: 응답 검증
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        
        # 4. READ: 데이터베이스에서 새 사용자 확인
        self.assertTrue(User.objects.filter(email='new_user@example.com').exists())
        new_user = User.objects.get(email='new_user@example.com')
        
        # 5. VERIFY: 사용자 정보 검증
        self.assertEqual(new_user.username, 'NewUser')
        self.assertTrue(new_user.is_active)
    
    def test_create_notification(self):
        """Test creating notifications for a user via API"""
        # 1. SETUP: 알림 생성 데이터 준비
        url = '/api/users/notifications/'  # 직접 URL 지정
        data = {
            'user': self.test_user.id,  # Include user ID explicitly
            'type': NotificationType.ETC,
            'content': 'API test notification'
        }
        
          # 요청 전에 인증 토큰 확인
        print(f"Authentication header: {self.client.credentials}")

        # 2. EXECUTE: 알림 생성 API 호출
        response = self.client.post(url, data, format='json')
        
        # 응답 내용 출력
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.content}")
        # 3. ASSERT: 응답 검증
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 4. READ: 데이터베이스에서 알림 조회
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        
        # 5. VERIFY: 알림 정보 검증
        self.assertEqual(notification.content, 'API test notification')
        self.assertEqual(notification.user, self.test_user)
        self.assertFalse(notification.is_read)
    
    def test_mark_notification_as_read(self):
        """Test marking a notification as read"""
        # 1. CREATE: 테스트용 알림 생성
        notification = Notification.objects.create(
            user=self.test_user,
            type=NotificationType.ETC,
            content="Test notification to mark as read"
        )
        
        # 2. EXECUTE: 알림 읽음 처리 API 호출
        url = reverse('notification-mark-as-read', kwargs={'pk': notification.id})
        response = self.client.patch(url)
        
        # 3. ASSERT: 응답 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 4. READ: 데이터베이스에서 최신 알림 상태 조회
        updated_notification = Notification.objects.get(id=notification.id)
        
        # 5. VERIFY: 알림이 읽음 상태로 변경되었는지 확인
        self.assertTrue(updated_notification.is_read)
    
    def test_delete_user(self):
        """Test deleting a user account via API"""
        # 1. SETUP: 삭제할 새로운 테스트 사용자 생성
        test_user_to_delete = User.objects.create_user(
            email="delete_me@example.com",
            username="DeleteMe",
            password="password123"
        )
        
        # 2. EXECUTE: 사용자 삭제 API 호출
        url = reverse('user-delete-account')
        response = self.client.delete(url)
        
        # 3. ASSERT: 응답 검증
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # 4. VERIFY: 사용자가 실제로 삭제되었는지 확인
        self.assertFalse(User.objects.filter(id=self.test_user.id).exists())

    def test_delete_notification(self):
        """Test deleting a notification"""
        # 1. CREATE: 테스트용 알림 생성
        notification = Notification.objects.create(
            user=self.test_user,
            type=NotificationType.ETC,
            content="Test notification to delete"
        )
        
        # 2. EXECUTE: 알림 삭제 API 호출
        url = reverse('notification-detail', kwargs={'pk': notification.id})
        response = self.client.delete(url)
        
        # 3. ASSERT: 응답 검증
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # 4. VERIFY: 알림이 실제로 삭제되었는지 확인
        self.assertFalse(Notification.objects.filter(id=notification.id).exists())

    def test_delete_other_users_notification_permission(self):
        """Test that a user cannot delete another user's notification"""
        # 1. SETUP: 다른 사용자와 그 사용자의 알림 생성
        other_user = User.objects.create_user(
            email="other@example.com",
            username="OtherUser",
            password="password456"
        )
        other_notification = Notification.objects.create(
            user=other_user,
            type=NotificationType.ETC,
            content="Other user's notification"
        )
        
        # 2. EXECUTE: 다른 사용자의 알림 삭제 시도
        url = reverse('notification-detail', kwargs={'pk': other_notification.id})
        response = self.client.delete(url)
        
        # 3. ASSERT: 권한 오류 응답 확인
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)  # 또는 403 FORBIDDEN
        
        # 4. VERIFY: 알림이 삭제되지 않았는지 확인
        self.assertTrue(Notification.objects.filter(id=other_notification.id).exists())

    def test_user_deletion_cascades_to_notifications(self):
        """Test that when a user is deleted, their notifications are also deleted"""
        # 1. SETUP: 사용자용 알림 생성
        notification = Notification.objects.create(
            user=self.test_user,
            type=NotificationType.ETC,
            content="Notification that should be deleted with user"
        )
        user_id = self.test_user.id
        notification_id = notification.id
        
        # 2. EXECUTE: 사용자 삭제
        self.test_user.delete()
        
        # 3. VERIFY: 사용자와 함께 알림도 삭제되었는지 확인
        self.assertFalse(User.objects.filter(id=user_id).exists())
        self.assertFalse(Notification.objects.filter(id=notification_id).exists())
   
    def test_provider_deletion(self):
        """Test deleting a provider and checking related user updates"""
        # 1. SETUP: Provider를 사용하는 사용자 생성
        provider_to_delete = Provider.objects.create(domain="delete.com", name="DeleteMe")
        user_with_provider = User.objects.create_user(
            email="user_with_provider@delete.com",
            username="ProviderUser",
            password="password123"
        )
        user_with_provider.provider = provider_to_delete
        user_with_provider.save()
        
        # 2. EXECUTE: Provider 삭제
        provider_to_delete.delete()
        
        # 3. READ: 사용자 재조회
        updated_user = User.objects.get(id=user_with_provider.id)
        
        # 4. VERIFY: Provider가 삭제된 후 사용자의 provider 필드가 null이 되었는지 확인 (SET_NULL)
        self.assertIsNone(updated_user.provider)
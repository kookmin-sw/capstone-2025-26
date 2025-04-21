from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Feed, Comment, Like
from user_manager.models import User
from django.urls import reverse

class CommunityModelTests(TestCase):
    def setUp(self):
        # Create test user
        self.test_user = User.objects.create_user(
            email="test@example.com",
            username="TestUser",
            password="testpassword123"
        )
    
    def test_feed_creation(self):
        # Test creating a feed
        feed = Feed.objects.create(
            user=self.test_user,
            content="Test feed content"
        )
        
        self.assertEqual(Feed.objects.count(), 1)
        saved_feed = Feed.objects.first()
        self.assertEqual(saved_feed.content, "Test feed content")
        self.assertEqual(saved_feed.user, self.test_user)
        self.assertEqual(saved_feed.view_count, 0)
    
    def test_comment_creation(self):
        # Create a feed first
        feed = Feed.objects.create(
            user=self.test_user,
            content="Test feed content"
        )
        
        # Test creating a comment
        comment = Comment.objects.create(
            feed=feed,
            user=self.test_user,
            content="Test comment content"
        )
        
        self.assertEqual(Comment.objects.count(), 1)
        saved_comment = Comment.objects.first()
        self.assertEqual(saved_comment.content, "Test comment content")
        self.assertEqual(saved_comment.feed, feed)
    
    def test_like_creation(self):
        # Create a feed first
        feed = Feed.objects.create(
            user=self.test_user,
            content="Test feed content"
        )
        
        # Test creating a like
        like = Like.objects.create(
            feed=feed,
            user=self.test_user
        )
        
        self.assertEqual(Like.objects.count(), 1)
        saved_like = Like.objects.first()
        self.assertEqual(saved_like.feed, feed)
        self.assertEqual(saved_like.user, self.test_user)

class CommunityAPITests(TestCase):
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
    
    def test_create_feed(self):
        url = reverse('feed-list')
        data = {
            'content': 'API Test feed content'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Feed.objects.count(), 1)
        feed = Feed.objects.first()
        self.assertEqual(feed.content, 'API Test feed content')
        self.assertEqual(feed.user, self.test_user)
    
    def test_create_comment(self):
        # First create a feed
        feed = Feed.objects.create(
            user=self.test_user,
            content="Test feed content"
        )
        
        url = reverse('feed-comments', kwargs={'pk': feed.id})
        data = {
            'content': 'API Test comment content'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.first()
        self.assertEqual(comment.content, 'API Test comment content')
        self.assertEqual(comment.user, self.test_user)
    
    def test_like_feed(self):
        # First create a feed
        feed = Feed.objects.create(
            user=self.test_user,
            content="Test feed content"
        )
        
        url = reverse('feed-like', kwargs={'pk': feed.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.count(), 1)
        like = Like.objects.first()
        self.assertEqual(like.feed, feed)
        self.assertEqual(like.user, self.test_user)
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Feed, Comment, Like
from .serializers import FeedSerializer, CommentSerializer, LikeSerializer

User = get_user_model()

class FeedModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.feed = Feed.objects.create(user=self.user, content='Test content', title='Test title')

    def test_str_representation(self):
        expected = f"Feed {self.feed.id} by {self.user}"
        self.assertEqual(str(self.feed), expected)

    def test_default_view_count(self):
        self.assertEqual(self.feed.view_count, 0)

    def test_likes_count_property(self):
        Like.objects.create(feed=self.feed, user=self.user)
        self.assertEqual(self.feed.likes.count(), 1)

class CommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='commentuser', password='testpass')
        self.feed = Feed.objects.create(user=self.user, content='Content', title='Title')
        self.comment = Comment.objects.create(feed=self.feed, user=self.user, content='Comment text')

    def test_str_representation(self):
        expected = f"Comment by {self.user} on {self.feed}"
        self.assertEqual(str(self.comment), expected)

class LikeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='likeuser', password='testpass')
        self.feed = Feed.objects.create(user=self.user, content='Like content', title='Like title')
        self.like = Like.objects.create(feed=self.feed, user=self.user)

    def test_str_representation(self):
        expected = f"{self.user} likes {self.feed}"
        self.assertEqual(str(self.like), expected)

    def test_unique_together_constraint(self):
        with self.assertRaises(Exception):
            Like.objects.create(feed=self.feed, user=self.user)

class FeedSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='serializeruser', password='testpass')
        self.feed = Feed.objects.create(user=self.user, content='Serialize content', title='Serialize title')
        # Add two likes
        Like.objects.create(feed=self.feed, user=self.user)
        self.user2 = User.objects.create_user(username='serializeruser2', password='testpass')
        Like.objects.create(feed=self.feed, user=self.user2)

    def test_feed_serialization_fields(self):
        serializer = FeedSerializer(self.feed)
        data = serializer.data
        self.assertEqual(data['id'], self.feed.id)
        self.assertEqual(data['user']['id'], self.user.id)
        self.assertEqual(data['content'], self.feed.content)
        self.assertEqual(data['view_count'], self.feed.view_count)
        self.assertEqual(data['likes_count'], 2)
        self.assertIn('created_at', data)

    def test_feed_deserialization(self):
        payload = {'content': 'New content'}
        serializer = FeedSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save(user=self.user)
        self.assertEqual(instance.content, 'New content')
        self.assertEqual(instance.user, self.user)

class CommentSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='commentserializer', password='testpass')
        self.feed = Feed.objects.create(user=self.user, content='Feed content', title='Feed title')
        self.comment = Comment.objects.create(feed=self.feed, user=self.user, content='Some comment')

    def test_comment_serialization_fields(self):
        serializer = CommentSerializer(self.comment)
        data = serializer.data
        self.assertEqual(data['id'], self.comment.id)
        self.assertEqual(data['feed'], self.feed.id)
        self.assertEqual(data['user']['id'], self.user.id)
        self.assertEqual(data['content'], self.comment.content)
        self.assertIn('created_at', data)

    def test_comment_deserialization(self):
        payload = {'feed': self.feed.id, 'content': 'Another comment'}
        serializer = CommentSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save(user=self.user)
        self.assertEqual(instance.content, 'Another comment')
        self.assertEqual(instance.feed, self.feed)
        self.assertEqual(instance.user, self.user)

class LikeSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='likeserializer', password='testpass')
        self.feed = Feed.objects.create(user=self.user, content='Like feed', title='Like title')
        self.like = Like.objects.create(feed=self.feed, user=self.user)

    def test_like_serialization_fields(self):
        serializer = LikeSerializer(self.like)
        data = serializer.data
        self.assertEqual(data['id'], self.like.id)
        self.assertEqual(data['feed'], self.feed.id)
        self.assertEqual(data['user']['id'], self.user.id)
        self.assertIn('created_at', data)

    def test_like_deserialization_invalid(self):
        payload = {'feed': self.feed.id}
        serializer = LikeSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn('feed', serializer.errors)

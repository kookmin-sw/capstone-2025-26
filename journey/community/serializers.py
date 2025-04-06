from rest_framework import serializers
from .models import Feed, Comment, Like
from user_manager.serializer import UserSerializer

class FeedSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Feed
        fields = ['id', 'user', 'content', 'view_count', 'likes_count', 'created_at']
        read_only_fields = ['id', 'user', 'view_count', 'created_at']

    def get_likes_count(self, obj):
        return obj.likes.count()

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    feed = serializers.PrimaryKeyRelatedField(queryset=Feed.objects.all())

    class Meta:
        model = Comment
        fields = ['id', 'feed', 'user', 'content', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    feed = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'feed', 'user', 'created_at']
        read_only_fields = ['id', 'feed', 'user', 'created_at']

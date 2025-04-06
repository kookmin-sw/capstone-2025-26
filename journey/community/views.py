from django.shortcuts import render, get_object_or_404
from django.db.models import F
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Feed, Comment, Like
from .serializers import FeedSerializer, CommentSerializer, LikeSerializer
from .permissions import IsOwnerOrReadOnly

class FeedViewSet(viewsets.ModelViewSet):
    queryset = Feed.objects.all()
    serializer_class = FeedSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.view_count = F('view_count') + 1
        instance.save(update_fields=['view_count'])
        instance.refresh_from_db()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_create(self, serializer):
        # Automatically set the user to the logged-in user upon creation
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        feed = self.get_object()
        user = request.user
        
        try:
            # Check if the user already liked this feed
            like = Like.objects.get(feed=feed, user=user)
            # If like exists, delete it (unlike)
            like.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Like.DoesNotExist:
            # If like does not exist, create it (like)
            Like.objects.create(feed=feed, user=user)
            # Optionally return the created like data or just success
            # serializer = LikeSerializer(like_instance) # If you need to return data
            return Response({'status': 'liked'}, status=status.HTTP_201_CREATED)

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        queryset = Comment.objects.all()
        # Filter comments based on the 'feed' query parameter
        feed_id = self.request.query_params.get('feed', None)
        if feed_id is not None:
            queryset = queryset.filter(feed__id=feed_id)
        return queryset

    def perform_create(self, serializer):
        # Automatically set the user upon creation
        # Feed is now handled by the serializer based on request data
        serializer.save(user=self.request.user)
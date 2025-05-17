from django.shortcuts import render, get_object_or_404
from django.db.models import F
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Feed, Comment, Like
from .serializers import FeedSerializer, CommentSerializer, LikeSerializer
from .permissions import IsOwnerOrReadOnly

class FeedViewSet(viewsets.ModelViewSet):
    """
    피드 모델에 대한 CRUD 및 좋아요 토글 API를 제공합니다.
    """
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
        # 생성 시 요청 사용자를 user 필드에 자동 설정합니다.
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        feed = self.get_object()
        user = request.user
        
        try:
            # 사용자가 이미 좋아요를 눌렀는지 확인합니다.
            like = Like.objects.get(feed=feed, user=user)
            # 좋아요가 이미 있으면 삭제하여 취소 처리합니다.
            like.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Like.DoesNotExist:
            # 좋아요가 없으면 새로 생성합니다.
            Like.objects.create(feed=feed, user=user)
            # Optionally return the created like data or just success
            # serializer = LikeSerializer(like_instance) # If you need to return data
            return Response({'status': 'liked'}, status=status.HTTP_201_CREATED)

class CommentViewSet(viewsets.ModelViewSet):
    """
    댓글 모델에 대한 CRUD API를 제공합니다.
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        queryset = Comment.objects.all()
        # 'feed' 쿼리 파라미터로 댓글을 필터링합니다.
        feed_id = self.request.query_params.get('feed', None)
        if feed_id is not None:
            queryset = queryset.filter(feed__id=feed_id)
        return queryset

    def perform_create(self, serializer):
        # 생성 시 요청 사용자를 user 필드에 자동 설정합니다.
        serializer.save(user=self.request.user)
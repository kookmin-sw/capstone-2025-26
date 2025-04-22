from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, NotificationViewSet, UserChallengeStatusView

# 명확하게 분리된 라우터 생성
user_router = DefaultRouter()
user_router.register(r'users', UserViewSet, basename='user')

notification_router = DefaultRouter()
notification_router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    # 각 라우터를 독립적으로 포함
    path('', include(user_router.urls)),
    path('', include(notification_router.urls)),
    path('my-challenges/', UserChallengeStatusView.as_view(), name='my-challenges'),
]
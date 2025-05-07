from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, NotificationViewSet, UserChallengeStatusView

# Create a router without the 'users' prefix since it's already included in the main urls.py
user_router = DefaultRouter()
user_router.register(r'', UserViewSet, basename='user')

notification_router = DefaultRouter()
notification_router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    # Include user router at root level
    path('', include(user_router.urls)),
    path('', include(notification_router.urls)),
    path('my-challenges/', UserChallengeStatusView.as_view(), name='my-challenges'),
]
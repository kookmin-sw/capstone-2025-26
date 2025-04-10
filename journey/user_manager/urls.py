from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, NotificationViewSet, UserChallengeStatusView

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
    path('my-challenges/', UserChallengeStatusView.as_view(), name='my-challenges'),
]
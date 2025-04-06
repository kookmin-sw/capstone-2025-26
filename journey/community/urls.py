from django.urls import path, include
from rest_framework.routers import DefaultRouter # Use DefaultRouter again
from .views import FeedViewSet, CommentViewSet # Removed LikeViewSet import earlier

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'feeds', FeedViewSet, basename='feed')
router.register(r'comments', CommentViewSet, basename='comment')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
] 
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CrewViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
# Register with an empty prefix since 'crew/' is handled in the main urls.py
router.register(r'', CrewViewSet, basename='crew')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
] 
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RetrospectViewSet, TemplateViewSet, ChallengeViewSet

router = DefaultRouter()
router.register(r'retrospects', RetrospectViewSet, basename='retrospect')
router.register(r'templates', TemplateViewSet, basename='template')
router.register(r'challenges', ChallengeViewSet, basename='challenge')

urlpatterns = [
    path('', include(router.urls)),
] 
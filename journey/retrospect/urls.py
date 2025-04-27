from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (RetrospectViewSet, TemplateViewSet, ChallengeViewSet, 
                    PlanViewSet, RetrospectWeeklyAnalysisViewSet)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'retrospects', RetrospectViewSet, basename='retrospect')
router.register(r'templates', TemplateViewSet, basename='template')
router.register(r'challenges', ChallengeViewSet, basename='challenge')
router.register(r'retrospect-weekly-analysis', RetrospectWeeklyAnalysisViewSet, basename='retrospect-weekly-analysis')
router.register(r'plans', PlanViewSet, basename='plan') 

urlpatterns = [
    path('', include(router.urls)),
    # GenerateNextPlanAPIView URL 패턴 제거됨
]
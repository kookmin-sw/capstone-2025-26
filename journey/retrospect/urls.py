from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    RetrospectViewSet, TemplateViewSet, ChallengeViewSet, PlanViewSet,
    KpiViewSet, KpiResultViewSet
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'retrospects', RetrospectViewSet, basename='retrospect')
router.register(r'templates', TemplateViewSet, basename='template')
router.register(r'challenges', ChallengeViewSet, basename='challenge')
router.register(r'plans', PlanViewSet, basename='plan') 
router.register(r'kpis', KpiViewSet, basename='kpi')
router.register(r'kpi-results', KpiResultViewSet, basename='kpi-result')

urlpatterns = [
    path('', include(router.urls)),
]
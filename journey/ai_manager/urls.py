# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GenerateKpiFromChallengeAPIView, GeneratePlanFromChallengeAPIView,
    GenerateNextPlanAPIView, TriggerWeeklyAnalysisView,
    ChallengeWeeklyAnalysisView, UserWeeklyAnalysisView
)

# DefaultRouter 사용 (추가 기능 활용)
router = DefaultRouter()

app_name = 'ai_manager'

urlpatterns = [
    path('generate-kpi/', GenerateKpiFromChallengeAPIView.as_view(), name='generate-kpi'),
    path('generate-plan/', GeneratePlanFromChallengeAPIView.as_view(), name='generate-plan'),
    path('generate-tomorrow-plan/', GenerateNextPlanAPIView.as_view(), name='generate-tomorrow-plan'),
    path('trigger-weekly-analysis/', TriggerWeeklyAnalysisView.as_view(), name='trigger_weekly_analysis'),
    
    # 주간회고분석 조회 API
    path('challenge-weekly-analysis/', ChallengeWeeklyAnalysisView.as_view(), name='challenge-weekly-analysis'),
    path('user-weekly-analysis/', UserWeeklyAnalysisView.as_view(), name='user-weekly-analysis'),
]

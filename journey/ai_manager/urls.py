# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LLMViewSet

router = DefaultRouter()
router.register(r'', LLMViewSet, basename='')

urlpatterns = [
    path('', include(router.urls)),
    # URL 이름 변경: generate-next-plan -> generate-tomorrow-plan
    # URL에서 challenge_id 경로 파라미터 제거 (이제 요청 본문에서 제공)
    path('generate-tomorrow-plan/', GenerateNextPlanAPIView.as_view(), name='generate-tomorrow-plan'),
]

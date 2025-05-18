from .views import KakaoPayReadyView
from django.urls import path

urlpatterns = [
    path('kakao/ready/', KakaoPayReadyView.as_view(), name='ready'),
]
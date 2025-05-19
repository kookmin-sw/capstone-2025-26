from .views import KakaoPayReadyView, KakaoPayApproveView, KakaoPayFailView, KakaoPayCancelView
from django.urls import path

urlpatterns = [
    path('kakao/ready/', KakaoPayReadyView.as_view(), name='ready'),
    path('kakao/approve/', KakaoPayApproveView.as_view(), name='approve'),
    path('kakao/fail/', KakaoPayFailView.as_view(), name='fail'),
    path('kakao/cancel/', KakaoPayCancelView.as_view(), name='cancel'),
]
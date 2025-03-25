from .views import KakaoAuthorizeView, KakaoCallbackView
from django.urls import path

urlpatterns = [
    path('login/', KakaoAuthorizeView.as_view(), name='kakao_login_url'),
    path('callback/', KakaoCallbackView.as_view(), name='kakao_callback_url'), 
]
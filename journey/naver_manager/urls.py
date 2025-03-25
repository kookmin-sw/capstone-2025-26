from .views import NaverAuthorizeView, NaverCallbackView
from django.urls import path

urlpatterns = [
    path('login/', NaverAuthorizeView.as_view(), name='naver_login_url'),
    path('callback/', NaverCallbackView.as_view(), name='naver_callback_url'), 
]
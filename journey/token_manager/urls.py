from rest_framework_simplejwt.views import (
    TokenRefreshView, 
)
from .views import CustomTokenObtainPairView
from django.urls import path

urlpatterns = [
    path('', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
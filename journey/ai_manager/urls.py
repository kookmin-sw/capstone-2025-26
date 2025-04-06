# urls.py
from django.urls import path
from .views import llm_request

urlpatterns = [
    path('api/llm/', llm_request, name='llm_request'),
]

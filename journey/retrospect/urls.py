from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RetrospectViewSet, TemplateViewSet

router = DefaultRouter()
router.register(r'retrospects', RetrospectViewSet, basename='retrospect')
router.register(r'templates', TemplateViewSet, basename='template')

urlpatterns = [
    path('', include(router.urls)),
] 
"""
URL configuration for conversations app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, auth_views

router = DefaultRouter()
router.register(r'conversations', views.ConversationViewSet, basename='conversation')
router.register(r'intelligence', views.ConversationIntelligenceViewSet, basename='intelligence')

urlpatterns = [
    path('', include(router.urls)),
    # Auth endpoints
    path('auth/register/', auth_views.register, name='register'),
    path('auth/login/', auth_views.login, name='login'),
    path('auth/logout/', auth_views.logout, name='logout'),
    path('auth/user/', auth_views.get_current_user, name='current-user'),
    # Health check
    path('health/', views.health_check, name='health-check'),
]
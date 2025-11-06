"""
WebSocket routing configuration.
Enables real-time communication for chat.
"""
from django.urls import path

websocket_urlpatterns = [
    # WebSocket URL patterns can be added here if needed
    # path('ws/chat/<str:conversation_id>/', ChatConsumer.as_asgi()),
]
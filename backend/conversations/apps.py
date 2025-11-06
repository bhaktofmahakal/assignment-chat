"""Conversations app configuration."""
from django.apps import AppConfig


class ConversationsConfig(AppConfig):
    """Configuration for conversations app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'conversations'
    
    def ready(self):
        """Initialize app."""
        import conversations.signals  # noqa
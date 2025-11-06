"""Django signals for conversations app."""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Conversation, Message
from .ai_module import EmbeddingService

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Conversation)
def generate_conversation_embedding(sender, instance: Conversation, created: bool, **kwargs):
    """
    Generate embedding for conversation after it's ended.
    Used for semantic search.
    """
    if not created and instance.status == Conversation.Status.ENDED:
        try:
            embedding_service = EmbeddingService()
            text_to_embed = f"{instance.title} {instance.summary}"
            embedding = embedding_service.generate_embedding(text_to_embed)
            
            if embedding:
                instance.embedding = embedding
                instance.save(update_fields=['embedding'])
                logger.info(f"Embedding generated for conversation {instance.id}")
        
        except Exception as e:
            logger.error(f"Error generating conversation embedding: {str(e)}")


@receiver(post_save, sender=Message)
def generate_message_embedding(sender, instance: Message, created: bool, **kwargs):
    """
    Generate embedding for message for semantic search.
    """
    if created:
        try:
            embedding_service = EmbeddingService()
            embedding = embedding_service.generate_embedding(instance.content)
            
            if embedding:
                instance.embedding = embedding
                instance.save(update_fields=['embedding'])
                logger.info(f"Embedding generated for message {instance.id}")
        
        except Exception as e:
            logger.error(f"Error generating message embedding: {str(e)}")
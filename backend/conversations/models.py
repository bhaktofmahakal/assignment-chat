"""
Database models for conversation management.
Handles storage of conversations, messages, and conversation metadata.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MaxLengthValidator
from datetime import timedelta
import uuid


class Conversation(models.Model):
    """
    Represents a conversation session between a user and AI.
    
    Attributes:
        id: Unique identifier (UUID)
        user: Foreign key to Django User model
        title: Auto-generated or user-defined title
        description: Optional conversation description
        status: Current state of conversation (active, ended)
        started_at: Timestamp when conversation started
        ended_at: Timestamp when conversation ended
        summary: AI-generated summary (generated on conversation end)
        key_points: Extracted key points from conversation
        sentiment: Overall sentiment of conversation
        duration: Total duration in seconds
    """
    
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        ENDED = 'ended', 'Ended'
        ARCHIVED = 'archived', 'Archived'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True
    )
    started_at = models.DateTimeField(auto_now_add=True, db_index=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    key_points = models.JSONField(default=list, blank=True)
    sentiment = models.CharField(
        max_length=20,
        choices=[
            ('positive', 'Positive'),
            ('neutral', 'Neutral'),
            ('negative', 'Negative'),
            ('mixed', 'Mixed'),
        ],
        null=True,
        blank=True
    )
    duration = models.IntegerField(null=True, blank=True, help_text='Duration in seconds')
    embedding = models.JSONField(null=True, blank=True, help_text='Conversation embedding for semantic search')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', '-started_at']),
            models.Index(fields=['status', 'user']),
            models.Index(fields=['user', 'status']),
        ]
    
    def __str__(self) -> str:
        """Return string representation of conversation."""
        return f"{self.title} ({self.user.username})"
    
    def is_active(self) -> bool:
        """Check if conversation is active."""
        return self.status == self.Status.ACTIVE
    
    def end_conversation(self) -> None:
        """Mark conversation as ended and calculate duration."""
        self.status = self.Status.ENDED
        self.ended_at = timezone.now()
        if self.started_at:
            duration = (self.ended_at - self.started_at).total_seconds()
            self.duration = int(duration)
        self.save()
    
    def message_count(self) -> int:
        """Get total number of messages in conversation."""
        return self.messages.count()


class Message(models.Model):
    """
    Represents a single message in a conversation.
    
    Attributes:
        id: Unique identifier (UUID)
        conversation: Foreign key to Conversation
        sender: Role of sender (user or ai)
        content: Message text content
        metadata: Additional message metadata (e.g., processing info)
        embedding: Vector embedding for semantic search
        tokens_used: Token count for API billing tracking
        created_at: Timestamp when message was created
    """
    
    class Sender(models.TextChoices):
        USER = 'user', 'User'
        AI = 'ai', 'AI Assistant'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        db_index=True
    )
    sender = models.CharField(
        max_length=10,
        choices=Sender.choices,
        db_index=True
    )
    content = models.TextField(validators=[MaxLengthValidator(4000)])
    metadata = models.JSONField(default=dict, blank=True)
    embedding = models.JSONField(null=True, blank=True, help_text='Message embedding vector')
    tokens_used = models.IntegerField(default=0, help_text='Token count for API tracking')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['sender', 'created_at']),
        ]
    
    def __str__(self) -> str:
        """Return string representation of message."""
        preview = self.content[:50] + '...' if len(self.content) > 50 else self.content
        return f"{self.get_sender_display()}: {preview}"


class ConversationAnalysis(models.Model):
    """
    Stores analysis results for conversations.
    Used for conversation intelligence queries and semantic search.
    
    Attributes:
        conversation: Foreign key to Conversation
        topics: Extracted topics from conversation
        entities: Named entities found in conversation
        intent: Primary intent of conversation
        keywords: Important keywords
        sentiment_scores: Detailed sentiment breakdown
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.OneToOneField(
        Conversation,
        on_delete=models.CASCADE,
        related_name='analysis'
    )
    topics = models.JSONField(default=list, help_text='Extracted topics with confidence scores')
    entities = models.JSONField(default=list, help_text='Named entities and their types')
    intent = models.CharField(max_length=100, blank=True)
    keywords = models.JSONField(default=list, help_text='Important keywords')
    sentiment_scores = models.JSONField(default=dict, help_text='Detailed sentiment analysis')
    action_items = models.JSONField(default=list, help_text='Extracted action items')
    questions_asked = models.JSONField(default=list, help_text='Questions from the conversation')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Conversation Analyses'
        indexes = [
            models.Index(fields=['conversation']),
        ]
    
    def __str__(self) -> str:
        """Return string representation."""
        return f"Analysis for {self.conversation.title}"


class SearchQuery(models.Model):
    """
    Logs user search queries for analytics and improvement.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='search_queries')
    query_text = models.TextField()
    results_count = models.IntegerField(default=0)
    execution_time = models.FloatField(help_text='Query execution time in seconds')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self) -> str:
        """Return string representation."""
        return f"Query by {self.user.username}: {self.query_text[:50]}"
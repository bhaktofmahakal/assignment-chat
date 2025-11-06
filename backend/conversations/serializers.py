"""
Serializers for API endpoints.
Handles serialization/deserialization of model instances for JSON API responses.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Conversation, Message, ConversationAnalysis, SearchQuery
from typing import Dict, Any, List


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model."""
    
    sender_display = serializers.CharField(source='get_sender_display', read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'id',
            'conversation',
            'sender',
            'sender_display',
            'content',
            'metadata',
            'tokens_used',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'tokens_used']


class ConversationListSerializer(serializers.ModelSerializer):
    """Serializer for listing conversations (summary view)."""
    
    message_count = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Conversation
        fields = [
            'id',
            'title',
            'description',
            'status',
            'status_display',
            'started_at',
            'ended_at',
            'message_count',
            'sentiment',
            'duration',
        ]
        read_only_fields = ['id', 'started_at', 'ended_at']
    
    def get_message_count(self, obj: Conversation) -> int:
        """Get count of messages in conversation."""
        return obj.message_count()


class ConversationDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed conversation view with full message history."""
    
    messages = MessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Conversation
        fields = [
            'id',
            'title',
            'description',
            'status',
            'status_display',
            'started_at',
            'ended_at',
            'summary',
            'key_points',
            'sentiment',
            'duration',
            'message_count',
            'messages',
        ]
        read_only_fields = [
            'id',
            'started_at',
            'ended_at',
            'summary',
            'key_points',
            'sentiment',
            'duration',
        ]
    
    def get_message_count(self, obj: Conversation) -> int:
        """Get count of messages in conversation."""
        return obj.message_count()


class ConversationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new conversations."""
    
    class Meta:
        model = Conversation
        fields = ['title', 'description']
    
    def validate_title(self, value: str) -> str:
        """Validate title is not empty and reasonable length."""
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        if len(value) > 255:
            raise serializers.ValidationError("Title cannot exceed 255 characters.")
        return value.strip()


class ConversationAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for conversation analysis."""
    
    class Meta:
        model = ConversationAnalysis
        fields = [
            'id',
            'conversation',
            'topics',
            'entities',
            'intent',
            'keywords',
            'sentiment_scores',
            'action_items',
            'questions_asked',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class SearchQuerySerializer(serializers.ModelSerializer):
    """Serializer for search queries."""
    
    class Meta:
        model = SearchQuery
        fields = ['id', 'query_text', 'results_count', 'execution_time', 'created_at']
        read_only_fields = ['id', 'created_at', 'results_count', 'execution_time']


class ConversationIntelligenceQuerySerializer(serializers.Serializer):
    """Serializer for conversation intelligence queries."""
    
    query = serializers.CharField(
        max_length=1000,
        help_text="Question about past conversations"
    )
    date_from = serializers.DateTimeField(
        required=False,
        allow_null=True,
        help_text="Filter conversations from this date"
    )
    date_to = serializers.DateTimeField(
        required=False,
        allow_null=True,
        help_text="Filter conversations until this date"
    )
    topics = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list,
        help_text="Filter by specific topics"
    )
    limit = serializers.IntegerField(
        default=5,
        min_value=1,
        max_value=50,
        help_text="Maximum number of results"
    )
    
    def validate_query(self, value: str) -> str:
        """Validate query is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Query cannot be empty.")
        return value.strip()
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate date range."""
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError(
                "date_from must be before date_to"
            )
        
        return data


class MessageCreateSerializer(serializers.Serializer):
    """Serializer for creating messages in a conversation."""
    
    content = serializers.CharField(
        max_length=4000,
        help_text="Message content"
    )
    
    def validate_content(self, value: str) -> str:
        """Validate message content."""
        if not value or not value.strip():
            raise serializers.ValidationError("Message cannot be empty.")
        return value.strip()


class ConversationEndSerializer(serializers.Serializer):
    """Serializer for ending a conversation."""
    
    generate_summary = serializers.BooleanField(
        default=True,
        help_text="Whether to generate AI summary"
    )


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user information."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']
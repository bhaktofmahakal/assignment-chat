"""Django admin configuration for conversations app."""
from django.contrib import admin
from .models import Conversation, Message, ConversationAnalysis, SearchQuery


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Admin configuration for Conversation model."""
    list_display = ['title', 'user', 'status', 'started_at', 'message_count']
    list_filter = ['status', 'started_at', 'sentiment']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['id', 'created_at', 'updated_at', 'started_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('id', 'user', 'title', 'description')
        }),
        ('Status', {
            'fields': ('status', 'started_at', 'ended_at', 'duration')
        }),
        ('Analysis', {
            'fields': ('summary', 'key_points', 'sentiment', 'embedding')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin configuration for Message model."""
    list_display = ['id', 'conversation', 'sender', 'content_preview', 'created_at']
    list_filter = ['sender', 'created_at', 'conversation__user']
    search_fields = ['content', 'conversation__title']
    readonly_fields = ['id', 'created_at', 'embedding']
    
    def content_preview(self, obj):
        """Display content preview."""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    
    content_preview.short_description = 'Content'


@admin.register(ConversationAnalysis)
class ConversationAnalysisAdmin(admin.ModelAdmin):
    """Admin configuration for ConversationAnalysis model."""
    list_display = ['conversation', 'intent', 'created_at']
    list_filter = ['created_at', 'intent']
    search_fields = ['conversation__title', 'topics']
    readonly_fields = ['id', 'created_at']


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    """Admin configuration for SearchQuery model."""
    list_display = ['query_text', 'user', 'results_count', 'execution_time', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['query_text', 'user__username']
    readonly_fields = ['id', 'created_at', 'results_count', 'execution_time']
"""
API Views for conversation management and AI integration.
Implements RESTful endpoints for chat, conversation management, and intelligence queries.
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from uuid import UUID

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, QuerySet, Prefetch
from django.http import JsonResponse, StreamingHttpResponse

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request

from .models import Conversation, Message, ConversationAnalysis, SearchQuery
from .serializers import (
    ConversationDetailSerializer,
    ConversationListSerializer,
    ConversationCreateSerializer,
    MessageSerializer,
    MessageCreateSerializer,
    ConversationAnalysisSerializer,
    ConversationEndSerializer,
    ConversationIntelligenceQuerySerializer,
)
from .ai_module import ChatService, ConversationSummarizer, EmbeddingService, QueryEngine

logger = logging.getLogger(__name__)


class ConversationPagination(PageNumberPagination):
    """Custom pagination for conversation lists."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations.
    
    Endpoints:
        - GET /conversations/ - List all conversations
        - POST /conversations/ - Create new conversation
        - GET /conversations/{id}/ - Get conversation details
        - PATCH /conversations/{id}/ - Update conversation
        - DELETE /conversations/{id}/ - Delete conversation
        - POST /conversations/{id}/end/ - End conversation
        - POST /conversations/{id}/messages/ - Send message
        - GET /conversations/{id}/messages/ - Get conversation messages
    """
    
    permission_classes = [IsAuthenticated]
    pagination_class = ConversationPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['started_at', 'updated_at']
    ordering = ['-started_at']
    
    def get_queryset(self) -> QuerySet:
        """Get conversations for current user."""
        queryset = Conversation.objects.filter(user=self.request.user)
        
        # Optimize queries with prefetch
        queryset = queryset.prefetch_related(
            Prefetch('messages'),
            Prefetch('analysis')
        )
        
        # Filter by status if provided
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return ConversationCreateSerializer
        elif self.action == 'retrieve':
            return ConversationDetailSerializer
        else:
            return ConversationListSerializer
    
    def perform_create(self, serializer) -> None:
        """Create conversation for current user."""
        serializer.save(user=self.request.user)
        logger.info(f"Conversation created: {serializer.instance.id} by {self.request.user.username}")
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def end(self, request: Request, pk: UUID = None) -> Response:
        """
        End a conversation and generate summary.
        
        Args:
            request: HTTP request
            pk: Conversation UUID
            
        Returns:
            Response with conversation details and summary
        """
        conversation = self.get_object()
        
        if not conversation.is_active():
            return Response(
                {'error': 'Conversation is already ended.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ConversationEndSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # End conversation
            conversation.end_conversation()
            
            # Generate summary if requested
            if serializer.validated_data.get('generate_summary', True):
                summarizer = ConversationSummarizer()
                summary_data = summarizer.generate_summary(conversation)
                
                conversation.summary = summary_data.get('summary')
                conversation.key_points = summary_data.get('key_points', [])
                conversation.sentiment = summary_data.get('sentiment')
                
                conversation.save()
                
                # Generate analysis
                analyzer = QueryEngine()
                analysis_data = analyzer.analyze_conversation(conversation)
                
                ConversationAnalysis.objects.update_or_create(
                    conversation=conversation,
                    defaults=analysis_data
                )
            
            logger.info(f"Conversation ended: {conversation.id}")
            return Response(
                ConversationDetailSerializer(conversation).data,
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            logger.error(f"Error ending conversation {conversation.id}: {str(e)}")
            return Response(
                {'error': f'Failed to end conversation: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def send_message(self, request: Request, pk: UUID = None) -> Response:
        """
        Send a message in a conversation.
        
        Args:
            request: HTTP request with message content
            pk: Conversation UUID
            
        Returns:
            Response with user message and AI response
        """
        conversation = self.get_object()
        
        if not conversation.is_active():
            return Response(
                {'error': 'Cannot send message to ended conversation.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = MessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            user_message_content = serializer.validated_data['content']
            
            # Create user message
            user_message = Message.objects.create(
                conversation=conversation,
                sender=Message.Sender.USER,
                content=user_message_content,
                metadata={'ip': self._get_client_ip(request)}
            )
            
            # Get AI response
            chat_service = ChatService()
            ai_response_content = chat_service.get_response(conversation, user_message)
            
            # Create AI message
            ai_message = Message.objects.create(
                conversation=conversation,
                sender=Message.Sender.AI,
                content=ai_response_content,
                metadata={'model': chat_service.model}
            )
            
            logger.info(f"Message sent in conversation {conversation.id}")
            
            return Response({
                'user_message': MessageSerializer(user_message).data,
                'ai_message': MessageSerializer(ai_message).data,
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"Error sending message in {conversation.id}: {str(e)}")
            return Response(
                {'error': f'Failed to send message: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def messages(self, request: Request, pk: UUID = None) -> Response:
        """
        Get all messages in a conversation with pagination.
        
        Args:
            request: HTTP request
            pk: Conversation UUID
            
        Returns:
            Paginated list of messages
        """
        conversation = self.get_object()
        messages = Message.objects.filter(conversation=conversation)
        
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(messages, request)
        if page is not None:
            serializer = MessageSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ConversationIntelligenceViewSet(viewsets.ViewSet):
    """
    ViewSet for conversation intelligence queries.
    
    Endpoints:
        - POST /intelligence/query/ - Query past conversations with AI
        - GET /intelligence/analytics/ - Get conversation analytics
    """
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def query(self, request: Request) -> Response:
        """
        Query past conversations using AI-powered search and analysis.
        
        Args:
            request: HTTP request with query parameters
            
        Returns:
            AI response with relevant conversation excerpts
        """
        serializer = ConversationIntelligenceQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            query_text = serializer.validated_data['query']
            date_from = serializer.validated_data.get('date_from')
            date_to = serializer.validated_data.get('date_to')
            topics = serializer.validated_data.get('topics', [])
            limit = serializer.validated_data.get('limit', 5)
            
            # Log search query
            start_time = timezone.now()
            
            # Get relevant conversations
            query_engine = QueryEngine()
            results = query_engine.search_conversations(
                user=request.user,
                query=query_text,
                date_from=date_from,
                date_to=date_to,
                topics=topics,
                limit=limit
            )
            
            # Generate AI response
            ai_response = query_engine.generate_intelligence_response(
                query_text,
                results
            )
            
            # Serialize results
            serialized_results = []
            for result in results:
                conversation = result['conversation']
                serialized_results.append({
                    'conversation': ConversationListSerializer(conversation).data,
                    'similarity_score': result.get('similarity_score', 0),
                    'excerpt': result.get('excerpt', ''),
                    'message_count': conversation.message_count(),
                })
            
            # Log execution time
            execution_time = (timezone.now() - start_time).total_seconds()
            SearchQuery.objects.create(
                user=request.user,
                query_text=query_text,
                results_count=len(results),
                execution_time=execution_time
            )
            
            logger.info(f"Intelligence query by {request.user.username}: {query_text[:50]}")
            
            return Response({
                'query': query_text,
                'ai_response': ai_response,
                'relevant_conversations': serialized_results,
                'results_count': len(results),
                'execution_time': execution_time,
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error in intelligence query: {str(e)}")
            return Response(
                {'error': f'Failed to process query: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def analytics(self, request: Request) -> Response:
        """
        Get conversation analytics for the user.
        
        Args:
            request: HTTP request
            
        Returns:
            Analytics data about conversations
        """
        try:
            user_conversations = Conversation.objects.filter(user=request.user)
            
            analytics = {
                'total_conversations': user_conversations.count(),
                'active_conversations': user_conversations.filter(
                    status=Conversation.Status.ACTIVE
                ).count(),
                'ended_conversations': user_conversations.filter(
                    status=Conversation.Status.ENDED
                ).count(),
                'total_messages': Message.objects.filter(
                    conversation__user=request.user
                ).count(),
                'average_messages_per_conversation': (
                    Message.objects.filter(conversation__user=request.user).count()
                    / max(user_conversations.count(), 1)
                ),
                'sentiment_distribution': self._get_sentiment_distribution(user_conversations),
                'recent_conversations': ConversationListSerializer(
                    user_conversations[:5],
                    many=True
                ).data,
            }
            
            return Response(analytics, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error generating analytics: {str(e)}")
            return Response(
                {'error': f'Failed to generate analytics: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_sentiment_distribution(self, conversations: QuerySet) -> Dict[str, int]:
        """Get sentiment distribution for conversations."""
        distribution = {
            'positive': 0,
            'neutral': 0,
            'negative': 0,
            'mixed': 0,
        }
        
        for conversation in conversations:
            if conversation.sentiment:
                distribution[conversation.sentiment] = distribution.get(conversation.sentiment, 0) + 1
        
        return distribution


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def health_check(request: Request) -> Response:
    """
    Health check endpoint.
    
    Returns:
        Status information
    """
    return Response({
        'status': 'healthy',
        'timestamp': timezone.now(),
        'user': request.user.username,
    })
"""
AI Integration Module
Handles AI-powered chat, summarization, embeddings, and intelligent queries.
"""
import logging
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import os

import numpy as np
import requests
from django.conf import settings
from django.contrib.auth.models import User

from .models import Conversation, Message
from django.db.models import Q

logger = logging.getLogger(__name__)


class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    @abstractmethod
    def get_response(self, messages: List[Dict[str, str]]) -> str:
        """Get response from AI provider."""
        pass
    
    @abstractmethod
    def get_embeddings(self, text: str) -> List[float]:
        """Get embeddings for text."""
        pass


class OpenAIProvider(AIProvider):
    """OpenAI API provider."""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = "https://api.openai.com/v1"
        self.model = settings.CHAT_MODEL
        self.embedding_model = settings.EMBEDDING_MODEL
    
    def get_response(self, messages: List[Dict[str, str]]) -> str:
        """Get response from OpenAI."""
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2000,
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    def get_embeddings(self, text: str) -> List[float]:
        """Get embeddings from OpenAI."""
        try:
            response = requests.post(
                f"{self.base_url}/embeddings",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.embedding_model,
                    "input": text,
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()['data'][0]['embedding']
        except Exception as e:
            logger.error(f"OpenAI embeddings error: {str(e)}")
            raise


class LMStudioProvider(AIProvider):
    """LM Studio local provider."""
    
    def __init__(self):
        self.base_url = settings.LM_STUDIO_URL
        self.model = settings.CHAT_MODEL
    
    def get_response(self, messages: List[Dict[str, str]]) -> str:
        """Get response from LM Studio."""
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2000,
                    "stream": False,
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"LM Studio API error: {str(e)}")
            raise
    
    def get_embeddings(self, text: str) -> List[float]:
        """Generate embeddings using LM Studio (fallback to simple hash)."""
        # LM Studio may not have embeddings endpoint, use simple implementation
        try:
            response = requests.post(
                f"{self.base_url}/embeddings",
                json={
                    "model": self.model,
                    "input": text,
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()['data'][0]['embedding']
        except:
            # Fallback: create simple deterministic embedding
            return self._simple_embedding(text)
    
    @staticmethod
    def _simple_embedding(text: str, dim: int = 1536) -> List[float]:
        """Create simple deterministic embedding."""
        hash_val = hash(text) % 2**32
        np.random.seed(hash_val)
        return np.random.randn(dim).tolist()


class GeminiProvider(AIProvider):
    """Google Generative AI (Gemini) provider."""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        # Use gemini-2.0-flash as it's the current latest and fastest model
        # Falls back to gemini-1.5-pro if 2.0-flash is unavailable
        self.model = "gemini-2.0-flash"
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
    
    def get_response(self, messages: List[Dict[str, str]]) -> str:
        """Get response from Gemini API."""
        try:
            # Convert messages to Gemini format
            contents = self._format_messages_for_gemini(messages)
            
            response = requests.post(
                f"{self.base_url}/{self.model}:generateContent",
                params={"key": self.api_key},
                json={
                    "contents": contents,
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 2000,
                    }
                },
                timeout=30
            )
            
            # Handle 404 (model not found) - try fallback models
            if response.status_code == 404:
                if self.model == "gemini-2.0-flash":
                    logger.warning(f"Model {self.model} not found, falling back to gemini-1.5-pro")
                    self.model = "gemini-1.5-pro"
                    return self.get_response(messages)
                elif self.model == "gemini-1.5-pro":
                    logger.warning(f"Model {self.model} not found, falling back to gemini-pro")
                    self.model = "gemini-pro"
                    return self.get_response(messages)
            
            response.raise_for_status()
            
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                raise Exception("No response from Gemini API")
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise
    
    def get_embeddings(self, text: str) -> List[float]:
        """Generate embeddings using Gemini Embedding API."""
        try:
            response = requests.post(
                f"{self.base_url}/embedding-001:embedContent",
                params={"key": self.api_key},
                json={
                    "model": f"models/embedding-001",
                    "content": {
                        "parts": [{"text": text}]
                    }
                },
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            if 'embedding' in result:
                return result['embedding']['values']
            else:
                # If no embedding in response, return empty to trigger fallback
                return []
        except Exception as e:
            logger.error(f"Gemini embeddings error: {str(e)}")
            # Return empty list to trigger fallback text search instead of using simple embedding
            return []
    
    @staticmethod
    def _format_messages_for_gemini(messages: List[Dict[str, str]]) -> List[Dict]:
        """Convert OpenAI format messages to Gemini format."""
        contents = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            # Skip system messages for Gemini (it handles context differently)
            if role == "system":
                continue
            
            # Map user/assistant roles
            gemini_role = "user" if role in ["user", "system"] else "model"
            
            contents.append({
                "role": gemini_role,
                "parts": [{"text": content}]
            })
        
        return contents if contents else [{"role": "user", "parts": [{"text": "Hello"}]}]
    
    @staticmethod
    def _simple_embedding(text: str, dim: int = 768) -> List[float]:
        """Create simple deterministic embedding as fallback."""
        hash_val = hash(text) % 2**32
        np.random.seed(hash_val)
        return np.random.randn(dim).tolist()


class ChatService:
    """
    Service for handling real-time chat with AI.
    Maintains conversation context and handles message flow.
    """
    
    def __init__(self):
        self.provider = self._get_provider()
        self.model = settings.CHAT_MODEL
        self.max_context_messages = 20
    
    def _get_provider(self) -> AIProvider:
        """Get appropriate AI provider based on settings."""
        ai_provider = settings.AI_PROVIDER.lower()
        
        if ai_provider == 'openai':
            return OpenAIProvider()
        elif ai_provider == 'gemini':
            return GeminiProvider()
        elif ai_provider == 'lm_studio':
            return LMStudioProvider()
        else:
            # Default to LM Studio
            return LMStudioProvider()
    
    def get_response(self, conversation: Conversation, user_message: Message) -> str:
        """
        Get AI response for a user message.
        
        Args:
            conversation: Conversation instance
            user_message: User message instance
            
        Returns:
            AI response text
        """
        try:
            # Build message context
            messages = self._build_context(conversation)
            messages.append({
                "role": "user",
                "content": user_message.content
            })
            
            # Get response from provider
            response_text = self.provider.get_response(messages)
            
            logger.info(f"AI response generated for conversation {conversation.id}")
            return response_text
        
        except Exception as e:
            logger.error(f"Error getting AI response: {str(e)}")
            # Return a fallback response instead of failing completely
            fallback_response = self._get_fallback_response(user_message.content)
            logger.info(f"Using fallback response for conversation {conversation.id}")
            return fallback_response
    
    def _get_fallback_response(self, user_message: str) -> str:
        """
        Generate a simple fallback response when AI is unavailable.
        
        Args:
            user_message: The user's message
            
        Returns:
            A simple acknowledgment response
        """
        # Extract key question words to provide more relevant fallback
        keywords = ['what', 'how', 'why', 'when', 'where', 'who', 'which', 'can', 'could', 'would', 'help']
        user_lower = user_message.lower()
        
        if any(keyword in user_lower for keyword in keywords):
            return f"I appreciate your question about '{user_message[:50]}...'. Unfortunately, I'm currently experiencing temporary service issues. Please try again in a moment."
        else:
            return f"Thank you for your message. I'm temporarily unavailable, but I've recorded your message. Please try again shortly."
    
    def _build_context(self, conversation: Conversation) -> List[Dict[str, str]]:
        """Build message context for conversation."""
        messages = []
        
        # Add system message
        messages.append({
            "role": "system",
            "content": "You are a helpful AI assistant. Provide clear, concise, and helpful responses."
        })
        
        # Add conversation history
        recent_messages = Message.objects.filter(
            conversation=conversation
        ).order_by('-created_at')[:self.max_context_messages]
        
        for msg in reversed(recent_messages):
            messages.append({
                "role": "assistant" if msg.sender == Message.Sender.AI else "user",
                "content": msg.content
            })
        
        return messages


class ConversationSummarizer:
    """
    Service for generating conversation summaries.
    Extracts key points and creates concise summaries.
    """
    
    def __init__(self):
        self.provider = self._get_provider()
    
    def _get_provider(self) -> AIProvider:
        """Get AI provider."""
        ai_provider = settings.AI_PROVIDER.lower()
        if ai_provider == 'openai':
            return OpenAIProvider()
        elif ai_provider == 'gemini':
            return GeminiProvider()
        else:
            return LMStudioProvider()
    
    def generate_summary(self, conversation: Conversation) -> Dict[str, Any]:
        """
        Generate summary for completed conversation.
        
        Args:
            conversation: Completed conversation
            
        Returns:
            Dictionary with summary, key_points, and sentiment
        """
        try:
            # Get all messages
            messages = Message.objects.filter(conversation=conversation).order_by('created_at')
            
            if not messages.exists():
                return {
                    'summary': 'No messages in conversation.',
                    'key_points': [],
                    'sentiment': 'neutral'
                }
            
            # Build conversation text
            conversation_text = self._build_conversation_text(messages)
            
            # Generate summary
            summary = self._generate_summary_text(conversation_text)
            
            # Extract key points
            key_points = self._extract_key_points(conversation_text)
            
            # Analyze sentiment
            sentiment = self._analyze_sentiment(conversation_text)
            
            logger.info(f"Summary generated for conversation {conversation.id}")
            
            return {
                'summary': summary,
                'key_points': key_points,
                'sentiment': sentiment
            }
        
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return {
                'summary': 'Failed to generate summary.',
                'key_points': [],
                'sentiment': 'neutral'
            }
    
    def _build_conversation_text(self, messages) -> str:
        """Build text representation of conversation."""
        text = ""
        for msg in messages:
            sender = "User" if msg.sender == Message.Sender.USER else "AI"
            text += f"{sender}: {msg.content}\n\n"
        return text
    
    def _generate_summary_text(self, conversation_text: str) -> str:
        """Generate summary using AI."""
        try:
            response = self.provider.get_response([
                {
                    "role": "system",
                    "content": "Summarize the following conversation in 2-3 sentences."
                },
                {
                    "role": "user",
                    "content": f"Conversation:\n\n{conversation_text}"
                }
            ])
            return response
        except Exception as e:
            logger.error(f"Error generating summary text: {str(e)}")
            return "Unable to generate summary."
    
    def _extract_key_points(self, conversation_text: str) -> List[str]:
        """Extract key points from conversation."""
        try:
            response = self.provider.get_response([
                {
                    "role": "system",
                    "content": "Extract 3-5 key points from the conversation. Return as JSON array of strings."
                },
                {
                    "role": "user",
                    "content": f"Conversation:\n\n{conversation_text}"
                }
            ])
            
            # Parse JSON response
            try:
                return json.loads(response)
            except:
                return [point.strip() for point in response.split('\n') if point.strip()]
        
        except Exception as e:
            logger.error(f"Error extracting key points: {str(e)}")
            return []
    
    def _analyze_sentiment(self, conversation_text: str) -> str:
        """Analyze overall sentiment of conversation."""
        try:
            response = self.provider.get_response([
                {
                    "role": "system",
                    "content": "Analyze the sentiment of this conversation. Respond with one word: positive, negative, neutral, or mixed."
                },
                {
                    "role": "user",
                    "content": f"Conversation:\n\n{conversation_text}"
                }
            ])
            
            sentiment = response.strip().lower()
            valid_sentiments = ['positive', 'negative', 'neutral', 'mixed']
            return sentiment if sentiment in valid_sentiments else 'neutral'
        
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return 'neutral'


class EmbeddingService:
    """Service for generating and managing embeddings."""
    
    def __init__(self):
        self.provider = self._get_provider()
    
    def _get_provider(self) -> AIProvider:
        """Get AI provider."""
        ai_provider = settings.AI_PROVIDER.lower()
        if ai_provider == 'openai':
            return OpenAIProvider()
        elif ai_provider == 'gemini':
            return GeminiProvider()
        else:
            return LMStudioProvider()
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text."""
        try:
            return self.provider.get_embeddings(text)
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return []
    
    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between embeddings."""
        try:
            arr1 = np.array(embedding1)
            arr2 = np.array(embedding2)
            
            norm1 = np.linalg.norm(arr1)
            norm2 = np.linalg.norm(arr2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return float(np.dot(arr1, arr2) / (norm1 * norm2))
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0


class QueryEngine:
    """
    Service for intelligent conversation queries and analysis.
    Implements semantic search and conversation intelligence.
    """
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.provider = self._get_provider()
        self.similarity_threshold = 0.5
    
    def _get_provider(self) -> AIProvider:
        """Get AI provider."""
        ai_provider = settings.AI_PROVIDER.lower()
        if ai_provider == 'openai':
            return OpenAIProvider()
        elif ai_provider == 'gemini':
            return GeminiProvider()
        else:
            return LMStudioProvider()
    
    def search_conversations(
        self,
        user: User,
        query: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        topics: Optional[List[str]] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search conversations using semantic similarity.
        
        Args:
            user: User instance
            query: Search query
            date_from: Optional start date filter
            date_to: Optional end date filter
            topics: Optional topic filters
            limit: Maximum number of results
            
        Returns:
            List of relevant conversation data
        """
        try:
            # Get query embedding
            query_embedding = self.embedding_service.generate_embedding(query)
            
            if not query_embedding:
                # Fallback to text search
                return self._fallback_search(user, query, date_from, date_to, limit)
            
            # Get user conversations (both active and ended)
            conversations = Conversation.objects.filter(
                user=user
            ).exclude(status=Conversation.Status.ARCHIVED)
            
            # Apply date filters
            if date_from:
                conversations = conversations.filter(started_at__gte=date_from)
            if date_to:
                conversations = conversations.filter(ended_at__lte=date_to)
            
            # Calculate similarity scores
            results = []
            for conv in conversations:
                if conv.embedding:
                    similarity = self.embedding_service.similarity(
                        query_embedding,
                        conv.embedding
                    )
                    
                    if similarity > self.similarity_threshold:
                        results.append({
                            'conversation': conv,
                            'similarity_score': similarity,
                            'excerpt': conv.summary or 'No summary available'
                        })
            
            # Sort by similarity and limit
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            return results[:limit]
        
        except Exception as e:
            logger.error(f"Error searching conversations: {str(e)}")
            return self._fallback_search(user, query, date_from, date_to, limit)
    
    def _fallback_search(
        self,
        user: User,
        query: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Fallback keyword search in conversation titles and message content."""
        # Search by title or message content
        conversations = Conversation.objects.filter(
            user=user
        ).exclude(
            status=Conversation.Status.ARCHIVED
        ).filter(
            Q(title__icontains=query) | Q(messages__content__icontains=query)
        ).distinct()
        
        if date_from:
            conversations = conversations.filter(started_at__gte=date_from)
        if date_to:
            conversations = conversations.filter(ended_at__lte=date_to)
        
        return [
            {
                'conversation': conv,
                'similarity_score': 0.5,
                'excerpt': conv.summary or self._extract_excerpt(conv, query)
            }
            for conv in conversations[:limit]
        ]
    
    def _extract_excerpt(self, conversation: Conversation, query: str) -> str:
        """Extract relevant excerpt from conversation messages containing query."""
        try:
            messages = conversation.messages.filter(
                content__icontains=query
            ).values_list('content', flat=True)
            
            if messages:
                excerpt = messages[0]
                # Limit excerpt to 150 characters
                return excerpt[:150] + '...' if len(excerpt) > 150 else excerpt
            
            return conversation.summary or 'No summary available'
        except Exception as e:
            logger.warning(f"Error extracting excerpt: {str(e)}")
            return conversation.summary or 'No summary available'
    
    def generate_intelligence_response(
        self,
        query: str,
        search_results: List[Dict[str, Any]]
    ) -> str:
        """
        Generate AI response for conversation intelligence query.
        
        Args:
            query: Original user query
            search_results: Search results from semantic search
            
        Returns:
            AI-generated response with relevant information
        """
        try:
            if not search_results:
                return "No relevant conversations found for your query."
            
            # Build context from search results
            context = self._build_query_context(search_results)
            
            # Generate response
            response = self.provider.get_response([
                {
                    "role": "system",
                    "content": "Answer the user's question about their past conversations based on the provided context."
                },
                {
                    "role": "user",
                    "content": f"Context from past conversations:\n{context}\n\nQuestion: {query}"
                }
            ])
            
            return response
        
        except Exception as e:
            logger.error(f"Error generating intelligence response: {str(e)}")
            return "Unable to generate response. Please try again."
    
    def _build_query_context(self, search_results: List[Dict[str, Any]]) -> str:
        """Build context from search results."""
        context = ""
        for i, result in enumerate(search_results, 1):
            conv = result['conversation']
            context += f"\nConversation {i}: {conv.title}\n"
            context += f"Date: {conv.started_at.strftime('%Y-%m-%d %H:%M')}\n"
            context += f"Summary: {conv.summary}\n"
            context += f"Sentiment: {conv.sentiment}\n"
        
        return context
    
    def analyze_conversation(self, conversation: Conversation) -> Dict[str, Any]:
        """
        Analyze conversation for intelligence features.
        
        Args:
            conversation: Conversation to analyze
            
        Returns:
            Analysis data
        """
        try:
            # Get conversation text
            messages = Message.objects.filter(conversation=conversation)
            conversation_text = "\n".join([f"{msg.get_sender_display()}: {msg.content}" for msg in messages])
            
            # Extract topics
            topics = self._extract_topics(conversation_text)
            
            # Extract entities
            entities = self._extract_entities(conversation_text)
            
            # Extract action items
            action_items = self._extract_action_items(conversation_text)
            
            # Extract questions
            questions = self._extract_questions(messages)
            
            return {
                'topics': topics,
                'entities': entities,
                'keywords': topics[:5],  # Top 5 topics as keywords
                'action_items': action_items,
                'questions_asked': questions,
                'sentiment_scores': {'overall': 0.5},
                'intent': 'general_conversation',
            }
        
        except Exception as e:
            logger.error(f"Error analyzing conversation: {str(e)}")
            return {}
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from conversation text."""
        try:
            response = self.provider.get_response([
                {
                    "role": "system",
                    "content": "Extract main topics from the conversation. Return as JSON array of strings."
                },
                {
                    "role": "user",
                    "content": f"Conversation:\n{text}"
                }
            ])
            
            try:
                return json.loads(response)
            except:
                return [topic.strip() for topic in response.split(',') if topic.strip()]
        
        except Exception as e:
            logger.error(f"Error extracting topics: {str(e)}")
            return []
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract entities from conversation text."""
        try:
            response = self.provider.get_response([
                {
                    "role": "system",
                    "content": "Extract important named entities (people, places, organizations) from the conversation. Return as JSON array."
                },
                {
                    "role": "user",
                    "content": f"Conversation:\n{text}"
                }
            ])
            
            try:
                return json.loads(response)
            except:
                return [entity.strip() for entity in response.split(',') if entity.strip()]
        
        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
            return []
    
    def _extract_action_items(self, text: str) -> List[str]:
        """Extract action items from conversation."""
        try:
            response = self.provider.get_response([
                {
                    "role": "system",
                    "content": "Extract action items or tasks mentioned in the conversation. Return as JSON array."
                },
                {
                    "role": "user",
                    "content": f"Conversation:\n{text}"
                }
            ])
            
            try:
                return json.loads(response)
            except:
                return [item.strip() for item in response.split(',') if item.strip()]
        
        except Exception as e:
            logger.error(f"Error extracting action items: {str(e)}")
            return []
    
    def _extract_questions(self, messages) -> List[str]:
        """Extract questions from conversation."""
        questions = []
        for msg in messages:
            if msg.sender == Message.Sender.USER and '?' in msg.content:
                questions.append(msg.content)
        return questions
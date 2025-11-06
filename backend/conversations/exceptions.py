"""Custom exception handlers and utilities."""
import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for API.
    Provides consistent error response format.
    """
    response = exception_handler(exc, context)
    
    if response is None:
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return Response(
            {
                'error': 'Internal server error',
                'detail': str(exc)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Log error
    logger.error(f"API Error: {str(exc)}")
    
    return response


class ConversationError(Exception):
    """Base exception for conversation errors."""
    pass


class ConversationNotFoundError(ConversationError):
    """Raised when conversation is not found."""
    pass


class AIServiceError(ConversationError):
    """Raised when AI service encounters error."""
    pass


class MessageError(ConversationError):
    """Raised when message processing fails."""
    pass
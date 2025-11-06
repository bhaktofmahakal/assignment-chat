"""
Authentication Views
Handles user registration, login, and token management.
"""
import logging
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user account.
    
    Expected request body:
    {
        "username": "string",
        "email": "string",
        "password": "string"
    }
    
    Returns:
    {
        "user": {
            "id": "integer",
            "username": "string",
            "email": "string"
        },
        "token": "string"
    }
    """
    data = request.data
    
    # Validate input
    if not data.get('username') or not data.get('password'):
        return Response(
            {'error': 'Username and password are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not data.get('email'):
        return Response(
            {'error': 'Email is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if user already exists
    if User.objects.filter(username=data['username']).exists():
        return Response(
            {'error': 'Username already exists.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if User.objects.filter(email=data['email']).exists():
        return Response(
            {'error': 'Email already exists.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Create user
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password']
        )
        
        # Create token
        token, _ = Token.objects.get_or_create(user=user)
        
        logger.info(f"New user registered: {user.username}")
        
        return Response(
            {
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                },
                'token': token.key,
            },
            status=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return Response(
            {'error': 'Failed to register user.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login user and return authentication token.
    
    Expected request body:
    {
        "username": "string",
        "password": "string"
    }
    
    Returns:
    {
        "user": {
            "id": "integer",
            "username": "string",
            "email": "string"
        },
        "token": "string"
    }
    """
    data = request.data
    
    # Validate input
    if not data.get('username') or not data.get('password'):
        return Response(
            {'error': 'Username and password are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Authenticate user
    user = authenticate(
        username=data['username'],
        password=data['password']
    )
    
    if not user:
        return Response(
            {'error': 'Invalid credentials.'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        # Get or create token
        token, _ = Token.objects.get_or_create(user=user)
        
        logger.info(f"User logged in: {user.username}")
        
        return Response(
            {
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                },
                'token': token.key,
            },
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return Response(
            {'error': 'Failed to login.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """
    Get current authenticated user information.
    
    Returns:
    {
        "id": "integer",
        "username": "string",
        "email": "string"
    }
    """
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Logout user by invalidating token.
    This is optional as tokens can be deleted on client side.
    """
    try:
        request.user.auth_token.delete()
        logger.info(f"User logged out: {request.user.username}")
        return Response(
            {'message': 'Successfully logged out.'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return Response(
            {'error': 'Failed to logout.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
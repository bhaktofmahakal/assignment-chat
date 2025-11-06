import axios from 'axios'

/**
 * API Service Module
 * Centralized API communication with Django backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add request interceptor for authentication
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Token ${token}`
  }
  return config
})

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth and redirect to login
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

/**
 * Conversation APIs
 */
export const conversationAPI = {
  /**
   * Get all conversations for user
   */
  getConversations: (params = {}) =>
    apiClient.get('/conversations/', { params }),

  /**
   * Get single conversation with full message history
   */
  getConversation: (id) =>
    apiClient.get(`/conversations/${id}/`),

  /**
   * Create new conversation
   */
  createConversation: (data) =>
    apiClient.post('/conversations/', data),

  /**
   * Update conversation
   */
  updateConversation: (id, data) =>
    apiClient.patch(`/conversations/${id}/`, data),

  /**
   * Delete conversation
   */
  deleteConversation: (id) =>
    apiClient.delete(`/conversations/${id}/`),

  /**
   * End conversation and generate summary
   */
  endConversation: (id, data = {}) =>
    apiClient.post(`/conversations/${id}/end/`, data),

  /**
   * Send message in conversation
   */
  sendMessage: (id, content) =>
    apiClient.post(`/conversations/${id}/send_message/`, { content }),

  /**
   * Get messages in conversation
   */
  getMessages: (id, params = {}) =>
    apiClient.get(`/conversations/${id}/messages/`, { params }),
}

/**
 * Intelligence APIs
 */
export const intelligenceAPI = {
  /**
   * Query past conversations using AI
   */
  queryConversations: (data) =>
    apiClient.post('/intelligence/query/', data),

  /**
   * Get user conversation analytics
   */
  getAnalytics: () =>
    apiClient.get('/intelligence/analytics/'),
}

/**
 * Authentication APIs
 */
export const authAPI = {
  /**
   * Register new user
   */
  register: (data) =>
    apiClient.post('/auth/register/', data),

  /**
   * Login user
   */
  login: (data) =>
    apiClient.post('/auth/login/', data),

  /**
   * Logout user
   */
  logout: () =>
    apiClient.post('/auth/logout/'),

  /**
   * Get current user info
   */
  getCurrentUser: () =>
    apiClient.get('/auth/user/'),
}

/**
 * Health check
 */
export const healthCheck = () =>
  apiClient.get('/health/')

export default apiClient
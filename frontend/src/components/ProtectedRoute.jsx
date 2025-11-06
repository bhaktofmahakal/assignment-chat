import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

/**
 * Protected Route Component
 * Redirects to login if user is not authenticated
 */
function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuthStore()

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return isAuthenticated ? children : <Navigate to="/login" replace />
}

export default ProtectedRoute
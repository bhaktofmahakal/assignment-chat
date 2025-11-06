import React, { useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import Layout from './components/Layout'
import ChatInterface from './pages/ChatInterface'
import ConversationsDashboard from './pages/ConversationsDashboard'
import ConversationIntelligence from './pages/ConversationIntelligence'
import Login from './pages/Login'
import Register from './pages/Register'
import ProtectedRoute from './components/ProtectedRoute'

/**
 * Main App Component
 * Handles routing and authentication state management
 */
function App() {
  const { isAuthenticated, initializeAuth } = useAuthStore()

  useEffect(() => {
    // Initialize authentication on app mount
    initializeAuth()
  }, [initializeAuth])

  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Protected Routes */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout>
                <Navigate to="/chat" replace />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/chat"
          element={
            <ProtectedRoute>
              <Layout>
                <ChatInterface />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/chat/:id"
          element={
            <ProtectedRoute>
              <Layout>
                <ChatInterface />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Layout>
                <ConversationsDashboard />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/intelligence"
          element={
            <ProtectedRoute>
              <Layout>
                <ConversationIntelligence />
              </Layout>
            </ProtectedRoute>
          }
        />

        {/* 404 Not Found */}
        <Route path="*" element={<Navigate to="/chat" replace />} />
      </Routes>
    </Router>
  )
}

export default App
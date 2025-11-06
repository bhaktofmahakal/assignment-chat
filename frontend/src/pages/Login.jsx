import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { authAPI } from '../services/api'

/**
 * Login Page Component
 * Handles user authentication
 */
function Login() {
  const navigate = useNavigate()
  const { login } = useAuthStore()
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      const response = await authAPI.login(formData)
      const { token, user } = response.data

      login(token, user)
      navigate('/chat')
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Card */}
        <div className="bg-slate-700/30 border border-slate-600/30 rounded-2xl shadow-2xl p-8 backdrop-blur">
          {/* Logo */}
          <div className="text-center mb-8">
            <div className="inline-block p-3 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-xl mb-4">
              <span className="text-2xl">💬</span>
            </div>
            <h1 className="text-3xl font-bold text-transparent bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text">
              Chat Portal
            </h1>
            <p className="text-slate-400 mt-2">AI-Powered Conversation Intelligence</p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Username Field */}
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-slate-200 mb-2">
                Username
              </label>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                placeholder="Enter your username"
                required
                className="w-full px-4 py-3 bg-slate-600/50 border border-slate-500/50 text-slate-100 placeholder-slate-400 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all duration-200"
              />
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-slate-200 mb-2">
                Password
              </label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                placeholder="Enter your password"
                required
                className="w-full px-4 py-3 bg-slate-600/50 border border-slate-500/50 text-slate-100 placeholder-slate-400 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all duration-200"
              />
            </div>

            {/* Error Message */}
            {error && (
              <div className="p-4 bg-red-500/10 border border-red-500/30 text-red-300 rounded-lg">
                <p className="text-sm">{error}</p>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full px-4 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-medium rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl"
            >
              {loading ? 'Logging in...' : 'Login'}
            </button>
          </form>

          {/* Demo Credentials */}
          <div className="mt-6 p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
            <p className="text-sm text-blue-300 font-medium mb-3">📋 Demo Credentials:</p>
            <div className="space-y-2">
              <p className="text-sm text-slate-300">
                Username: <code className="bg-slate-600/50 px-2 py-1 rounded text-blue-300 font-mono">demo</code>
              </p>
              <p className="text-sm text-slate-300">
                Password: <code className="bg-slate-600/50 px-2 py-1 rounded text-blue-300 font-mono">demo123</code>
              </p>
            </div>
          </div>

          {/* Registration Link */}
          <div className="mt-6 text-center">
            <p className="text-slate-400 text-sm">
              Don't have an account?{' '}
              <Link to="/register" className="text-blue-400 hover:text-cyan-400 font-medium transition-colors">
                Create one here
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login
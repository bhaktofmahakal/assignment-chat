import React from 'react'
import { useAuthStore } from '../stores/authStore'

/**
 * Header Component - Modern Dark Theme
 * Displays user information and app title
 */
function Header() {
  const { user } = useAuthStore()

  return (
    <header className="bg-gradient-to-r from-slate-800 to-slate-700 border-b border-slate-700/50 shadow-lg">
      <div className="flex items-center justify-between px-8 py-4">
        <div>
          <h2 className="text-2xl font-bold text-transparent bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text">
            AI Chat Portal
          </h2>
          <p className="text-slate-400 text-sm">Intelligent conversation analysis</p>
        </div>

        <div className="flex items-center gap-4">
          {user && (
            <div className="text-right">
              <p className="font-medium text-slate-100">{user.username}</p>
              <p className="text-sm text-slate-400">{user.email}</p>
            </div>
          )}
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center shadow-lg">
            <span className="text-white font-bold text-sm">
              {user?.username?.[0].toUpperCase()}
            </span>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
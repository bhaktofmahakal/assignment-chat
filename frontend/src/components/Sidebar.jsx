import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { MessageCircle, BarChart3, Brain, LogOut, Menu, X } from 'lucide-react'

/**
 * Sidebar Navigation Component - Modern Professional Design
 */
function Sidebar() {
  const location = useLocation()
  const { logout } = useAuthStore()
  const [isOpen, setIsOpen] = useState(true)

  const navigationItems = [
    { label: 'Chat', path: '/chat', icon: MessageCircle },
    { label: 'Dashboard', path: '/dashboard', icon: BarChart3 },
    { label: 'Intelligence', path: '/intelligence', icon: Brain },
  ]

  const isActive = (path) => location.pathname === path || location.pathname.startsWith(path + '/')

  return (
    <aside
      className={`${
        isOpen ? 'w-64' : 'w-20'
      } bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white shadow-2xl transition-all duration-300 flex flex-col border-r border-slate-700`}
    >
      {/* Sidebar Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-700/50">
        {isOpen && (
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-gradient-to-r from-blue-400 to-cyan-400 rounded-full"></div>
            <h1 className="text-lg font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              Chat Portal
            </h1>
          </div>
        )}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="p-2 hover:bg-slate-700/50 rounded-lg transition-all duration-200"
          aria-label="Toggle sidebar"
        >
          {isOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Navigation Menu */}
      <nav className="mt-8 space-y-2 px-3 flex-1">
        {navigationItems.map((item) => {
          const Icon = item.icon
          const active = isActive(item.path)
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 group ${
                active
                  ? 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white shadow-lg'
                  : 'text-slate-300 hover:bg-slate-700/50 hover:text-white'
              }`}
            >
              <Icon size={20} className={`transition-transform duration-200 ${active ? '' : 'group-hover:scale-110'}`} />
              {isOpen && (
                <span className="font-medium text-sm">{item.label}</span>
              )}
            </Link>
          )
        })}
      </nav>

      {/* Logout Button */}
      <div className="p-4 border-t border-slate-700/50">
        <button
          onClick={() => {
            logout()
            window.location.href = '/login'
          }}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 rounded-lg transition-all duration-200 text-white font-medium shadow-lg hover:shadow-xl"
        >
          <LogOut size={18} />
          {isOpen && <span>Logout</span>}
        </button>
      </div>
    </aside>
  )
}

export default Sidebar
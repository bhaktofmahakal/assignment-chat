import React from 'react'
import Sidebar from './Sidebar'
import Header from './Header'

/**
 * Main Layout Component - Modern Dark Theme
 * Wraps pages with navigation sidebar and header
 */
function Layout({ children }) {
  return (
    <div className="flex h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Sidebar Navigation */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Header */}
        <Header />

        {/* Page Content */}
        <main className="flex-1 overflow-auto p-6 sm:p-8">
          <div className="max-w-7xl">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}

export default Layout
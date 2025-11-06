import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Trash2, Eye } from 'lucide-react'
import api from '../services/api'

/**
 * Conversations Dashboard Page
 * Displays list of all conversations with search and management options
 */
function ConversationsDashboard() {
  const navigate = useNavigate()
  const [conversations, setConversations] = useState([])
  const [searchQuery, setSearchQuery] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchConversations()
  }, [])

  const fetchConversations = async () => {
    try {
      setLoading(true)
      setError('')
      const response = await api.get('/conversations/')
      setConversations(response.data.results || response.data)
    } catch (err) {
      setError('Failed to fetch conversations. Please try again.')
      console.error('Error fetching conversations:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleViewConversation = (conversationId) => {
    navigate(`/chat/${conversationId}`)
  }

  const handleDeleteConversation = async (conversationId, e) => {
    e.stopPropagation()
    if (!window.confirm('Are you sure you want to delete this conversation?')) {
      return
    }

    try {
      await api.delete(`/conversations/${conversationId}/`)
      setConversations(conversations.filter(c => c.id !== conversationId))
    } catch (err) {
      console.error('Error deleting conversation:', err)
      setError('Failed to delete conversation.')
    }
  }

  const filteredConversations = conversations.filter(
    (conv) =>
      (conv.title || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (conv.summary || '').toLowerCase().includes(searchQuery.toLowerCase())
  )

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-slate-400">Loading conversations...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 min-h-screen">
      <div>
        <h1 className="text-4xl font-bold text-transparent bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text mb-2">
          Conversations
        </h1>
        <p className="text-slate-400">Browse and manage your past conversations</p>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-300 px-4 py-3 rounded-lg flex items-center gap-2">
          <span>⚠️</span>
          {error}
        </div>
      )}

      <div className="relative">
        <Search className="absolute left-4 top-3.5 text-slate-400" size={20} />
        <input
          type="text"
          placeholder="Search conversations by title or content..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-12 pr-4 py-3 bg-slate-700/50 border border-slate-600/50 text-slate-100 placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
        />
      </div>

      {filteredConversations.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-5xl mb-4">📁</div>
          <p className="text-slate-400 text-lg">
            {searchQuery
              ? 'No conversations match your search.'
              : 'No conversations yet. Start chatting to create one!'}
          </p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredConversations.map((conversation) => (
            <div
              key={conversation.id}
              className="bg-slate-700/30 border border-slate-600/30 rounded-xl p-5 hover:border-slate-500/50 hover:bg-slate-700/50 hover:shadow-xl transition-all duration-300 cursor-pointer group"
              onClick={() => handleViewConversation(conversation.id)}
            >
              <div className="flex items-start justify-between mb-3">
                <h3 className="text-lg font-semibold text-slate-100 line-clamp-2 flex-1 group-hover:text-blue-400 transition-colors">
                  {conversation.title || 'Untitled Conversation'}
                </h3>
                <span
                  className={`text-xs font-semibold px-3 py-1 rounded-full whitespace-nowrap ml-2 ${
                    conversation.status === 'active'
                      ? 'bg-green-500/20 text-green-300 border border-green-500/30'
                      : 'bg-slate-500/20 text-slate-300 border border-slate-500/30'
                  }`}
                >
                  {conversation.status}
                </span>
              </div>

              {conversation.summary && (
                <p className="text-sm text-slate-400 line-clamp-2 mb-4">
                  {conversation.summary}
                </p>
              )}

              <div className="flex items-center justify-between mb-4">
                <div className="text-xs text-slate-500">
                  {formatDate(conversation.created_at)}
                </div>
                {conversation.sentiment_analysis && (
                  <span className="text-xs bg-purple-500/20 text-purple-300 px-2 py-1 rounded-full border border-purple-500/30">
                    {conversation.sentiment_analysis.overall_sentiment}
                  </span>
                )}
              </div>

              <div className="flex gap-2">
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    handleViewConversation(conversation.id)
                  }}
                  className="flex-1 flex items-center justify-center gap-2 bg-blue-600/30 text-blue-300 hover:bg-blue-600/50 hover:text-blue-200 py-2.5 rounded-lg transition-all duration-200 text-sm font-medium border border-blue-500/20 group-hover:border-blue-500/50"
                >
                  <Eye size={16} />
                  View
                </button>
                <button
                  onClick={(e) => handleDeleteConversation(conversation.id, e)}
                  className="p-2.5 text-red-400 hover:bg-red-600/20 hover:text-red-300 rounded-lg transition-all duration-200 border border-red-500/20 hover:border-red-500/50"
                  title="Delete conversation"
                >
                  <Trash2 size={18} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default ConversationsDashboard
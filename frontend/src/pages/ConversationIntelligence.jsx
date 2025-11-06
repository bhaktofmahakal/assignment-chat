import React, { useState } from 'react'
import { Search, Loader } from 'lucide-react'
import api from '../services/api'

/**
 * Conversation Intelligence Page
 * Allows users to query and analyze past conversations
 */
function ConversationIntelligence() {
  const [query, setQuery] = useState('')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [topics, setTopics] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!query.trim()) {
      setError('Please enter a query.')
      return
    }

    try {
      setLoading(true)
      setError('')
      setResults(null)

      const payload = {
        query: query.trim(),
      }

      if (dateFrom) payload.date_from = dateFrom
      if (dateTo) payload.date_to = dateTo
      if (topics) payload.topics = topics.split(',').map(t => t.trim())

      const response = await api.post('/intelligence/query/', payload)
      setResults(response.data)
    } catch (err) {
      setError('Failed to process your query. Please try again.')
      console.error('Error querying conversations:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setQuery('')
    setDateFrom('')
    setDateTo('')
    setTopics('')
    setResults(null)
    setError('')
  }

  return (
    <div className="space-y-6 min-h-screen">
      <div>
        <h1 className="text-4xl font-bold text-transparent bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text mb-2">
          Conversation Intelligence
        </h1>
        <p className="text-slate-400">
          Ask questions about your past conversations and get AI-powered insights
        </p>
      </div>

      <form onSubmit={handleSearch} className="bg-slate-700/30 border border-slate-600/30 rounded-xl p-6 space-y-4 shadow-lg">
        <div>
          <label className="block text-sm font-medium text-slate-200 mb-3">
            Your Question
          </label>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., What topics did I discuss about travel last month? What were the key decisions made?"
            className="w-full px-4 py-3 bg-slate-600/50 border border-slate-500/50 text-slate-100 placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none transition-all duration-200 disabled:opacity-50"
            rows="4"
            disabled={loading}
          />
        </div>

        <div className="grid md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-200 mb-2">
              From Date
            </label>
            <input
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              className="w-full px-4 py-2.5 bg-slate-600/50 border border-slate-500/50 text-slate-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 disabled:opacity-50"
              disabled={loading}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-200 mb-2">
              To Date
            </label>
            <input
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              className="w-full px-4 py-2.5 bg-slate-600/50 border border-slate-500/50 text-slate-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 disabled:opacity-50"
              disabled={loading}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-200 mb-2">
              Topics (comma-separated)
            </label>
            <input
              type="text"
              value={topics}
              onChange={(e) => setTopics(e.target.value)}
              placeholder="e.g., travel, planning, budget"
              className="w-full px-4 py-2.5 bg-slate-600/50 border border-slate-500/50 text-slate-100 placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 disabled:opacity-50"
              disabled={loading}
            />
          </div>
        </div>

        <div className="flex gap-2 pt-2">
          <button
            type="submit"
            disabled={loading}
            className="flex items-center justify-center gap-2 flex-1 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white py-3 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl font-medium"
          >
            {loading ? (
              <>
                <Loader size={20} className="animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Search size={20} />
                Search Conversations
              </>
            )}
          </button>
          <button
            type="button"
            onClick={handleReset}
            disabled={loading}
            className="px-6 py-3 border border-slate-500/30 text-slate-300 rounded-lg hover:bg-slate-600/50 hover:border-slate-500/50 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          >
            Reset
          </button>
        </div>
      </form>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-300 px-4 py-3 rounded-lg flex items-center gap-2">
          <span>⚠️</span>
          {error}
        </div>
      )}

      {results && (
        <div className="bg-slate-700/30 border border-slate-600/30 rounded-xl p-6 space-y-6 shadow-lg">
          <div>
            <h2 className="text-2xl font-bold text-transparent bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text mb-4">
              AI Response
            </h2>
            <p className="text-slate-300 whitespace-pre-wrap leading-relaxed">{results.ai_response}</p>
          </div>

          {results.relevant_conversations && results.relevant_conversations.length > 0 && (
            <div>
              <h3 className="text-xl font-semibold text-slate-100 mb-2">
                Relevant Conversations ({results.results_count})
              </h3>
              <div className="text-sm text-slate-400 mb-4">
                Found in {results.execution_time.toFixed(2)} seconds
              </div>
              <div className="space-y-3">
                {results.relevant_conversations.map((result, idx) => {
                  const conv = result.conversation
                  return (
                    <div
                      key={idx}
                      className="border border-slate-600/30 bg-slate-600/20 rounded-lg p-4 hover:bg-slate-600/40 hover:border-slate-500/50 transition-all duration-200 cursor-pointer"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="font-medium text-slate-100 hover:text-blue-400 transition-colors">
                          {conv.title || 'Untitled Conversation'}
                        </h4>
                        {result.similarity_score && (
                          <span className="text-xs bg-green-500/20 text-green-300 px-3 py-1 rounded-full border border-green-500/30 whitespace-nowrap ml-2">
                            {(result.similarity_score * 100).toFixed(0)}% match
                          </span>
                        )}
                      </div>
                      {result.excerpt && (
                        <p className="text-sm text-slate-400 mb-3 line-clamp-2">{result.excerpt}</p>
                      )}
                      <div className="text-xs text-slate-500 flex items-center gap-2">
                        <span>📅</span>
                        {new Date(conv.started_at).toLocaleDateString()} •
                        <span>💬</span>
                        {result.message_count} messages
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default ConversationIntelligence
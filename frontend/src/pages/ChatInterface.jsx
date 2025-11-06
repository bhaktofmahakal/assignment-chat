import React, { useState, useEffect, useRef } from 'react'
import { useParams } from 'react-router-dom'
import { useConversationStore } from '../stores/conversationStore'
import { conversationAPI } from '../services/api'
import MessageList from '../components/MessageList'
import MessageInput from '../components/MessageInput'

/**
 * Chat Interface Page Component
 * Main chat page with message display and input
 */
function ChatInterface() {
  const { id: conversationId } = useParams()
  const [loading, setLoading] = useState(false)
  const [isCreatingNew, setIsCreatingNew] = useState(!conversationId)
  const [newConvTitle, setNewConvTitle] = useState('')
  const [sendLoading, setSendLoading] = useState(false)
  const [streamingMessageId, setStreamingMessageId] = useState(null)
  const messagesEndRef = useRef(null)

  const {
    currentConversation,
    messages,
    setCurrentConversation,
    setMessages,
    addMessage,
    setError,
  } = useConversationStore()

  // Auto scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Load conversation on mount or when ID changes
  useEffect(() => {
    if (conversationId) {
      loadConversation()
    }
  }, [conversationId])

  const loadConversation = async () => {
    setLoading(true)
    try {
      const response = await conversationAPI.getConversation(conversationId)
      setCurrentConversation(response.data)
      setMessages(response.data.messages || [])
      setIsCreatingNew(false)
    } catch (error) {
      setError('Failed to load conversation')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateConversation = async (e) => {
    e.preventDefault()
    if (!newConvTitle.trim()) return

    setLoading(true)
    try {
      const response = await conversationAPI.createConversation({
        title: newConvTitle,
        description: '',
      })
      setCurrentConversation(response.data)
      setMessages([])
      setNewConvTitle('')
      setIsCreatingNew(false)
    } catch (error) {
      setError('Failed to create conversation')
    } finally {
      setLoading(false)
    }
  }

  const handleSendMessage = async (content) => {
    if (!currentConversation) return

    setSendLoading(true)
    
    // Create optimistic UI update
    const tempUserMessage = {
      id: `temp-${Date.now()}`,
      sender: 'user',
      sender_display: 'User',
      content,
      created_at: new Date().toISOString(),
    }
    addMessage(tempUserMessage)

    try {
      const response = await conversationAPI.sendMessage(currentConversation.id, content)
      
      // Remove temp message and add real ones
      const updatedMessages = messages.filter((msg) => !msg.id.startsWith('temp-'))
      const newUserMessage = response.data.user_message
      const newAiMessage = response.data.ai_message
      
      setMessages([
        ...updatedMessages,
        newUserMessage,
        newAiMessage,
      ])
      
      // Set streaming effect for AI message
      setStreamingMessageId(newAiMessage.id)
      
      // Clear streaming after message is fully displayed
      // Calculate time based on content length
      const streamingTime = newAiMessage.content.length * 15 + 500
      setTimeout(() => {
        setStreamingMessageId(null)
      }, streamingTime)
    } catch (error) {
      // Remove temp message on error
      const updatedMessages = messages.filter((msg) => !msg.id.startsWith('temp-'))
      setMessages(updatedMessages)
      setError('Failed to send message')
      console.error('Error sending message:', error)
    } finally {
      setSendLoading(false)
    }
  }

  const handleEndConversation = async () => {
    if (!currentConversation) return
    if (!window.confirm('End this conversation?')) return

    setLoading(true)
    try {
      await conversationAPI.endConversation(currentConversation.id, {
        generate_summary: true,
      })
      setCurrentConversation(null)
      setMessages([])
      setIsCreatingNew(true)
    } catch (error) {
      setError('Failed to end conversation')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <div className="bg-gradient-to-r from-slate-800 to-slate-700 border-b border-slate-700/50 px-8 py-4 shadow-lg">
        <div className="flex items-center justify-between">
          <div>
            {currentConversation && (
              <>
                <h2 className="text-2xl font-bold text-transparent bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text">
                  {currentConversation.title}
                </h2>
                <p className="text-sm text-slate-400 mt-1">
                  Status: <span className={`font-medium ${
                    currentConversation.status === 'active' 
                      ? 'text-green-400' 
                      : 'text-slate-300'
                  }`}>{currentConversation.status_display}</span>
                </p>
              </>
            )}
            {isCreatingNew && <h2 className="text-2xl font-bold text-transparent bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text">Start a New Conversation</h2>}
          </div>
          {currentConversation && currentConversation.status === 'active' && (
            <button
              onClick={handleEndConversation}
              disabled={loading}
              className="px-6 py-2.5 bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white font-medium rounded-lg transition-all duration-200 disabled:opacity-50 shadow-lg hover:shadow-xl"
            >
              End Conversation
            </button>
          )}
        </div>
      </div>

      {/* Create New Conversation Form */}
      {isCreatingNew && (
        <div className="flex-1 flex items-center justify-center p-8">
          <form onSubmit={handleCreateConversation} className="w-full max-w-md">
            <div className="bg-slate-700/50 border border-slate-600/50 rounded-2xl shadow-2xl p-8 backdrop-blur">
              <h3 className="text-xl font-semibold text-slate-100 mb-6">What would you like to discuss?</h3>
              <input
                type="text"
                value={newConvTitle}
                onChange={(e) => setNewConvTitle(e.target.value)}
                placeholder="Enter conversation topic..."
                className="w-full px-4 py-3 bg-slate-600/50 border border-slate-500/50 text-slate-100 placeholder-slate-400 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none mb-6 transition-all duration-200"
              />
              <button
                type="submit"
                disabled={loading || !newConvTitle.trim()}
                className="w-full px-4 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-medium rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl"
              >
                {loading ? 'Creating...' : 'Start Conversation'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Messages Area */}
      {!isCreatingNew && (
        <>
          <div className="flex-1 overflow-auto p-8 space-y-4">
            {messages.length === 0 ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <div className="text-6xl mb-4">💬</div>
                  <p className="text-slate-400 text-lg">No messages yet. Start the conversation!</p>
                  <p className="text-slate-500 text-sm mt-2">Ask anything and the AI will respond</p>
                </div>
              </div>
            ) : (
              <>
                <MessageList messages={messages} streamingMessageId={streamingMessageId} />
                <div ref={messagesEndRef} />
              </>
            )}
          </div>

          {/* Message Input */}
          {currentConversation && currentConversation.status === 'active' && (
            <div className="bg-gradient-to-t from-slate-900 to-transparent p-8 border-t border-slate-700/50">
              <MessageInput onSendMessage={handleSendMessage} isLoading={sendLoading} />
            </div>
          )}
        </>
      )}

      {loading && !isCreatingNew && (
        <div className="flex items-center justify-center p-4 bg-slate-800/50">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
          <span className="ml-3 text-slate-300">Loading conversation...</span>
        </div>
      )}
    </div>
  )
}

export default ChatInterface
import React, { useState } from 'react'
import { Send, Plus } from 'lucide-react'

/**
 * Message Input Component - Modern Professional Design
 * Handles message composition and submission
 */
function MessageInput({ onSendMessage, isLoading = false }) {
  const [content, setContent] = useState('')
  const [isFocused, setIsFocused] = useState(false)

  const handleSubmit = (e) => {
    e.preventDefault()
    if (content.trim() && !isLoading) {
      onSendMessage(content.trim())
      setContent('')
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey && !isLoading) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className={`rounded-2xl border-2 transition-all duration-200 ${
        isFocused 
          ? 'border-blue-500 bg-slate-700/50' 
          : 'border-slate-600/30 bg-slate-700/30 hover:border-slate-500/50'
      } shadow-lg`}>
        <div className="flex items-end gap-3 p-4">
          <button
            type="button"
            className="flex-shrink-0 p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-600/50 rounded-lg transition-all duration-200"
            title="Add attachment"
          >
            <Plus size={20} />
          </button>
          
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            onKeyPress={handleKeyPress}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder="Ask anything... (Shift+Enter for new line)"
            disabled={isLoading}
            className="flex-1 bg-transparent text-slate-100 placeholder-slate-400 outline-none resize-none max-h-32 text-sm md:text-base disabled:opacity-50"
            rows="1"
          />
          
          <button
            type="submit"
            disabled={isLoading || !content.trim()}
            className="flex-shrink-0 p-2.5 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-lg hover:from-blue-500 hover:to-cyan-500 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl transform hover:scale-105"
            title="Send message (Enter)"
          >
            {isLoading ? (
              <div className="animate-spin">
                <Send size={20} />
              </div>
            ) : (
              <Send size={20} />
            )}
          </button>
        </div>
      </div>
      <p className="text-xs text-slate-400 mt-2 ml-2">
        Press <kbd className="px-1.5 py-0.5 bg-slate-700 rounded text-slate-300 font-mono text-xs">Enter</kbd> to send • <kbd className="px-1.5 py-0.5 bg-slate-700 rounded text-slate-300 font-mono text-xs">Shift + Enter</kbd> for new line
      </p>
    </form>
  )
}

export default MessageInput
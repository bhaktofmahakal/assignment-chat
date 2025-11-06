import React, { useState, useEffect } from 'react'
import { formatDistanceToNow } from 'date-fns'
import { CheckCheck } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

/**
 * Message Bubble Component - Modern Professional Design with Markdown Support
 * Displays individual message with styling, markdown parsing, and streaming effect
 */
function MessageBubble({ message, isStreaming = false }) {
  const isUserMessage = message.sender === 'user'
  const [displayedContent, setDisplayedContent] = useState('')
  const [currentIndex, setCurrentIndex] = useState(0)

  // Streaming effect for AI messages
  useEffect(() => {
    if (isStreaming && !isUserMessage) {
      if (currentIndex < message.content.length) {
        const timer = setTimeout(() => {
          setDisplayedContent(message.content.substring(0, currentIndex + 1))
          setCurrentIndex(currentIndex + 1)
        }, 15) // 15ms per character for smooth streaming effect
        return () => clearTimeout(timer)
      }
    } else {
      // Non-streaming: show full content immediately
      setDisplayedContent(message.content)
      setCurrentIndex(message.content.length)
    }
  }, [message.content, currentIndex, isStreaming, isUserMessage])

  const formattedTime = message.created_at
    ? formatDistanceToNow(new Date(message.created_at), { addSuffix: true })
    : ''

  // Custom markdown components for clean rendering
  const markdownComponents = {
    p: ({ children }) => <p className="mb-3 last:mb-0">{children}</p>,
    strong: ({ children }) => <strong className="font-bold text-slate-100">{children}</strong>,
    em: ({ children }) => <em className="italic text-slate-200">{children}</em>,
    code: ({ inline, children }) =>
      inline ? (
        <code className="bg-slate-600/50 px-2 py-1 rounded text-slate-100 text-xs font-mono">
          {children}
        </code>
      ) : (
        <code className="block bg-slate-600/50 p-3 rounded-lg my-2 text-slate-100 text-xs font-mono overflow-x-auto">
          {children}
        </code>
      ),
    pre: ({ children }) => <pre className="overflow-x-auto">{children}</pre>,
    blockquote: ({ children }) => (
      <blockquote className="border-l-4 border-blue-500 pl-4 py-1 my-2 italic text-slate-300">
        {children}
      </blockquote>
    ),
    h1: ({ children }) => <h1 className="text-lg font-bold mt-4 mb-2 text-slate-100">{children}</h1>,
    h2: ({ children }) => <h2 className="text-base font-bold mt-3 mb-2 text-slate-100">{children}</h2>,
    h3: ({ children }) => <h3 className="text-sm font-bold mt-2 mb-1 text-slate-100">{children}</h3>,
    ul: ({ children }) => <ul className="list-disc pl-6 my-2 space-y-1">{children}</ul>,
    ol: ({ children }) => <ol className="list-decimal pl-6 my-2 space-y-1">{children}</ol>,
    li: ({ children }) => <li className="text-slate-100">{children}</li>,
    a: ({ href, children }) => (
      <a 
        href={href} 
        target="_blank" 
        rel="noopener noreferrer"
        className="text-blue-400 hover:text-blue-300 underline"
      >
        {children}
      </a>
    ),
  }

  return (
    <div className={`flex gap-3 animate-fade-in ${isUserMessage ? 'justify-end' : 'justify-start'}`}>
      {!isUserMessage && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-lg">
          <span className="text-xs font-bold text-white">AI</span>
        </div>
      )}
      <div className="flex flex-col gap-2">
        <div
          className={`px-4 py-3 rounded-2xl shadow-md transition-all duration-200 hover:shadow-lg ${
            isUserMessage
              ? 'bg-gradient-to-br from-blue-600 to-blue-700 text-white rounded-br-none max-w-xs lg:max-w-2xl'
              : 'bg-slate-700 text-slate-50 rounded-bl-none border border-slate-600/50 max-w-xs lg:max-w-2xl'
          }`}
        >
          <div className="break-words text-sm md:text-base leading-relaxed">
            {isUserMessage ? (
              // User messages: plain text without markdown parsing
              <p className="whitespace-pre-wrap">{message.content}</p>
            ) : (
              // AI messages: parse markdown and show streaming effect
              <ReactMarkdown 
                remarkPlugins={[remarkGfm]}
                components={markdownComponents}
              >
                {displayedContent}
              </ReactMarkdown>
            )}
          </div>

          {/* Cursor indicator for streaming messages */}
          {isStreaming && !isUserMessage && currentIndex < message.content.length && (
            <span className="inline-block w-2 h-4 ml-1 bg-slate-400 animate-pulse" />
          )}

          <div className={`flex items-center gap-1.5 mt-3 text-xs ${isUserMessage ? 'text-blue-100' : 'text-slate-400'}`}>
            {formattedTime}
            {isUserMessage && <CheckCheck size={14} />}
          </div>
        </div>
      </div>
    </div>
  )
}

export default MessageBubble
import React from 'react'
import MessageBubble from './MessageBubble'

/**
 * Message List Component
 * Displays all messages in a conversation with streaming support
 */
function MessageList({ messages = [], streamingMessageId = null }) {
  return (
    <div className="space-y-4">
      {messages.map((message) => (
        <MessageBubble 
          key={message.id} 
          message={message}
          isStreaming={streamingMessageId === message.id}
        />
      ))}
    </div>
  )
}

export default MessageList
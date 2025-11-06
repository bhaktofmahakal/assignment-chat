import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import MessageBubble from '../src/components/MessageBubble'

/**
 * Test suite for Markdown rendering and streaming functionality
 * Validates that AI responses properly parse markdown and stream text
 */

describe('MessageBubble Component - Markdown & Streaming', () => {
  
  describe('Markdown Parsing', () => {
    it('should render bold text from markdown', async () => {
      const message = {
        id: '1',
        sender: 'ai',
        content: 'This is **bold text** in a response',
        created_at: new Date().toISOString(),
      }
      
      render(<MessageBubble message={message} isStreaming={false} />)
      
      await waitFor(() => {
        const boldElement = screen.getByText('bold text')
        expect(boldElement.tagName).toBe('STRONG')
      })
    })

    it('should render italic text from markdown', async () => {
      const message = {
        id: '2',
        sender: 'ai',
        content: 'This is *italic text* in a response',
        created_at: new Date().toISOString(),
      }
      
      render(<MessageBubble message={message} isStreaming={false} />)
      
      await waitFor(() => {
        const emElement = screen.getByText('italic text')
        expect(emElement.tagName).toBe('EM')
      })
    })

    it('should render code blocks from markdown', async () => {
      const message = {
        id: '3',
        sender: 'ai',
        content: 'Here is a code block:\n\n```javascript\nconst x = 5\n```',
        created_at: new Date().toISOString(),
      }
      
      render(<MessageBubble message={message} isStreaming={false} />)
      
      await waitFor(() => {
        expect(screen.getByText(/const x = 5/)).toBeInTheDocument()
      })
    })

    it('should render inline code from markdown', async () => {
      const message = {
        id: '4',
        sender: 'ai',
        content: 'Use the `console.log()` function',
        created_at: new Date().toISOString(),
      }
      
      render(<MessageBubble message={message} isStreaming={false} />)
      
      await waitFor(() => {
        expect(screen.getByText(/console.log/)).toBeInTheDocument()
      })
    })

    it('should render lists from markdown', async () => {
      const message = {
        id: '5',
        sender: 'ai',
        content: '- Item 1\n- Item 2\n- Item 3',
        created_at: new Date().toISOString(),
      }
      
      render(<MessageBubble message={message} isStreaming={false} />)
      
      await waitFor(() => {
        expect(screen.getByText('Item 1')).toBeInTheDocument()
        expect(screen.getByText('Item 2')).toBeInTheDocument()
        expect(screen.getByText('Item 3')).toBeInTheDocument()
      })
    })

    it('should render headings from markdown', async () => {
      const message = {
        id: '6',
        sender: 'ai',
        content: '## This is a heading\nSome content below',
        created_at: new Date().toISOString(),
      }
      
      render(<MessageBubble message={message} isStreaming={false} />)
      
      await waitFor(() => {
        const heading = screen.getByText('This is a heading')
        expect(heading.tagName).toBe('H2')
      })
    })
  })

  describe('Streaming Effect', () => {
    it('should progressively display content when streaming', async () => {
      vi.useFakeTimers()
      
      const message = {
        id: '7',
        sender: 'ai',
        content: 'Hello world',
        created_at: new Date().toISOString(),
      }
      
      const { container } = render(<MessageBubble message={message} isStreaming={true} />)
      
      // Initially nothing is visible
      await waitFor(() => {
        // After some time, text should start appearing
        vi.advanceTimersByTime(100)
        const textContent = container.textContent
        expect(textContent.length).toBeGreaterThan(0)
      })
      
      vi.useRealTimers()
    })

    it('should show cursor indicator while streaming', async () => {
      vi.useFakeTimers()
      
      const message = {
        id: '8',
        sender: 'ai',
        content: 'Test content that is streaming',
        created_at: new Date().toISOString(),
      }
      
      const { container } = render(<MessageBubble message={message} isStreaming={true} />)
      
      // Advance time but not beyond full content
      vi.advanceTimersByTime(100)
      
      // Look for the blinking cursor (pulse animation)
      const cursor = container.querySelector('.animate-pulse')
      expect(cursor).toBeInTheDocument()
      
      vi.useRealTimers()
    })

    it('should not show cursor when streaming is done', async () => {
      const message = {
        id: '9',
        sender: 'ai',
        content: 'Complete message',
        created_at: new Date().toISOString(),
      }
      
      const { container } = render(<MessageBubble message={message} isStreaming={false} />)
      
      // When not streaming, cursor should not be visible
      const cursor = container.querySelector('.animate-pulse')
      expect(cursor).not.toBeInTheDocument()
    })
  })

  describe('User Messages', () => {
    it('should not parse markdown for user messages', async () => {
      const message = {
        id: '10',
        sender: 'user',
        content: 'This **should not** be parsed as markdown',
        created_at: new Date().toISOString(),
      }
      
      render(<MessageBubble message={message} isStreaming={false} />)
      
      await waitFor(() => {
        // Should be plain text, not parsed
        expect(screen.getByText(/\*\*should not\*\*/)).toBeInTheDocument()
      })
    })

    it('should display user message styling', async () => {
      const message = {
        id: '11',
        sender: 'user',
        content: 'User message',
        created_at: new Date().toISOString(),
      }
      
      const { container } = render(<MessageBubble message={message} isStreaming={false} />)
      
      await waitFor(() => {
        const messageDiv = container.querySelector('.from-blue-600')
        expect(messageDiv).toBeInTheDocument()
      })
    })
  })

  describe('Complex Markdown Scenarios', () => {
    it('should handle mixed markdown elements', async () => {
      const message = {
        id: '12',
        sender: 'ai',
        content: `## Overview
This is a **comprehensive** solution for your problem.

### Key Points:
- Use *proper* formatting
- \`const result = calculate()\`
- See the [documentation](https://example.com)`,
        created_at: new Date().toISOString(),
      }
      
      render(<MessageBubble message={message} isStreaming={false} />)
      
      await waitFor(() => {
        expect(screen.getByText('Overview')).toBeInTheDocument()
        expect(screen.getByText('comprehensive')).toBeInTheDocument()
      })
    })
  })
})
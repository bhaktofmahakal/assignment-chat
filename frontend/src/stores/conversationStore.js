import { create } from 'zustand'

/**
 * Conversation Store
 * Manages conversation state and active chat data
 */
export const useConversationStore = create((set, get) => ({
  // State
  conversations: [],
  currentConversation: null,
  messages: [],
  loading: false,
  error: null,

  // Actions
  /**
   * Set conversations list
   */
  setConversations: (conversations) =>
    set({ conversations }),

  /**
   * Set current active conversation
   */
  setCurrentConversation: (conversation) =>
    set({ currentConversation: conversation }),

  /**
   * Set messages for current conversation
   */
  setMessages: (messages) =>
    set({ messages }),

  /**
   * Add message to current conversation
   */
  addMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, message],
    })),

  /**
   * Add conversation to list
   */
  addConversation: (conversation) =>
    set((state) => ({
      conversations: [conversation, ...state.conversations],
    })),

  /**
   * Update conversation in list
   */
  updateConversation: (conversationId, updates) =>
    set((state) => ({
      conversations: state.conversations.map((conv) =>
        conv.id === conversationId ? { ...conv, ...updates } : conv
      ),
      currentConversation:
        state.currentConversation?.id === conversationId
          ? { ...state.currentConversation, ...updates }
          : state.currentConversation,
    })),

  /**
   * Remove conversation from list
   */
  removeConversation: (conversationId) =>
    set((state) => ({
      conversations: state.conversations.filter((conv) => conv.id !== conversationId),
    })),

  /**
   * Clear current conversation
   */
  clearCurrentConversation: () =>
    set({
      currentConversation: null,
      messages: [],
    }),

  /**
   * Set loading state
   */
  setLoading: (loading) =>
    set({ loading }),

  /**
   * Set error state
   */
  setError: (error) =>
    set({ error }),

  /**
   * Clear error
   */
  clearError: () =>
    set({ error: null }),

  /**
   * Reset store
   */
  reset: () =>
    set({
      conversations: [],
      currentConversation: null,
      messages: [],
      loading: false,
      error: null,
    }),
}))
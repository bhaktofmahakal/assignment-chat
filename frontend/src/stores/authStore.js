import { create } from 'zustand'

/**
 * Authentication Store
 * Manages user authentication state
 */
export const useAuthStore = create((set) => ({
  // State
  isAuthenticated: false,
  user: null,
  token: null,
  loading: true,

  // Actions
  /**
   * Initialize authentication from localStorage
   */
  initializeAuth: () => {
    const token = localStorage.getItem('auth_token')
    const user = localStorage.getItem('user')
    
    if (token && user) {
      set({
        isAuthenticated: true,
        token,
        user: JSON.parse(user),
        loading: false,
      })
    } else {
      set({ loading: false })
    }
  },

  /**
   * Login user
   */
  login: (token, user) => {
    localStorage.setItem('auth_token', token)
    localStorage.setItem('user', JSON.stringify(user))
    set({
      isAuthenticated: true,
      token,
      user,
    })
  },

  /**
   * Logout user
   */
  logout: () => {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user')
    set({
      isAuthenticated: false,
      user: null,
      token: null,
    })
  },

  /**
   * Update user info
   */
  setUser: (user) => {
    localStorage.setItem('user', JSON.stringify(user))
    set({ user })
  },
}))
import { defineStore } from 'pinia'
import { getCurrentUser, login, register } from '@/api/auth'
import type { LoginPayload, RegisterPayload, UserInfo } from '@/types/auth'

interface AuthState {
  token: string
  user: UserInfo | null
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    token: localStorage.getItem('access_token') || '',
    user: null,
  }),
  getters: {
    isLoggedIn: (state) => Boolean(state.token),
    isAdmin: (state) => state.user?.role === 'admin',
  },
  actions: {
    async login(payload: LoginPayload) {
      const result = await login(payload)
      this.token = result.access_token
      this.user = result.user
      localStorage.setItem('access_token', result.access_token)
    },
    async register(payload: RegisterPayload) {
      return register(payload)
    },
    async fetchCurrentUser() {
      if (!this.token) return
      this.user = await getCurrentUser()
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('access_token')
    },
  },
})

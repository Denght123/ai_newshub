import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useAuthStore } from './auth'
import { getCurrentUser, login } from '@/api/auth'

vi.mock('@/api/auth', () => ({
  login: vi.fn(),
  register: vi.fn(),
  getCurrentUser: vi.fn(),
}))

describe('auth store', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('stores token after login', async () => {
    vi.mocked(login).mockResolvedValue({
      access_token: 'test-token',
      token_type: 'bearer',
      user: {
        id: 1,
        username: 'tester',
        email: 'tester@example.com',
        role: 'user',
      },
    })

    const store = useAuthStore()
    await store.login({ username_or_email: 'tester', password: '123456' })

    expect(store.isLoggedIn).toBe(true)
    expect(store.user?.username).toBe('tester')
    expect(localStorage.getItem('access_token')).toBe('test-token')
  })

  it('clears token on logout', () => {
    localStorage.setItem('access_token', 'old-token')
    const store = useAuthStore()

    store.logout()

    expect(store.isLoggedIn).toBe(false)
    expect(localStorage.getItem('access_token')).toBeNull()
  })

  it('loads current user when token exists', async () => {
    localStorage.setItem('access_token', 'token')
    vi.mocked(getCurrentUser).mockResolvedValue({
      id: 2,
      username: 'admin',
      email: 'admin@example.com',
      role: 'admin',
    })

    const store = useAuthStore()
    await store.fetchCurrentUser()

    expect(store.isAdmin).toBe(true)
  })
})

import { apiGet, apiPost } from './request'
import type { LoginPayload, LoginResult, RegisterPayload, UserInfo } from '@/types/auth'

export function register(payload: RegisterPayload) {
  return apiPost<UserInfo>('/auth/register', payload)
}

export function login(payload: LoginPayload) {
  return apiPost<LoginResult>('/auth/login', payload)
}

export function getCurrentUser() {
  return apiGet<UserInfo>('/auth/me')
}

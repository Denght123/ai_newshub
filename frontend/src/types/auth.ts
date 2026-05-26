export type UserRole = 'user' | 'admin'

export interface UserInfo {
  id: number
  username: string
  email: string
  nickname?: string | null
  role: UserRole
  is_active?: boolean
  created_at?: string
}

export interface LoginPayload {
  username_or_email: string
  password: string
}

export interface RegisterPayload {
  username: string
  email: string
  password: string
}

export interface LoginResult {
  access_token: string
  token_type: string
  user: UserInfo
}

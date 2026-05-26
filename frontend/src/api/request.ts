import axios from 'axios'
import { ElMessage } from 'element-plus'
import type { ApiResponse } from '@/types/common'
import { isMockMode, mockRequest } from './mock'

const baseURL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

export const http = axios.create({
  baseURL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.set('Authorization', `Bearer ${token}`)
  }
  return config
})

http.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status
    const message = error.response?.data?.message || error.message || '请求失败，请稍后重试'

    if (status === 401) {
      localStorage.removeItem('access_token')
      if (window.location.pathname !== '/login') {
        ElMessage.warning('登录已失效，请重新登录')
        window.location.href = '/login'
      }
    }

    return Promise.reject(new Error(message))
  },
)

export async function apiGet<T>(url: string, params?: Record<string, unknown>): Promise<T> {
  if (isMockMode()) return mockRequest<T>('GET', url, undefined, params)
  const response = await http.get<ApiResponse<T>>(url, { params })
  return unwrapResponse(response.data)
}

export async function apiPost<T>(url: string, data?: unknown): Promise<T> {
  if (isMockMode()) return mockRequest<T>('POST', url, data)
  const response = await http.post<ApiResponse<T>>(url, data)
  return unwrapResponse(response.data)
}

export async function apiPut<T>(url: string, data?: unknown): Promise<T> {
  if (isMockMode()) return mockRequest<T>('PUT', url, data)
  const response = await http.put<ApiResponse<T>>(url, data)
  return unwrapResponse(response.data)
}

export async function apiPatch<T>(url: string, data?: unknown): Promise<T> {
  if (isMockMode()) return mockRequest<T>('PATCH', url, data)
  const response = await http.patch<ApiResponse<T>>(url, data)
  return unwrapResponse(response.data)
}

export async function apiDelete<T>(url: string): Promise<T> {
  if (isMockMode()) return mockRequest<T>('DELETE', url)
  const response = await http.delete<ApiResponse<T>>(url)
  return unwrapResponse(response.data)
}

function unwrapResponse<T>(response: ApiResponse<T>): T {
  if (response.code !== 200) {
    throw new Error(response.message || '接口返回异常')
  }
  return response.data
}

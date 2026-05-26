export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export interface PageResult<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  pages: number
}

export interface SelectOption {
  label: string
  value: string | number | boolean
}

export type Order = 'asc' | 'desc'

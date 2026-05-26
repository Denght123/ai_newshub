export interface CategoryItem {
  id: number
  name: string
  description?: string | null
  sort_order: number
  is_active: boolean
}

export interface CategoryPayload {
  name: string
  description?: string
  sort_order: number
  is_active?: boolean
}

export interface TagItem {
  id: number
  name: string
}

export interface TagPayload {
  name: string
}

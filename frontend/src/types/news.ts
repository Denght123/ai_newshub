import type { CategoryItem, TagItem } from './taxonomy'

export type NewsStatus = 'unread' | 'read' | 'added_to_topic' | 'ignored'

export interface NewsPayload {
  title: string
  source_name?: string
  source_url?: string
  summary?: string
  content?: string
  category_id?: number | null
  tag_ids?: number[]
  status?: NewsStatus
  importance_score?: number
  heat_score?: number
  publish_time?: string
}

export interface NewsItem {
  id: number
  title: string
  source_name?: string | null
  source_url?: string | null
  summary?: string | null
  content?: string | null
  category?: Pick<CategoryItem, 'id' | 'name'> | null
  tags?: TagItem[]
  status: NewsStatus
  importance_score: number
  heat_score: number
  is_favorite: boolean
  publish_time?: string | null
  created_at?: string
  updated_at?: string
  created_by?: {
    id: number
    username: string
  }
}

export interface NewsListParams {
  page: number
  page_size: number
  keyword?: string
  category_id?: number
  status?: NewsStatus
  is_favorite?: boolean
  order_by?: 'created_at' | 'publish_time' | 'heat_score' | 'importance_score'
  order?: 'asc' | 'desc'
}

export interface FavoritePayload {
  is_favorite: boolean
}

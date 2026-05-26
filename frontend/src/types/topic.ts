import type { CategoryItem } from './taxonomy'

export type TopicStatus = 'pending' | 'selected' | 'writing' | 'published' | 'abandoned'

export interface TopicPayload {
  news_id?: number | null
  title: string
  angle?: string
  recommended_title?: string
  reason?: string
  target_reader?: string
  category_id?: number | null
  status?: TopicStatus
  value_score?: number
  difficulty_score?: number
  traffic_score?: number
  deadline?: string
}

export interface TopicItem {
  id: number
  news_id?: number | null
  news?: {
    id: number
    title: string
  } | null
  title: string
  angle?: string | null
  recommended_title?: string | null
  reason?: string | null
  target_reader?: string | null
  category?: Pick<CategoryItem, 'id' | 'name'> | null
  status: TopicStatus
  value_score: number
  difficulty_score: number
  traffic_score: number
  deadline?: string | null
  created_at?: string
  updated_at?: string
}

export interface TopicListParams {
  page: number
  page_size: number
  keyword?: string
  category_id?: number
  status?: TopicStatus
  order_by?: 'created_at' | 'deadline' | 'value_score' | 'traffic_score' | 'difficulty_score'
  order?: 'asc' | 'desc'
}

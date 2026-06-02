import type { CategoryItem } from './taxonomy'

export type AIDigestSourceProfile = 'balanced' | 'minimal' | 'official_first' | 'community_hot'
export type AIDigestCategoryStrategy = 'match_existing' | 'fixed' | 'none'
export type AIDigestRunStatus = 'reserved' | 'queued' | 'running' | 'completed' | 'failed'

export interface AIDigestRunPayload {
  skill_name: string
  llm_provider: string
  api_base_url: string
  api_key?: string
  model: string
  time_window_hours: number
  max_items: number
  source_profile: AIDigestSourceProfile
  category_strategy: AIDigestCategoryStrategy
  category_ids: number[]
  auto_create_missing_categories: boolean
  create_topics: boolean
  dry_run: boolean
  prompt_note?: string
}

export interface AIDigestPreviewItem {
  title: string
  source_name?: string
  source_url?: string
  matched_category?: Pick<CategoryItem, 'id' | 'name'> | null
  importance_score?: number
  heat_score?: number
  one_line_summary?: string
}

export interface AIDigestRunResult {
  run_id: string
  status: AIDigestRunStatus
  message: string
  received_items: number
  created_news_count: number
  created_topic_count: number
  skipped_count: number
  failed_sources: string[]
  preview_items: AIDigestPreviewItem[]
  config_summary?: {
    current_user_id: number
    skill_name: string
    llm_provider: string
    api_base_url: string
    model: string
    time_window_hours: number
    max_items: number
    source_profile: string
    category_strategy: string
    matched_category_count: number
    auto_create_missing_categories: boolean
    create_topics: boolean
    dry_run: boolean
  }
}

import type { NewsStatus } from './news'
import type { TopicStatus } from './topic'

export interface DashboardRecentNews {
  id: number
  title: string
  status: NewsStatus
  created_at: string
}

export interface DashboardRecentTopic {
  id: number
  title: string
  status: TopicStatus
  created_at: string
}

export interface DashboardOverview {
  news_total: number
  unread_news_total: number
  favorite_news_total: number
  topic_total: number
  pending_topic_total: number
  writing_topic_total: number
  published_topic_total: number
  recent_news: DashboardRecentNews[]
  recent_topics: DashboardRecentTopic[]
}

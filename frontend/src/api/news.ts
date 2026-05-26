import { apiDelete, apiGet, apiPatch, apiPost, apiPut } from './request'
import type { PageResult } from '@/types/common'
import type { FavoritePayload, NewsItem, NewsListParams, NewsPayload } from '@/types/news'
import type { TopicItem, TopicPayload } from '@/types/topic'

export function getNewsList(params: NewsListParams) {
  return apiGet<PageResult<NewsItem>>('/news', params as unknown as Record<string, unknown>)
}

export function getNewsDetail(newsId: number) {
  return apiGet<NewsItem>(`/news/${newsId}`)
}

export function createNews(payload: NewsPayload) {
  return apiPost<NewsItem>('/news', payload)
}

export function updateNews(newsId: number, payload: NewsPayload) {
  return apiPut<NewsItem>(`/news/${newsId}`, payload)
}

export function deleteNews(newsId: number) {
  return apiDelete<null>(`/news/${newsId}`)
}

export function updateNewsFavorite(newsId: number, payload: FavoritePayload) {
  return apiPatch<Pick<NewsItem, 'id' | 'is_favorite'>>(`/news/${newsId}/favorite`, payload)
}

export function createTopicFromNews(newsId: number, payload: TopicPayload) {
  return apiPost<TopicItem>(`/news/${newsId}/to-topic`, payload)
}

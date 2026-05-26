import { apiDelete, apiGet, apiPatch, apiPost, apiPut } from './request'
import type { PageResult } from '@/types/common'
import type { TopicItem, TopicListParams, TopicPayload, TopicStatus } from '@/types/topic'

export function getTopicList(params: TopicListParams) {
  return apiGet<PageResult<TopicItem>>('/topics', params as unknown as Record<string, unknown>)
}

export function getTopicDetail(topicId: number) {
  return apiGet<TopicItem>(`/topics/${topicId}`)
}

export function createTopic(payload: TopicPayload) {
  return apiPost<TopicItem>('/topics', payload)
}

export function updateTopic(topicId: number, payload: TopicPayload) {
  return apiPut<TopicItem>(`/topics/${topicId}`, payload)
}

export function updateTopicStatus(topicId: number, status: TopicStatus) {
  return apiPatch<Pick<TopicItem, 'id' | 'status'>>(`/topics/${topicId}/status`, { status })
}

export function deleteTopic(topicId: number) {
  return apiDelete<null>(`/topics/${topicId}`)
}

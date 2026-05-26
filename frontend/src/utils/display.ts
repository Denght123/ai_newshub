import type { NewsStatus } from '@/types/news'
import type { TopicStatus } from '@/types/topic'

export const newsStatusText: Record<NewsStatus, string> = {
  unread: '待阅读',
  read: '已阅读',
  added_to_topic: '已加选题',
  ignored: '已忽略',
}

export const topicStatusText: Record<TopicStatus, string> = {
  pending: '待评估',
  selected: '已选中',
  writing: '写作中',
  published: '已发布',
  abandoned: '已放弃',
}

export function formatDate(value?: string | null) {
  if (!value) return '-'
  return new Date(value).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function toDateTimeInputValue(value?: string | null) {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  const offset = date.getTimezoneOffset() * 60000
  return new Date(date.getTime() - offset).toISOString().slice(0, 16)
}

export function toApiDateTime(value?: string) {
  if (!value) return undefined
  return new Date(value).toISOString()
}

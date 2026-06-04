import { apiDelete, apiGet, apiPost } from './request'
import { isMockMode } from './mock'
import type {
  DailyDigestRunPayload,
  DailyDigestRunResult,
  KnowledgeDocumentDetail,
  KnowledgeDocumentItem,
  MatchedChunk,
  RagChatPayload,
  RagCitation,
  RagChatSession,
  RagChatSessionDetail,
  RagChatResult,
} from '@/types/rag'
import type { PageResult } from '@/types/common'

const baseURL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

export interface StreamDonePayload {
  session_id?: number
  session_title?: string
  citations?: RagCitation[]
  matched_chunks?: MatchedChunk[]
}

export function createDailyDigestRun(payload: DailyDigestRunPayload) {
  return apiPost<DailyDigestRunResult>('/daily-digest/runs', payload, {
    timeout: 300000,
  })
}

export function getKnowledgeDocuments(params: {
  digest_date?: string
  keyword?: string
  page?: number
  page_size?: number
}) {
  return apiGet<PageResult<KnowledgeDocumentItem>>('/knowledge/documents', params)
}

export function getKnowledgeDocumentDetail(documentId: number) {
  return apiGet<KnowledgeDocumentDetail>(`/knowledge/documents/${documentId}`)
}

export function askRagChat(payload: RagChatPayload) {
  return apiPost<RagChatResult>('/rag-chat/ask', payload, {
    timeout: 120000,
  })
}

export function getRagChatSessions() {
  return apiGet<RagChatSession[]>('/rag-chat/sessions')
}

export function getRagChatSessionDetail(sessionId: number) {
  return apiGet<RagChatSessionDetail>(`/rag-chat/sessions/${sessionId}`)
}

export function deleteRagChatSession(sessionId: number) {
  return apiDelete<null>(`/rag-chat/sessions/${sessionId}`)
}

export async function streamRagChat(
  payload: RagChatPayload,
  onDelta: (content: string) => void,
  onDone?: (data?: StreamDonePayload) => void,
) {
  if (isMockMode()) {
    const result = await askRagChat(payload)
    const demoParts = result.answer.match(/[\s\S]{1,18}/g) || [result.answer]

    for (const part of demoParts) {
      await new Promise((resolve) => window.setTimeout(resolve, 180))
      onDelta(part)
    }
    onDone?.({
      session_id: result.session_id,
      session_title: result.session_title,
      citations: result.citations,
      matched_chunks: result.matched_chunks,
    })
    return
  }

  // 流式接口不能直接用 Axios，这里用浏览器原生 fetch 读取 ReadableStream。
  const token = localStorage.getItem('access_token')
  const response = await fetch(`${baseURL}/rag-chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok || !response.body) {
    throw new Error('流式问答请求失败')
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const events = buffer.split('\n\n')
    buffer = events.pop() || ''

    for (const event of events) {
      const line = event
        .split('\n')
        .find((item) => item.startsWith('data: '))
      if (!line) continue

      const payloadText = line.replace('data: ', '')
      const data = JSON.parse(payloadText) as { type: string; content?: string } & StreamDonePayload
      if (data.type === 'delta' && data.content) onDelta(data.content)
      if (data.type === 'done') onDone?.(data)
    }
  }
}

import { apiGet, apiPost } from './request'
import { isMockMode } from './mock'
import { getLocalDateString } from '@/utils/date'
import type {
  DailyDigestRunPayload,
  DailyDigestRunResult,
  KnowledgeDocumentDetail,
  KnowledgeDocumentItem,
  MatchedChunk,
  RagChatPayload,
  RagCitation,
  RagChatResult,
} from '@/types/rag'
import type { PageResult } from '@/types/common'

const baseURL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

interface StreamDonePayload {
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

export async function streamRagChat(
  payload: RagChatPayload,
  onDelta: (content: string) => void,
  onDone?: (data?: StreamDonePayload) => void,
) {
  if (isMockMode()) {
    const demoParts = [
      '演示模式：我会先从知识库里检索日期和关键词，',
      '再把命中的片段交给大模型组织回答。',
      `你当前的问题是：${payload.question}`,
    ]
    for (const part of demoParts) {
      await new Promise((resolve) => window.setTimeout(resolve, 180))
      onDelta(part)
    }
    onDone?.({
      citations: [
        {
          document_id: 1,
          title: '示例知识文档：等待后端入库逻辑接入',
          source_name: 'Reserved Source',
          digest_date: payload.date_from || getLocalDateString(),
        },
      ],
      matched_chunks: [
        {
          chunk_id: 1,
          document_id: 1,
          chunk_text: '这里会显示后端 RAG 检索命中的知识片段。',
          score: 0.82,
        },
      ],
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

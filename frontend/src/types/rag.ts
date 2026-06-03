export interface LLMConfigPayload {
  api_base_url?: string
  api_key?: string
  model?: string
}

export interface DailyDigestRunPayload {
  digest_date?: string
  max_items: number
  dry_run: boolean
  llm_config: LLMConfigPayload
}

export interface DailyDigestPreviewItem {
  title: string
  summary?: string
  source_name?: string
  source_url?: string
  published_at?: string
  credibility: string
}

export interface DailyDigestRunResult {
  run_id: string
  status: string
  digest_date: string
  message: string
  collected_count: number
  document_count: number
  chunk_count: number
  failed_sources: string[]
  preview_items: DailyDigestPreviewItem[]
}

export interface KnowledgeDocumentItem {
  id: number
  title: string
  summary?: string
  source_name?: string
  source_url?: string
  published_at?: string
  digest_date: string
  credibility: string
}

export interface KnowledgeChunk {
  id: number
  chunk_index: number
  chunk_text: string
}

export interface KnowledgeDocumentDetail extends KnowledgeDocumentItem {
  content?: string
  chunks: KnowledgeChunk[]
}

export interface RagChatPayload {
  question: string
  date_from?: string
  date_to?: string
  top_k: number
}

export interface RagCitation {
  document_id?: number
  title: string
  source_name?: string
  source_url?: string
  digest_date?: string
}

export interface MatchedChunk {
  chunk_id?: number
  document_id?: number
  chunk_text: string
  score?: number
}

export interface RagChatResult {
  answer: string
  citations: RagCitation[]
  matched_chunks: MatchedChunk[]
}

import { apiPost } from './request'
import type { AIDigestRunPayload, AIDigestRunResult } from '@/types/aiDigest'

export function runAIDigestImport(payload: AIDigestRunPayload) {
  return apiPost<AIDigestRunResult>('/ai-digest/runs', payload, {
    timeout: 120000,
  })
}

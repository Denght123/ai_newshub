import { apiGet } from './request'

export interface HealthResult {
  status: string
  service: string
}

export function getHealth() {
  return apiGet<HealthResult>('/health')
}

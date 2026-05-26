import { apiGet } from './request'
import type { DashboardOverview } from '@/types/dashboard'

export function getDashboardOverview() {
  return apiGet<DashboardOverview>('/dashboard/overview')
}

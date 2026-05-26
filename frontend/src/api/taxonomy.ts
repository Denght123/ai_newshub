import { apiDelete, apiGet, apiPost, apiPut } from './request'
import type { CategoryItem, CategoryPayload, TagItem, TagPayload } from '@/types/taxonomy'

export function getCategories(onlyActive = false) {
  return apiGet<CategoryItem[]>('/categories', { only_active: onlyActive })
}

export function createCategory(payload: CategoryPayload) {
  return apiPost<CategoryItem>('/categories', payload)
}

export function updateCategory(categoryId: number, payload: CategoryPayload) {
  return apiPut<CategoryItem>(`/categories/${categoryId}`, payload)
}

export function deleteCategory(categoryId: number) {
  return apiDelete<null>(`/categories/${categoryId}`)
}

export function getTags() {
  return apiGet<TagItem[]>('/tags')
}

export function createTag(payload: TagPayload) {
  return apiPost<TagItem>('/tags', payload)
}

export function updateTag(tagId: number, payload: TagPayload) {
  return apiPut<TagItem>(`/tags/${tagId}`, payload)
}

export function deleteTag(tagId: number) {
  return apiDelete<null>(`/tags/${tagId}`)
}

import { describe, expect, it } from 'vitest'
import { formatDate, newsStatusText, toApiDateTime, toDateTimeInputValue, topicStatusText } from './display'

describe('display utils', () => {
  it('maps business status labels', () => {
    expect(newsStatusText.unread).toBe('待阅读')
    expect(topicStatusText.writing).toBe('写作中')
  })

  it('formats empty date safely', () => {
    expect(formatDate()).toBe('-')
    expect(toDateTimeInputValue()).toBe('')
  })

  it('converts datetime-local value to api datetime', () => {
    const result = toApiDateTime('2026-04-28T10:30')
    expect(result).toContain('2026-04-28T')
  })
})

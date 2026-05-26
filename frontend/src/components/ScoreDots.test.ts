import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import ScoreDots from './ScoreDots.vue'

describe('ScoreDots', () => {
  it('renders five dots and marks active score', () => {
    const wrapper = mount(ScoreDots, {
      props: {
        value: 3,
        label: '热度',
      },
    })

    expect(wrapper.findAll('.score-dot')).toHaveLength(5)
    expect(wrapper.findAll('.is-on')).toHaveLength(3)
    expect(wrapper.attributes('aria-label')).toBe('热度3分')
  })
})

import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'

import Username from '@/components/common/Username.vue'

describe('Username', () => {
  it('displays username', () => {
    const wrapper = mount(Username, {
      propsData: {
        username: 'Hello'
      }
    })
    expect(wrapper.text()).to.equal('Hello')
  })
})

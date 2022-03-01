import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'

import Username from '@/components/common/Username.vue'

import { render } from '../../utils'

describe('Username', () => {
  it('displays username', () => {
    const wrapper = mount(Username, {
      propsData: {
        username: 'Hello'
      }
    })
    const vm = render(Username, {username: 'Hello'})
    expect(wrapper.text()).to.equal('Hello')
  })
})

import DangerousButton from '~/components/common/DangerousButton.vue'
import AlbumDetail from '~/views/admin/library/AlbumDetail.vue'
import SanitizedHtml from '~/components/SanitizedHtml.vue'
import HumanDate from '~/components/common/HumanDate.vue'

import { shallowMount } from '@vue/test-utils'
import { vi } from 'vitest'

import router from '~/router'
import store from '~/store'

describe('views/admin/library', () => {
  describe('Album details', () => {
    it('displays default cover', async () => {
      const wrapper = shallowMount(AlbumDetail, {
        props: { id: 1 },
        directives: {
          dropdown: () => null,
          title: () => null,
          lazy: () => null
        },
        global: {
          stubs: { DangerousButton, HumanDate, SanitizedHtml },
          plugins: [router, store]
        }
      })

      await vi.waitUntil(() => wrapper.find('img').exists())
      expect(wrapper.find('img').attributes('src')).to.include('default-cover')
    })
  })
})

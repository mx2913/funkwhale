import { describe, it, expect } from 'vitest'
import store from '@/store/playlists'

import { testAction } from '../../utils'

describe('store/playlists', () => {
  describe('mutations', () => {
    it('set playlists', () => {
      const state = { playlists: [] }
      store.mutations.playlists(state, [{ id: 1, name: 'test' }])
      expect(state.playlists).to.deep.equal([{ id: 1, name: 'test' }])
    })
  })
  describe('actions', () => {
    it('fetchOwn does nothing with no user', () => {
      testAction({
        action: store.actions.fetchOwn,
        payload: null,
        params: { state: { playlists: [] }, rootState: { auth: { profile: {} } } },
        expectedMutations: []
      })
    })
  })
})

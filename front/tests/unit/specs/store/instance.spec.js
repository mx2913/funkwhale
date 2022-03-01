import { describe, beforeEach, afterEach, it, expect } from 'vitest'
import store from '@/store/instance'
import { testAction } from '../../utils'

describe('store/instance', () => {

  describe('mutations', () => {
    it('settings', () => {
      const state = {settings: {users: {upload_quota: {value: 1}}}}
      let settings = {users: {registration_enabled: {value: true}}}
      store.mutations.settings(state, settings)
      expect(state.settings).to.deep.equal({
        users: {upload_quota: {value: 1}, registration_enabled: {value: true}}
      })
    })
    it('instanceUrl', () => {
      const state = {instanceUrl: null, knownInstances: ['http://test2/', 'http://test/']}
      store.mutations.instanceUrl(state, 'http://test')
      expect(state).to.deep.equal({
        instanceUrl: 'http://test/',  // trailing slash added
        knownInstances: ['http://test/', 'http://test2/']
      })
    })
  })
  describe('actions', () => {
    it('fetchSettings', () => {
      testAction({
        action: store.actions.fetchSettings,
        payload: null,
        expectedMutations: [
          {
            type: 'settings',
            payload: {
              users: {
                upload_quota: {
                  section: 'users',
                  name: 'upload_quota',
                  value: 1
                },
                registration_enabled: {
                  section: 'users',
                  name: 'registration_enabled',
                  value: false
                }
              }
            }
          }
        ]
      })
    })
  })
})

import type { BackendError, User } from '~/types'
import type { Module } from 'vuex'
import type { RootState } from '~/store/index'
import type { RouteLocationRaw } from 'vue-router'
import type { WebviewWindow } from '@tauri-apps/api/webview'

import axios from 'axios'
import useLogger from '~/composables/useLogger'
import useFormData from '~/composables/useFormData'

import { clear as clearIDB } from 'idb-keyval'
import { useQueue } from '~/composables/audio/queue'
import { isTauri } from '~/composables/tauri'

export type Permission = 'settings' | 'library' | 'moderation'
export interface State {
  authenticated: boolean
  username: string
  fullUsername: string
  availablePermissions: Record<Permission, boolean>,
  profile: null | User
  oauth: OAuthTokens
  scopedTokens: ScopedTokens

  applicationSecret: string | undefined

  oauthWindow: WebviewWindow | undefined
}

interface ScopedTokens {
  listen: null | string
}

interface OAuthTokens {
  clientId: null | string
  clientSecret: null | string
  accessToken: null | string
  refreshToken: null | string
}

const NEEDED_SCOPES = 'read write'

const logger = useLogger()

function getDefaultScopedTokens (): ScopedTokens {
  return {
    listen: null
  }
}

function getDefaultOauth (): OAuthTokens {
  return {
    clientId: null,
    clientSecret: null,
    accessToken: null,
    refreshToken: null
  }
}

async function createOauthApp () {
  const payload = {
    name: `Funkwhale web client at ${location.hostname}`,
    website: location.origin,
    scopes: NEEDED_SCOPES,
    redirect_uris: `${location.origin}/auth/callback`
  }
  return (await axios.post('oauth/apps/', payload)).data
}

const store: Module<State, RootState> = {
  namespaced: true,
  state: {
    authenticated: false,
    username: '',
    fullUsername: '',
    availablePermissions: {
      settings: false,
      library: false,
      moderation: false
    },
    profile: null,
    oauth: getDefaultOauth(),
    scopedTokens: getDefaultScopedTokens(),

    applicationSecret: undefined,

    oauthWindow: undefined
  },
  getters: {
    header: state => {
      if (state.oauth.accessToken) {
        return 'Bearer ' + state.oauth.accessToken
      }
    }
  },
  mutations: {
    reset (state) {
      state.authenticated = false
      state.profile = null
      state.username = ''
      state.fullUsername = ''
      state.scopedTokens = getDefaultScopedTokens()
      state.oauth = getDefaultOauth()
      state.availablePermissions = {
        settings: false,
        library: false,
        moderation: false
      }

      state.applicationSecret = undefined
    },
    profile: (state, value) => {
      state.profile = value
    },
    authenticated: (state, value) => {
      state.authenticated = value
      if (value === false) {
        state.username = ''
        state.fullUsername = ''
        state.profile = null
        state.scopedTokens = getDefaultScopedTokens()
        state.availablePermissions = {
          settings: false,
          library: false,
          moderation: false
        }
      }
    },
    username: (state, value) => {
      state.username = value
    },
    fullUsername: (state, value) => {
      state.fullUsername = value
    },
    avatar: (state, value) => {
      if (state.profile) {
        state.profile.avatar = value
      }
    },
    scopedTokens: (state, value) => {
      state.scopedTokens = { ...value }
    },
    permission: (state, { key, status }: { key: Permission, status: boolean }) => {
      state.availablePermissions[key] = status
    },
    profilePartialUpdate: (state, payload: User) => {
      if (!state.profile) {
        state.profile = {} as User
      }

      for (const [key, value] of Object.entries(payload)) {
        state.profile[key as keyof User] = value as never
      }
    },
    oauthApp: (state, payload) => {
      state.oauth.clientId = payload.client_id
      state.oauth.clientSecret = payload.client_secret
    },
    oauthToken: (state, payload) => {
      state.oauth.accessToken = payload.access_token
      state.oauth.refreshToken = payload.refresh_token
    }
  },
  actions: {
    // Send a request to the login URL and save the returned JWT
    async login ({ dispatch }, { credentials }) {
      const form = useFormData(credentials)
      await axios.post('users/login', form)

      logger.info('Successfully logged in as', credentials.username)
      await dispatch('fetchUser')
    },
    async logout ({ commit }) {
      try {
        await axios.post('users/logout')
      } catch (error) {
        logger.error('Error while logging out, probably logged in via oauth', error)
      }

      const modules = [
        'auth',
        'favorites',
        'player',
        'playlists',
        'queue',
        'radios'
      ]

      for (const module of modules) {
        commit(`${module}/reset`, null, { root: true })
      }

      // Clear session storage
      sessionStorage.clear()

      // Clear track queue
      await useQueue().clear()

      // Clear all indexedDB data
      await clearIDB()

      logger.info('Log out, goodbye!')
    },

    async fetchNotifications ({ dispatch, state }) {
      return Promise.all([
        dispatch('ui/fetchUnreadNotifications', null, { root: true }),
        state.availablePermissions.library && dispatch('ui/fetchPendingReviewEdits', null, { root: true }),
        state.availablePermissions.moderation && dispatch('ui/fetchPendingReviewReports', null, { root: true }),
        state.availablePermissions.moderation && dispatch('ui/fetchPendingReviewRequests', null, { root: true })
      ])
    },
    async fetchUser ({ dispatch }) {
      try {
        const response = await axios.get('users/me/')
        logger.info('Successfully fetched user profile')

        dispatch('updateUser', response.data)

        await Promise.all([
          dispatch('fetchNotifications'),
          dispatch('favorites/fetch', null, { root: true }),
          dispatch('playlists/fetchOwn', null, { root: true }),
          dispatch('libraries/fetchFollows', null, { root: true }),
          dispatch('channels/fetchSubscriptions', null, { root: true }),
          dispatch('moderation/fetchContentFilters', null, { root: true })
        ])
      } catch (error) {
        if ((error as BackendError).response?.status === 401) {
          logger.info('User is not authenticated')
          return
        }

        logger.error('Error while fetching user profile', error)
      }
    },
    updateUser ({ commit }, data) {
      commit('authenticated', true)
      commit('profile', data)
      commit('username', data.username)
      commit('fullUsername', data.full_username)

      if (data.tokens) {
        commit('scopedTokens', data.tokens)
      }

      for (const [permission, hasPermission] of Object.entries(data.permissions)) {
        // this makes it easier to check for permissions in templates
        commit('permission', { key: permission, status: hasPermission })
      }
    },
    async tryFinishOAuthFlow ({ state }) {
      if (isTauri()) {
        return state.oauthWindow?.close().catch(() => {
          // Ignore the error in case of window being already closed
        })
      }
    },
    async oauthLogin ({ state, rootState, commit, dispatch }, next: RouteLocationRaw) {
      const app = await createOauthApp()
      commit('oauthApp', app)
      const redirectUrl = encodeURIComponent(`${location.origin}/auth/callback`)
      const params = `response_type=code&scope=${encodeURIComponent(NEEDED_SCOPES)}&redirect_uri=${redirectUrl}&state=${next}&client_id=${state.oauth.clientId}`
      const authorizeUrl = `${rootState.instance.instanceUrl}authorize?${params}`

      if (isTauri()) {
        const { WebviewWindow } = await import('@tauri-apps/api/webview')

        state.oauthWindow = new WebviewWindow('oauth', {
          title: `Login to ${rootState.instance.settings.instance.name}`,
          parent: 'main',
          url: authorizeUrl
        })

        const token = await new Promise((resolve, reject) => {
          state.oauthWindow?.once('tauri://error', reject)
          state.oauthWindow?.once('tauri://destroyed', () => reject(new Error('Aborted by user')))
          state.oauthWindow?.once('oauthToken', async (event) => resolve(event.payload))
        }).finally(() => dispatch('tryFinishOAuthFlow'))

        commit('oauthToken', token)
        await dispatch('fetchUser')
      } else {
        logger.log('Redirecting user...', authorizeUrl)
        location.href = authorizeUrl
      }
    },
    async handleOauthCallback ({ state, commit, dispatch }, authorizationCode) {
      logger.log('Fetching token...')
      const payload = {
        client_id: state.oauth.clientId,
        client_secret: state.oauth.clientSecret,
        grant_type: 'authorization_code',
        code: authorizationCode,
        redirect_uri: `${location.origin}/auth/callback`
      }
      const response = await axios.post(
        'oauth/token/',
        useFormData(payload),
        { headers: { 'Content-Type': 'multipart/form-data' } }
      )

      if (isTauri()) {
        const { getCurrent } = await import('@tauri-apps/api/window')
        const currentWindow = getCurrent()

        // If the current window is the oauth window, pass the event to the main window
        if (currentWindow.label === 'oauth') {
          await currentWindow.emit('oauthToken', response.data)
          return
        }
      }

      commit('oauthToken', response.data)
      await dispatch('fetchUser')
    },
    async refreshOauthToken ({ state, commit }) {
      const payload = {
        client_id: state.oauth.clientId,
        client_secret: state.oauth.clientSecret,
        grant_type: 'refresh_token',
        refresh_token: state.oauth.refreshToken
      }
      const response = await axios.post(
        'oauth/token/',
        useFormData(payload),
        { headers: { 'Content-Type': 'multipart/form-data' } }
      )
      commit('oauthToken', response.data)
    }
  }
}

export default store

import type { Module } from 'vuex'
import type { RootState } from '~/store/index'
import type { SUPPORTED_LOCALES } from '~/init/locale'

import axios from 'axios'
import moment from 'moment'

type SupportedExtension = 'flac' | 'ogg' | 'mp3' | 'opus' | 'aac' | 'm4a' | 'aiff' | 'aif'

export type WebSocketEventName = 'inbox.item_added' | 'import.status_updated' | 'mutation.created' | 'mutation.updated'
  | 'report.created' | 'user_request.created' | 'Listen'

export type OrderingField = 'creation_date' | 'title' | 'album__title' | 'artist__name' | 'release_date' | 'name'
  | 'applied_date' | 'followers_count' | 'uploads_count' | 'length' | 'items_count' | 'modification_date' | 'size'
  | 'accessed_date' | 'bitrate' | 'duration' | 'last_fetch_date' | 'preferred_username' | 'domain' | 'handled_date'
  | 'album_title' | 'artist_name' | 'actors_count' | 'outbox_activities_count' | 'expiration_date' | 'date_joined'
  | 'last_activity' | 'username'

export type OrderingDirection = '-' | '+'
interface WebSocketEvent {
  type: WebSocketEventName
}

type WebSocketHandlers = Record<string, (event: WebSocketEvent) => void>

interface Message {
  displayTime: number
  key: string
}

type NotificationsKey = 'inbox' | 'pendingReviewEdits' | 'pendingReviewReports' | 'pendingReviewRequests'

export interface State {
  currentLanguage: 'en_US' | keyof typeof SUPPORTED_LOCALES
  selectedLanguage: boolean
  queueFocused: null | 'queue' | 'player'
  momentLocale: 'en'
  lastDate: Date
  maxMessages: number
  messageDisplayDuration: number
  supportedExtensions: SupportedExtension[]
  messages: Message[]
  window: {
    height: number
    width: number
  }
  pageTitle: null

  notifications: Record<NotificationsKey, number>
  websocketEventsHandlers: Record<WebSocketEventName, WebSocketHandlers>
}

const store: Module<State, RootState> = {
  namespaced: true,
  state: {
    currentLanguage: 'en_US',
    selectedLanguage: false,
    queueFocused: null,
    momentLocale: 'en',
    lastDate: new Date(),
    maxMessages: 100,
    messageDisplayDuration: 5 * 1000,
    supportedExtensions: ['flac', 'ogg', 'mp3', 'opus', 'aac', 'm4a', 'aiff', 'aif'],
    messages: [],
    window: {
      height: 0,
      width: 0
    },
    notifications: {
      inbox: 0,
      pendingReviewEdits: 0,
      pendingReviewReports: 0,
      pendingReviewRequests: 0
    },
    websocketEventsHandlers: {
      'inbox.item_added': {},
      'import.status_updated': {},
      'mutation.created': {},
      'mutation.updated': {},
      'report.created': {},
      'user_request.created': {},
      Listen: {}
    },
    pageTitle: null
  },
  getters: {
    showInstanceSupportMessage: (state, getters, rootState) => {
      if (!rootState.auth.profile) {
        return false
      }
      if (!rootState.instance.settings.instance.support_message.value) {
        return false
      }
      const displayDate = rootState.auth.profile.instance_support_message_display_date
      if (!displayDate) {
        return false
      }
      return moment(displayDate) < moment(state.lastDate)
    },
    showFunkwhaleSupportMessage: (state, getters, rootState) => {
      if (!rootState.auth.profile) {
        return false
      }
      if (!rootState.instance.settings.instance.funkwhale_support_message_enabled.value) {
        return false
      }
      const displayDate = rootState.auth.profile.funkwhale_support_message_display_date
      if (!displayDate) {
        return false
      }
      return moment(displayDate) < moment(state.lastDate)
    },
    additionalNotifications: (state, getters) => {
      let count = 0
      if (getters.showInstanceSupportMessage) {
        count += 1
      }
      if (getters.showFunkwhaleSupportMessage) {
        count += 1
      }
      return count
    },

    windowSize: (state) => {
      // IMPORTANT: if you modify these breakpoints, also modify the values in
      // style/vendor/_media.scss
      const width = state.window.width
      const breakpoints = [
        { name: 'widedesktop', width: 1200 },
        { name: 'desktop', width: 1024 },
        { name: 'tablet', width: 768 },
        { name: 'phone', width: 320 }
      ]
      for (let index = 0; index < breakpoints.length; index++) {
        const element = breakpoints[index]
        if (width >= element.width) {
          return element.name
        }
      }
      return 'phone'
    },
    layoutVersion: (state, getters) => {
      if (['tablet', 'phone'].indexOf(getters.windowSize) > -1) {
        return 'small'
      } else {
        return 'large'
      }
    }
  },
  mutations: {
    addWebsocketEventHandler: (state, { eventName, id, handler }: { eventName: WebSocketEventName, id: string, handler: (event: any) => void}) => {
      state.websocketEventsHandlers[eventName][id] = handler
    },
    removeWebsocketEventHandler: (state, { eventName, id }: { eventName: WebSocketEventName, id: string }) => {
      delete state.websocketEventsHandlers[eventName][id]
    },
    currentLanguage: (state, value) => {
      state.currentLanguage = value
      state.selectedLanguage = true
    },
    momentLocale: (state, value) => {
      state.momentLocale = value
      moment.locale(value)
    },
    computeLastDate: (state) => {
      state.lastDate = new Date()
    },
    queueFocused: (state, value) => {
      state.queueFocused = value
    },

    addMessage (state, message) {
      const finalMessage = {
        displayTime: state.messageDisplayDuration,
        key: String(new Date()),
        ...message
      }

      const key = finalMessage.key
      state.messages.splice(state.messages.findIndex(message => message.key === key), 1)
      state.messages.push(finalMessage)
      if (state.messages.length > state.maxMessages) {
        state.messages.shift()
      }
    },
    removeMessage (state, key) {
      state.messages.splice(state.messages.findIndex(message => message.key === key), 1)
    },
    notifications (state, { type, count }: { type: NotificationsKey, count: number }) {
      state.notifications[type] = count
    },
    incrementNotifications (state, { type, count, value }: { type: NotificationsKey, count: number, value?: number }) {
      if (value !== undefined) {
        state.notifications[type] = Math.max(0, value)
      } else {
        state.notifications[type] = Math.max(0, state.notifications[type] + count)
      }
    },
    pageTitle: (state, value) => {
      state.pageTitle = value
    },
    window: (state, value) => {
      state.window = value
    }
  },
  actions: {
    async fetchUnreadNotifications ({ commit }) {
      const response = await axios.get('federation/inbox/', { params: { is_read: false, page_size: 1 } })
        .catch(() => ({ data: { count: 0 } }))
      commit('notifications', { type: 'inbox', count: response.data.count })
    },
    async fetchPendingReviewEdits ({ commit }) {
      const response = await axios.get('mutations/', { params: { is_approved: 'null', page_size: 1 } })
        .catch(() => ({ data: { count: 0 } }))
      commit('notifications', { type: 'pendingReviewEdits', count: response.data.count })
    },
    async fetchPendingReviewReports ({ commit }) {
      const response = await axios.get('manage/moderation/reports/', { params: { is_handled: 'false', page_size: 1 } })
        .catch(() => ({ data: { count: 0 } }))
      commit('notifications', { type: 'pendingReviewReports', count: response.data.count })
    },
    async fetchPendingReviewRequests ({ commit }) {
      const response = await axios.get('manage/moderation/requests/', { params: { status: 'pending', page_size: 1 } })
        .catch(() => ({ data: { count: 0 } }))
      commit('notifications', { type: 'pendingReviewRequests', count: response.data.count })
    },

    async currentLanguage ({ commit, rootState, state }, value) {
      if (state.selectedLanguage && state.currentLanguage === value) return

      commit('currentLanguage', value)
      if (rootState.auth.authenticated) {
        await axios.post('users/settings', { language: value })
      }
    },

    websocketEvent ({ state }, event: WebSocketEvent) {
      const handlers = state.websocketEventsHandlers[event.type]
      console.log('Dispatching websocket event', event, handlers)
      if (!handlers) {
        return
      }

      const names = Object.keys(handlers)
      names.forEach((k) => {
        const handler = handlers[k]
        handler(event)
      })
    }
  }
}

export default store

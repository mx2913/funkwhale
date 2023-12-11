<script setup lang="ts">
import LegacyLayout from '~/LegacyLayout.vue'
import UiApp from '~/ui/App.vue'

import type { QueueTrack } from '~/composables/audio/queue'

import { watchEffect } from 'vue'

import { useQueue } from '~/composables/audio/queue'
import { useStore } from '~/store'

import useLogger from '~/composables/useLogger'

import { useRoute } from 'vue-router'

const route = useRoute()

const logger = useLogger()
logger.debug('App setup()')

const store = useStore()

// Tracks
const { currentTrack } = useQueue()
const getTrackInformationText = (track: QueueTrack | undefined) => {
  if (!track) {
    return null
  }

  return `♫ ${track.title} – ${track.artistName} ♫`
}

// Update title
const initialTitle = document.title
watchEffect(() => {
  const parts = [
    getTrackInformationText(currentTrack.value),
    store.state.ui.pageTitle,
    initialTitle || 'Funkwhale'
  ]

  document.title = parts.filter(i => i).join(' – ')
})

// Fetch user data on startup
// NOTE: We're not checking if we're authenticated in the store,
//       because we want to learn if we are authenticated at all
store.dispatch('auth/fetchUser')
</script>

<template>
  <UiApp v-if="route.fullPath.startsWith('/ui')" />
  <LegacyLayout v-else />
</template>

<style>
html, body {
  font-size: 16px;
}
</style>

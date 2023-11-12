<script setup lang="ts">
import type { Playlist } from '~/types'

import { ref, reactive, watch } from 'vue'
import { useStore } from '~/store'

import axios from 'axios'

import useErrorHandler from '~/composables/useErrorHandler'

import { FwButton } from '@funkwhale/ui'

import PlaylistCard from '~/components/playlists/Card.vue'

interface Props {
  filters: Record<string, unknown>
  url: string
}

const props = defineProps<Props>()

const store = useStore()

const objects = reactive([] as Playlist[])
const isLoading = ref(false)
const nextPage = ref('')
const fetchData = async (url = props.url) => {
  isLoading.value = true

  try {
    const params = {
      ...props.filters,
      page_size: props.filters.limit ?? 3
    }

    const response = await axios.get(url, { params })
    nextPage.value = response.data.next
    objects.push(...response.data.results)
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false
}

watch(
  () => store.state.moderation.lastUpdate,
  () => fetchData(),
  { immediate: true }
)
</script>

<template>
  <div>
    <h3
      v-if="!!$slots.title"
      class="ui header"
    >
      <slot name="title" />
    </h3>
    <div
      v-if="isLoading"
      class="ui inverted active dimmer"
    >
      <div class="ui loader" />
    </div>
    <div
      v-if="objects.length > 0"
      class="ui cards app-cards"
    >
      <playlist-card
        v-for="playlist in objects"
        :key="playlist.id"
        :playlist="playlist"
      />
    </div>
    <div
      v-else
      class="ui placeholder segment"
    >
      <div class="ui icon header">
        <i class="list icon" />
        {{ $t('components.playlists.Widget.placeholder.noPlaylists') }}
      </div>
      <fw-button
        v-if="$store.state.auth.authenticated"
        color="primary"
        icon="bi-list-task"
        @click="$store.commit('playlists/chooseTrack', null)"
      >
        {{ $t('components.playlists.Widget.button.create') }}
      </fw-button>
    </div>
    <template v-if="nextPage">
      <div class="ui hidden divider" />
      <fw-button
        v-if="nextPage"
        outline
        color="secondary"
        @click="fetchData(nextPage)"
      >
        {{ $t('components.playlists.Widget.button.more') }}
      </fw-button>
    </template>
  </div>
</template>

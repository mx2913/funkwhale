<script setup lang="ts">
import type { ArtistCredit } from '~/types'

interface Props {
  artistCredit: ArtistCredit[]
}

const props = defineProps<Props>()

const getRoute = (ac: ArtistCredit) => {
  return {
    name: ac.artist.channel ? 'channels.detail' : 'library.artists.detail',
    params: {
      id: ac.artist.id.toString()
    }
  }
}
</script>

<template>
  <div class="artist-label ui image label">
    <template
      v-for="ac in props.artistCredit"
      :key="ac.artist.id"
    >
      <router-link
        :to="getRoute(ac)"
      >
        <img
          v-if="ac.index === 0 && ac.artist.cover && ac.artist.cover.urls.original"
          v-lazy="$store.getters['instance/absoluteUrl'](ac.artist.cover.urls.medium_square_crop)"
          alt=""
          :class="[{circular: ac.artist.content_category != 'podcast'}]"
        >
        <i
          v-else-if="ac.index === 0 "
          :class="[ac.artist.content_category != 'podcast' ? 'circular' : 'bordered', 'inverted violet users icon']"
        />
        {{ ac.credit }}
      </router-link>
      <span>{{ ac.joinphrase }}</span>
    </template>
  </div>
</template>

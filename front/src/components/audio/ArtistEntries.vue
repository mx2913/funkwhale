<template>
  <div class="artist-entries">
    <div :class="[{active: currentTrack && track.id === currentTrack.id}, 'artist-entry']" @mouseover="track.hover = true" @mouseleave="track.hover = false"  @click.prevent="replacePlay(tracks, index)" v-for="(track, index) in tracks" :key="track.id">
      <span>      
        <img alt="" class="ui mini image" v-if="track.album && track.album.cover && track.album.cover.urls.original" v-lazy="$store.getters['instance/absoluteUrl'](track.album.cover.urls.medium_square_crop)">
        <img alt="" class="ui mini image" v-else src="../../assets/audio/default-cover.png">
      </span>
      <div class="actions">
        <play-button 
          v-if="currentTrack && isPlaying && track.id === currentTrack.id" 
          class="basic circular icon" 
          :playing="true"
          :button-classes="pausedButtonClasses" 
          :discrete="true" 
          :icon-only="true" 
          :track="track"
          :tracks="tracks">
        </play-button>
        <play-button 
          v-else-if="currentTrack && !isPlaying && track.id === currentTrack.id" 
          class="basic circular icon" 
          :paused="true"
          :button-classes="pausedButtonClasses" 
          :discrete="true" 
          :icon-only="true" 
          :track="track"
          :tracks="tracks">
        </play-button>
        <play-button 
          v-else-if="track.hover" 
          class="basic circular icon" 
          :button-classes="playingButtonClasses" 
          :discrete="true" :icon-only="true" 
          :track="track"
          :tracks="tracks">
        </play-button>
      </div>
      <div class="content ellipsis">
        <strong>{{ track.title }}</strong><br>
      </div>
      <div class="meta">
        <track-favorite-icon class="tiny" :border="false" :track="track"></track-favorite-icon>
        <human-duration v-if="track.uploads[0] && track.uploads[0].duration" :duration="track.uploads[0].duration"></human-duration>
      </div>
      <div class="actions">
        <play-button class="play-button basic icon" :dropdown-only="true" :is-playable="track.is_playable" :dropdown-icon-classes="['ellipsis', 'vertical', 'large really discrete']" :track="track"></play-button>
      </div>
    </div>
  </div>
</template>

<script>
import _ from '@/lodash'
import PlayButton from '@/components/audio/PlayButton'
import TrackFavoriteIcon from '@/components/favorites/TrackFavoriteIcon'
import { mapGetters } from "vuex"


export default {
  props: {
    tracks: Array,
  },
  components: {
    PlayButton,
    TrackFavoriteIcon,
  },
  data() {
    return {
      playingButtonClasses: ['really', 'tiny', 'basic', 'icon', 'button', 'play-button'],
      pausedButtonClasses: ['really', 'tiny', 'basic', 'icon', 'button', 'play-button', 'paused'],
    }
  },
  computed: {
    ...mapGetters({
      currentTrack: "queue/currentTrack",
    }),

    isPlaying () {
      return this.$store.state.player.playing
    },
  },
  methods: {
    prettyPosition (position, size) {
      var s = String(position);
      while (s.length < (size || 2)) {s = "0" + s;}
      return s;
    },
    replacePlay (tracks, trackIndex) {
      this.$store.dispatch('queue/clean')
      this.$store.dispatch('queue/appendMany', {tracks: tracks}).then(() => {
        this.$store.dispatch('queue/currentIndex', trackIndex)
      })
    },
  },
  created () {
    this.tracks.forEach((track) => {
        this.$set(track, 'hover', false)
    })
}
}
</script>

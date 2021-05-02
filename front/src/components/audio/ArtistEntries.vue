<template>
  <div class="artist-entries ui unstackable grid">
    <div class="artist-entries row">
      <div class="actions one wide left floated column"></div>
      <div class="image one wide left floated column"></div>
      <div class="content ellipsis two wide left floated column">
        <b>{{ labels.title }}</b>
      </div>
      <div class="content ellipsis two wide left floated column">
        <b>{{ labels.album }}</b>
      </div>
      <div class="meta one wide right floated column"></div>
      <div class="meta one wide right floated column">
        <i class="clock icon" style="padding: 0.5rem;" />
      </div>
      <div class="one wide right floated column"></div>
    </div>
    <div 
      :class="[{active: currentTrack && track.id === currentTrack.id}, 'artist-entry row']" 
      @mouseover="track.hover = true" 
      @mouseleave="track.hover = false"  
      @dblclick="replacePlay(tracks, index)"
      @contextmenu.prevent="$refs.playmenu.open()"
      v-for="(track, index) in tracks" :key="track.id">
      <div class="actions one wide left floated column">
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
      <div class="image one wide left floated column">
        <img alt="" class="ui artist-track mini image" v-if="track.album && track.album.cover && track.album.cover.urls.original" v-lazy="$store.getters['instance/absoluteUrl'](track.album.cover.urls.medium_square_crop)">
        <img alt="" class="ui artist-track mini image" v-else src="../../assets/audio/default-cover.png">
      </div>
      <div class="content ellipsis two wide left floated column">
        <router-link :to="{name: 'library.tracks.detail', params: {id: track.id }}">{{ track.title }}</router-link>
      </div>
      <div class="content ellipsis two wide left floated column">
        <router-link :to="{name: 'library.albums.detail', params: {id: track.album.id }}">{{ track.album.title }}</router-link>
      </div>
      <div class="meta one wide right floated column">
        <track-favorite-icon class="tiny" :border="false" :track="track"></track-favorite-icon>
      </div>
      <div class="meta one wide right floated column">
        <human-duration v-if="track.uploads[0] && track.uploads[0].duration" :duration="track.uploads[0].duration"></human-duration>
      </div>
      <div class="one wide right floated column">
        <play-button id="playmenu" class="play-button basic icon" :dropdown-only="true" :is-playable="track.is_playable" :dropdown-icon-classes="['ellipsis', 'vertical', 'large really discrete']" :track="track"></play-button>
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

    labels() {
      return {
        title: this.$pgettext("*/*/*/Noun", "Title"),
        album: this.$pgettext("*/*/*/Noun", "Album")
      }
    }
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

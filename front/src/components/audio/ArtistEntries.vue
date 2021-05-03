<template>
  <div class="artist-entries ui unstackable grid">
    <div class="artist-entries row">
      <div class="actions one wide left floated column"></div>
      <div v-if="showArt" class="image one wide left floated column"></div>
      <div class="content ellipsis two wide left floated column">
        <b>{{ labels.title }}</b>
      </div>
      <div v-if="showAlbum" class="content ellipsis two wide left floated column">
        <b>{{ labels.album }}</b>
      </div>
      <div v-if="showArtist" class="content ellipsis two wide left floated column">
        <b>{{ labels.artist }}</b>
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
      @dblclick="doubleClick(track, index)"
      @contextmenu.prevent="$refs.playmenu.open()"
      v-for="(track, index) in tracks" :key="track.id">
      <div class="actions one wide left floated column">
        <play-indicator
          v-if="!$store.state.player.isLoadingAudio && currentTrack && isPlaying && track.id === currentTrack.id && !track.hover">
        </play-indicator>
        <button
          v-else-if="currentTrack && isPlaying && track.id === currentTrack.id && track.hover"
          class="ui really tiny basic icon button play-button"
          @click.prevent.exact="pausePlayback"
        >
        <i class="pause icon" />
        </button>
        <button
          v-else-if="currentTrack && !isPlaying && track.id === currentTrack.id && track.hover"
          class="ui really tiny basic icon button play-button"
          @click.prevent.exact="resumePlayback"
        >
          <i class="play icon" />
        </button>
        <button
          v-else-if="track.hover"
          class="ui really tiny basic icon button play-button"
          @click.prevent.exact="replacePlay(tracks, index)"
        >
          <i class="play icon" />
        </button>
        <span class="trackPosition" v-else-if="showPosition">
          {{ prettyPosition(track.position) }}
        </span>
      </div>
      <div v-if="showArt" class="image left floated column">
        <img alt="" class="ui artist-track mini image" v-if="track.album && track.album.cover && track.album.cover.urls.original" v-lazy="$store.getters['instance/absoluteUrl'](track.album.cover.urls.medium_square_crop)">
        <img alt="" class="ui artist-track mini image" v-else src="../../assets/audio/default-cover.png">
      </div>
      <div class="content ellipsis left floated column">
        <router-link :to="{name: 'library.tracks.detail', params: {id: track.id }}">{{ track.title }}</router-link>
      </div>
      <div v-if="showAlbum" class="content ellipsis left floated column">
        <router-link :to="{name: 'library.albums.detail', params: {id: track.album.id }}">{{ track.album.title }}</router-link>
      </div>
      <div v-if="showArtist" class="content ellipsis left floated column">
        <router-link class="artist link" :to="{name: 'library.artists.detail', params: {id: track.artist.id }}">{{ track.artist.name }}</router-link>
      </div>
      <div class="meta right floated column">
        <track-favorite-icon class="tiny" :border="false" :track="track"></track-favorite-icon>
      </div>
      <div class="meta right floated column">
        <human-duration v-if="track.uploads[0] && track.uploads[0].duration" :duration="track.uploads[0].duration"></human-duration>
      </div>
      <div class="right floated column">
        <play-button id="playmenu" class="play-button basic icon" :dropdown-only="true" :is-playable="track.is_playable" :dropdown-icon-classes="['ellipsis', 'vertical', 'large really discrete']" :track="track"></play-button>
      </div>
    </div>
  </div>
</template>

<script>
import _ from '@/lodash'
import TrackFavoriteIcon from '@/components/favorites/TrackFavoriteIcon'
import { mapActions, mapGetters } from "vuex"
import PlayIndicator from '@/components/audio/track/PlayIndicator'
import PlayButton from '@/components/audio/PlayButton'

export default {
  props: {
    tracks: Array,
    showAlbum: {type: Boolean, required: false, default: true},
    showArtist: {type: Boolean, required: false, default: true},
    trackOnly: {type: Boolean, required: false, default: false},
    showPosition: {type: Boolean, required: false, default: false},
    showArt: {type: Boolean, required: false, default: true}
  },
  components: {
    TrackFavoriteIcon,
    PlayIndicator,
    PlayButton
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
        album: this.$pgettext("*/*/*/Noun", "Album"),
        artist: this.$pgettext("*/*/*/Noun", "Artist")
      }
    }
  },
  methods: {
    ...mapActions({
      resumePlayback: "player/resumePlayback",
      pausePlayback: "player/pausePlayback",
    }),

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
    doubleClick(track, index) {
      if (this.currentTrack && this.isPlaying && track.id === this.currentTrack.id) {
        this.pausePlayback()
      } else if (this.currentTrack && !this.isPlaying && track.id === this.currentTrack.id) {
        this.resumePlayback()
      } else {
        this.replacePlay(this.tracks, index)
      }
    }
  },
  created () {
    this.tracks.forEach((track) => {
        this.$set(track, 'hover', false)
    })
}
}
</script>

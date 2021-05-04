<template>
  <div>
    <!-- Show the search bar if search is true -->
    <inline-search-bar v-model="query" v-if="search" @search="additionalTracks = []; fetchData()"></inline-search-bar>
    <div class="ui hidden divider"></div>

    <!-- Add a header if needed -->

    <slot name="header"></slot>

    <!-- Show a message if no tracks are available -->

    <slot v-if="!isLoading && allTracks.length === 0" name="empty-state">
      <empty-state @refresh="fetchData('tracks/')" :refresh="true"></empty-state>
    </slot>

    <!-- If tracks are available, build the header -->

    <div v-else :class="['track-table', 'ui', 'unstackable', 'grid']">
      <div v-if="isLoading" class="ui inverted active dimmer">
        <div class="ui loader"></div>
      </div>
      <div class="track-table row">
        <div v-if="showPosition" class="actions left floated column">
          <i class="hashtag icon"></i>
        </div>
        <div v-else class="actions left floated column"></div>
        <div v-if="showArt" class="image left floated column"></div>
        <div class="content ellipsis left floated column">
          <b>{{ labels.title }}</b>
        </div>
        <div v-if="showAlbum" class="content ellipsisleft floated column">
          <b>{{ labels.album }}</b>
        </div>
        <div v-if="showArtist" class="content ellipsis left floated column">
          <b>{{ labels.artist }}</b>
        </div>
        <div v-if="$store.state.auth.authenticated" class="meta right floated column"></div>
        <div v-if="showDuration" class="meta right floated column">
          <i class="clock outline icon" style="padding: 0.5rem;" />
        </div>
        <div v-if="displayActions" class="meta right floated column"></div>
      </div>

      <!-- For each item, build a row -->

      <div 
        :class="[{active: currentTrack && track.id === currentTrack.id}, 'track-row row']" 
        @mouseover="track.hover = true" 
        @mouseleave="track.hover = false"  
        @dblclick="doubleClick(track, index)"
        @contextmenu.prevent="$refs.playmenu.open()"
        v-for="(track, index) in allTracks" :key="track.id">
        <div class="actions one wide left floated column">
          <play-indicator
            v-if="!$store.state.player.isLoadingAudio && currentTrack && isPlaying && track.id === currentTrack.id && !track.hover">
          </play-indicator>
          <button
            v-else-if="currentTrack && !isPlaying && track.id === currentTrack.id && !track.hover"
            class="ui really tiny basic icon button play-button paused"
          >
            <i class="pause icon" />
          </button>
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
            @click.prevent.exact="replacePlay(allTracks, index)"
          >
            <i class="play icon" />
          </button>
          <span class="trackPosition" v-else-if="showPosition">
            {{ prettyPosition(track.position) }}
          </span>
        </div>
        <div v-if="showArt" class="image left floated column">
          <img alt="" class="ui artist-track mini image" v-if="track.album && track.album.cover && track.album.cover.urls.original" v-lazy="$store.getters['instance/absoluteUrl'](track.album.cover.urls.medium_square_crop)">
          <img alt="" class="ui artist-track mini image" v-else src="../../../assets/audio/default-cover.png">
        </div>
        <div class="content ellipsis left floated column">
          <a 
            v-if="currentTrack && !isPlaying && track.id === currentTrack.id" 
            @click="resumePlayback"
          >
            {{ track.title }}
          </a>
          <a 
            v-else-if="currentTrack && isPlaying && track.id === currentTrack.id" 
            @click="pausePlayback"
          >
            {{ track.title }}
          </a>
          <a 
            v-else
            @click.prevent.exact="replacePlay(allTracks, index)"
          >
            {{ track.title }}
          </a>
        </div>
        <div v-if="showAlbum" class="content ellipsis left floated column">
          <router-link :to="{name: 'library.albums.detail', params: {id: track.album.id }}">{{ track.album.title }}</router-link>
        </div>
        <div v-if="showArtist" class="content ellipsis left floated column">
          <router-link class="artist link" :to="{name: 'library.artists.detail', params: {id: track.artist.id }}">{{ track.artist.name }}</router-link>
        </div>
        <div v-if="$store.state.auth.authenticated" class="meta right floated column">
          <track-favorite-icon class="tiny" :border="false" :track="track"></track-favorite-icon>
        </div>
        <div v-if="showDuration" class="meta right floated column">
          <human-duration v-if="track.uploads[0] && track.uploads[0].duration" :duration="track.uploads[0].duration"></human-duration>
        </div>
        <div v-if="displayActions" class="meta right floated column">
          <play-button id="playmenu" class="play-button basic icon" :dropdown-only="true" :is-playable="track.is_playable" :dropdown-icon-classes="['ellipsis', 'vertical', 'large really discrete']" :track="track"></play-button>
        </div>
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
import axios from 'axios'

export default {
  props: {
    tracks: Array,
    showAlbum: {type: Boolean, required: false, default: true},
    showArtist: {type: Boolean, required: false, default: true},
    trackOnly: {type: Boolean, required: false, default: false},
    showPosition: {type: Boolean, required: false, default: false},
    showArt: {type: Boolean, required: false, default: true},
    search: {type: Boolean, required: false, default: false},
    filters: {type: Object, required: false, default: null},
    nextUrl: {type: String, required: false, default: null},
    displayActions: {type: Boolean, required: false, default: true},
    showDuration: {type: Boolean, required: false, default: true},
  },
  components: {
    TrackFavoriteIcon,
    PlayIndicator,
    PlayButton
  },
  data () {
    return {
      fetchDataUrl: this.nextUrl,
      isLoading: false,
      additionalTracks: [],
      query: '',
    }
  },
  computed: {
    ...mapGetters({
      currentTrack: "queue/currentTrack",
    }),

    allTracks () {
      return (this.tracks || []).concat(this.additionalTracks)
    },

    isPlaying () {
      return this.$store.state.player.playing
    },

    labels() {
      return {
        title: this.$pgettext("*/*/*/Noun", "Title"),
        album: this.$pgettext("*/*/*/Noun", "Album"),
        artist: this.$pgettext("*/*/*/Noun", "Artist")
      }
    },

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
        this.replacePlay(this.allTracks, index)
      }
    },

    fetchData (url) {
      if (!url) {
        return
      }
      this.isLoading = true
      let self = this
      let params = _.clone(this.filters)
      params.page_size = this.limit
      params.page = this.page
      params.include_channels = true
      axios.get(url, {params: params}).then((response) => {
        self.nextPage = response.data.next
        self.isLoading = false
        self.objects = response.data.results
        self.count = response.data.count
        self.$emit('fetched', response.data)
      }, error => {
        self.isLoading = false
        self.errors = error.backendErrors
      })
    }
  },

  created () {

    if (!this.tracks) {
      this.fetchData('tracks/')
    }
    
    this.allTracks.forEach((track) => {
        this.$set(track, 'hover', false)
    })
}
}
</script>

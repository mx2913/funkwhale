<template>
  <section class="main pusher" :aria-label="labels.queue">
    <button
      class="ui basic circular icon button"
      @click.stop="$router.go(-1)">
      <i class="x icon"></i>
    </button>
    <div :class="['ui vertical stripe queue segment', $route.hash === '#player' ? 'player-focused' : '']">
      <div class="ui fluid container">
        <div class="ui stackable grid" id="queue-grid">
          <div class="ui sixteen wide mobile ten wide computer column queue-column">

            <div class="ui text container">
              <div class="ui sticky basic clearing fixed-header segment">
                <h2 class="ui header">
                  <div class="content">
                    <button class="ui right floated circular basic icon button dropdown controls-dropdown">
                      <i class="ellipsis vertical icon"></i>
                      <div
                        v-if="$store.state.ui.notifications.pendingReviewEdits + $store.state.ui.notifications.pendingReviewReports > 0"
                        :class="['ui', 'teal', 'mini', 'bottom floating', 'circular', 'label']">{{ $store.state.ui.notifications.pendingReviewEdits + $store.state.ui.notifications.pendingReviewReports }}</div>
                      <div class="menu">
                        <div
                          role="button"
                          class="item"
                          @click="$store.dispatch('queue/shuffle')">
                          <translate translate-context="*/Queue/*/Verb">Shuffle</translate>
                        </div>
                        <div
                          role="button"
                          class="item"
                          @click="$store.dispatch('queue/clean'); $router.go(-1)">
                          <translate translate-context="*/Queue/*/Verb">Clear</translate>
                        </div>
                        <div
                          role="button"
                          class="item"
                          @click="$router.go(-1)">
                          <translate translate-context="*/*/Button.Label/Verb">Close</translate>
                        </div>
                      </div>
                    </button>
                    {{ labels.queue }}
                    <div class="sub header">
                      <div>
                        <translate translate-context="Sidebar/Queue/Text" :translate-params="{index: queue.currentIndex + 1, length: queue.tracks.length}">
                          Track %{ index } of %{ length }
                        </translate><template v-if="!$store.state.radios.running"> -
                          <span :title="labels.duration">
                            {{ timeLeft }}
                          </span>
                        </template>
                      </div>
                    </div>
                  </div>
                </h2>
                <div v-if="$store.state.radios.running" class="ui black message">
                  <div class="content">
                    <div class="header">
                      <i class="feed icon"></i> <translate translate-context="Sidebar/Player/Title">You have a radio playing</translate>
                    </div>
                    <p><translate translate-context="Sidebar/Player/Paragraph">New tracks will be appended here automatically.</translate></p>
                    <div @click="$store.dispatch('radios/stop')" class="ui basic inverted red button"><translate translate-context="*/Player/Button.Label/Short, Verb">Stop radio</translate></div>
                  </div>
                </div>
              </div>
              <table class="ui compact very basic fixed single line selectable unstackable table">
                <draggable v-model="tracks" tag="tbody" @update="reorder" handle=".handle">
                  <tr
                    @click="$store.dispatch('queue/currentIndex', index)"
                    v-for="(track, index) in tracks"
                    :key="index"
                    :class="['queue-item', {'active': index === queue.currentIndex}]">
                    <td class="handle">
                      <i class="arrows alternate grey icon"></i>
                    </td>
                    <td class="image-cell">
                      <img class="ui mini image" v-if="track.album.cover && track.album.cover.original" :src="$store.getters['instance/absoluteUrl'](track.album.cover.small_square_crop)">
                      <img class="ui mini image" v-else src="../assets/audio/default-cover.png">
                    </td>
                    <td colspan="3">
                      <button class="title reset ellipsis" :title="track.title" :aria-label="labels.selectTrack">
                        <strong>{{ track.title }}</strong><br />
                        <span>
                          {{ track.artist.name }}
                        </span>
                      </button>
                    </td>
                    <td class="duration-cell">
                      <template v-if="track.uploads.length > 0">
                        {{ time.durationFormatted(track.uploads[0].duration) }}
                      </template>
                    </td>
                    <td class="controls">
                      <template v-if="$store.getters['favorites/isFavorite'](track.id)">
                        <i class="pink heart icon"></i>
                      </template>
                      <button :title="labels.removeFromQueue" @click.stop="cleanTrack(index)" :class="['ui', 'really', 'tiny', 'basic', 'circular', 'icon', 'button']">
                        <i class="x icon"></i>
                      </button>
                    </td>
                  </tr>
                </draggable>
              </table>
            </div>
          </div>
          <div class="ui six wide column current-track">
            <div class="ui basic segment" id="player">
              <template v-if="currentTrack">
                <img class="ui image" v-if="currentTrack.album.cover && currentTrack.album.cover.original" :src="$store.getters['instance/absoluteUrl'](currentTrack.album.cover.square_crop)">
                <img class="ui image" v-else src="../assets/audio/default-cover.png">
                <h3 class="ui header">
                  <div class="content ellipsis">
                    <router-link class="small header discrete link track" :title="currentTrack.title" :to="{name: 'library.tracks.detail', params: {id: currentTrack.id }}">
                      {{ currentTrack.title | truncate(35) }}
                    </router-link>
                    <div class="sub header">
                      <router-link class="discrete link artist" :title="currentTrack.artist.name" :to="{name: 'library.artists.detail', params: {id: currentTrack.artist.id }}">
                        {{ currentTrack.artist.name | truncate(35) }}</router-link> /<router-link class="discrete link album" :title="currentTrack.album.title" :to="{name: 'library.albums.detail', params: {id: currentTrack.album.id }}">
                        {{ currentTrack.album.title | truncate(35) }}
                      </router-link>
                    </div>
                  </div>
                </h3>
                <div class="ui small warning message" v-if="currentTrack && errored">
                  <div class="header">
                    <translate translate-context="Sidebar/Player/Error message.Title">The track cannot be loaded</translate>
                  </div>
                  <p v-if="hasNext && playing && $store.state.player.errorCount < $store.state.player.maxConsecutiveErrors">
                    <translate translate-context="Sidebar/Player/Error message.Paragraph">The next track will play automatically in a few seconds…</translate>
                    <i class="loading spinner icon"></i>
                  </p>
                  <p>
                    <translate translate-context="Sidebar/Player/Error message.Paragraph">You may have a connectivity issue.</translate>
                  </p>
                </div>
                <div class="additional-controls">
                  <track-favorite-icon
                    v-if="$store.state.auth.authenticated"
                    :class="{'inverted': !$store.getters['favorites/isFavorite'](currentTrack.id)}"
                    :track="currentTrack"></track-favorite-icon>
                  <track-playlist-icon
                    v-if="$store.state.auth.authenticated"
                    :class="['inverted']"
                    :track="currentTrack"></track-playlist-icon>
                  <button
                    v-if="$store.state.auth.authenticated"
                    @click="$store.dispatch('moderation/hide', {type: 'artist', target: currentTrack.artist})"
                    :class="['ui', 'really', 'basic', 'circular', 'inverted', 'icon', 'button']"
                    :aria-label="labels.addArtistContentFilter"
                    :title="labels.addArtistContentFilter">
                    <i :class="['eye slash outline', 'basic', 'icon']"></i>
                  </button>
                </div>
                <div class="progress-wrapper">
                  <div class="progress-area" v-if="currentTrack && !errored">
                    <div
                      ref="progress"
                      :class="['ui', 'small', 'orange', {'indicating': isLoadingAudio}, 'progress']"
                      @click="touchProgress">
                      <div class="buffer bar" :data-percent="bufferProgress" :style="{ 'width': bufferProgress + '%' }"></div>
                      <div class="position bar" :data-percent="progress" :style="{ 'width': progress + '%' }"></div>
                    </div>
                  </div>
                  <div class="progress">
                    <template v-if="!isLoadingAudio">
                      <span role="button" class="left floated timer start" @click="setCurrentTime(0)">{{currentTimeFormatted}}</span>
                      <span class="right floated timer total">{{durationFormatted}}</span>
                    </template>
                    <template v-else>
                      <span class="left floated">00:00</span>
                      <span class="right floated">00:00</span>
                    </template>
                  </div>
                </div>
                <div class="player-controls">
                  <div
                    class="control volume-control"
                    v-on:mouseover="showVolume = true"
                    v-on:mouseleave="showVolume = false"
                    v-bind:class="{ active : showVolume }">
                    <span
                      role="button"
                      v-if="volume === 0"
                      :title="labels.unmute"
                      :aria-label="labels.unmute"
                      @click.prevent.stop="unmute">
                      <i class="volume off icon"></i>
                    </span>
                    <span
                      role="button"
                      v-else-if="volume < 0.5"
                      :title="labels.mute"
                      :aria-label="labels.mute"
                      @click.prevent.stop="mute">
                      <i class="volume down icon"></i>
                    </span>
                    <span
                      role="button"
                      v-else
                      :title="labels.mute"
                      :aria-label="labels.mute"
                      @click.prevent.stop="mute">
                      <i class="volume up icon"></i>
                    </span>
                    <input
                      type="range"
                      step="0.05"
                      min="0"
                      max="1"
                      v-model="sliderVolume"
                      v-if="showVolume" />
                  </div>
                  <template v-if="!showVolume">
                    <span
                      role="button"
                      :title="labels.previousTrack"
                      :aria-label="labels.previousTrack"
                      class="control"
                      @click.prevent.stop="$store.dispatch('queue/previous')"
                      :disabled="emptyQueue">
                        <i :class="['ui', 'backward step', {'disabled': emptyQueue}, 'icon']"></i>
                    </span>

                    <span
                      role="button"
                      v-if="!playing"
                      :title="labels.play"
                      :aria-label="labels.play"
                      @click.prevent.stop="togglePlay"
                      class="control">
                        <i :class="['ui', 'play', {'disabled': !currentTrack}, 'icon']"></i>
                    </span>
                    <span
                      role="button"
                      v-else
                      :title="labels.pause"
                      :aria-label="labels.pause"
                      @click.prevent.stop="togglePlay"
                      class="control">
                        <i :class="['ui', 'pause', {'disabled': !currentTrack}, 'icon']"></i>
                    </span>
                    <span
                      role="button"
                      :title="labels.next"
                      :aria-label="labels.next"
                      class="control"
                      @click.prevent.stop="$store.dispatch('queue/next')"
                      :disabled="!hasNext">
                        <i :class="['ui', {'disabled': !hasNext}, 'forward step', 'icon']" ></i>
                    </span>


                    <span
                      role="button"
                      :title="labels.info"
                      :aria-label="labels.info"
                      class="control"
                      @click.prevent.stop="info"
                      :disabled="!currentTrack">
                        <i :class="['ui', {'disabled': !currentTrack}, 'circle info', 'icon']" ></i>
                    </span>
                  </template>
                </div>
                <div class="queue-controls">
                  <span
                      role="button"
                      v-if="looping === 0"
                      :title="labels.loopingDisabled"
                      :aria-label="labels.loopingDisabled"
                      @click.prevent.stop="$store.commit('player/looping', 1)"
                      :disabled="!currentTrack">
                      <i :class="['ui', {'disabled': !currentTrack}, 'step', 'repeat', 'icon']"></i>
                    </span>
                    <span
                      role="button"
                      @click.prevent.stop="$store.commit('player/looping', 2)"
                      :title="labels.loopingSingle"
                      :aria-label="labels.loopingSingle"
                      v-if="looping === 1"
                      class="looping"
                      :disabled="!currentTrack">
                      <i
                        class="repeat icon">
                        <span class="ui circular tiny orange label">1</span>
                      </i>
                    </span>
                    <span
                      role="button"
                      :title="labels.loopingWhole"
                      :aria-label="labels.loopingWhole"
                      v-if="looping === 2"
                      :disabled="!currentTrack"
                      @click.prevent.stop="$store.commit('player/looping', 0)">
                      <i
                        class="repeat orange icon">
                      </i>
                    </span>
                    <span
                      role="button"
                      :disabled="queue.tracks.length === 0"
                      :title="labels.shuffle"
                      :aria-label="labels.shuffle"
                      @click.prevent.stop="shuffle()">
                      <div v-if="isShuffling" class="ui inline shuffling inverted tiny active loader"></div>
                      <i v-else :class="['ui', 'random', {'disabled': queue.tracks.length === 0}, 'icon']" ></i>
                    </span>
                  <div class="position">
                    <translate translate-context="Sidebar/Queue/Text" :translate-params="{index: queue.currentIndex + 1, length: queue.tracks.length}">
                      %{ index } of %{ length }
                    </translate>
                  </div>
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
<script>
import { mapState, mapGetters, mapActions } from "vuex"
import $ from 'jquery'
import moment from "moment"
import lodash from '@/lodash'
import draggable from "vuedraggable"
import time from "@/utils/time"

import TrackFavoriteIcon from "@/components/favorites/TrackFavoriteIcon"
import TrackPlaylistIcon from "@/components/playlists/TrackPlaylistIcon"


export default {
  components: {
    TrackFavoriteIcon,
    TrackPlaylistIcon,
    draggable
  },
  data () {
    return {
      showVolume: false,
      isShuffling: false,
      tracksChangeBuffer: null,
      time
    }
  },
  mounted () {
    let self = this
    this.$nextTick(() => {
      $(this.$el).find('.ui.sticky').sticky({context: '#queue-grid'})
      $(this.$el).find('.controls-dropdown').dropdown({action: 'hide'})
      this.scrollToCurrent()
    })
  },
  computed: {
    ...mapState({
      currentIndex: state => state.queue.currentIndex,
      playing: state => state.player.playing,
      isLoadingAudio: state => state.player.isLoadingAudio,
      volume: state => state.player.volume,
      looping: state => state.player.looping,
      duration: state => state.player.duration,
      bufferProgress: state => state.player.bufferProgress,
      errored: state => state.player.errored,
      currentTime: state => state.player.currentTime,
      queue: state => state.queue
    }),
    ...mapGetters({
      currentTrack: "queue/currentTrack",
      hasNext: "queue/hasNext",
      emptyQueue: "queue/isEmpty",
      durationFormatted: "player/durationFormatted",
      currentTimeFormatted: "player/currentTimeFormatted",
      progress: "player/progress"
    }),
    tracks: {
      get() {
        return this.$store.state.queue.tracks
      },
      set(value) {
        this.tracksChangeBuffer = value
      }
    },
    labels () {
      return {
        queue: this.$pgettext('*/*/*', 'Queue'),
        duration: this.$pgettext('*/*/*', 'Duration'),
      }
    },
    timeLeft () {
      let seconds = lodash.sum(
        this.queue.tracks.slice(this.queue.currentIndex).map((t) => {
          return (t.uploads || []).map((u) => {
            return u.duration || 0
          })[0] || 0
        })
      )
      return moment(this.$store.state.ui.lastDate).add(seconds, 'seconds').fromNow(true)
    },
    sliderVolume: {
      get () {
        return this.volume
      },
      set (v) {
        this.$store.commit("player/volume", v)
      }
    }
  },
  methods: {
    ...mapActions({
      cleanTrack: "queue/cleanTrack",
      mute: "player/mute",
      unmute: "player/unmute",
      clean: "queue/clean",
      toggleMute: "player/toggleMute",
      togglePlay: "player/togglePlay",
    }),
    reorder: function(event) {
      this.$store.commit("queue/reorder", {
        tracks: this.tracksChangeBuffer,
        oldIndex: event.oldIndex,
        newIndex: event.newIndex
      })
    },
    scrollToCurrent() {
      let current = $(this.$el).find('.queue-item.active')[0]
      if (!current) {
        return
      }
      const elementRect = current.getBoundingClientRect();
      const absoluteElementTop = elementRect.top + window.pageYOffset;
      const middle = absoluteElementTop - (window.innerHeight / 2);
      window.scrollTo(0, middle);

    },
    touchProgress(e) {
      // todo
    },
    setCurrentTime(e) {
      // todo
    },
    shuffle() {
      let disabled = this.queue.tracks.length === 0
      if (this.isShuffling || disabled) {
        return
      }
      let self = this
      let msg = this.$pgettext('Content/Queue/Message', "Queue shuffled!")
      this.isShuffling = true
      setTimeout(() => {
        self.$store.dispatch("queue/shuffle", () => {
          self.isShuffling = false
          self.$store.commit("ui/addMessage", {
            content: msg,
            date: new Date()
          })
        })
      }, 100)
    },
  },
  watch: {
    '$store.state.queue.currentIndex': {
      handler () {
        this.$nextTick(() => {
          this.scrollToCurrent()
        })
      },
      immediate: true
    }
  }
}
</script>
<style lang="scss" scoped>
@import "../style/vendor/media";

.main > .button {
  position: fixed;
  top: 1em;
  right: 1em;
  z-index: 9999999;
}
.stripe.segment:not(.player-focused) #queue-grid .current-track {
  @include media("<desktop") {
    display: none;
  }
}
.player-focused .grid > .ui.queue-column {
  @include media("<desktop") {
    display: none;
  }
}
.ui.table > tbody > tr > td.controls {
  text-align: right;
}
.ui.table > tbody > tr > td {
  border: none;
}
td:first-child {
  padding-left: 1em !important;
}
td:last-child {
  padding-right: 1em !important;
}
.image-cell {
  width: 4em;
}
.queue.segment > .container {
  margin: 0 !important;
}
#queue-grid > .text.container {
  padding: 0;
  margin: 0 !important;
}
.handle {
  @include media("<desktop") {
    display: none;
  }
}
.duration-cell {
  @include media("<tablet") {
    display: none;
  }
}

.sticky .header .content {
  display: block;
}
.sticky.segment {
  padding-left: 0;
  padding-right: 0;
}
.current-track #player {
  padding: 1em;
  text-align: center;
  display: flex;
  position: fixed;
  height: 100vh;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  bottom: 0;
  top: 0;
  @include media("<desktop") {
    width: 100%;
    width: 100vw;
    left: 0;
    right: 0;
    justify-content: center;
    > .image {
      max-height: 50vh;
    }
  }
  > *:not(.image) {
    width: 100%;
  }
}
.progress-area {
  overflow: hidden;
}
.ui.progress .buffer.bar {
  position: absolute;
  background-color: rgba(255, 255, 255, 0.15);
}
.ui.progress:not([data-percent]):not(.indeterminate)
  .bar.position:not(.buffer) {
  background: #ff851b;
}

.indicating.progress .bar {
  left: -46px;
  width: 200% !important;
  color: grey;
  background: repeating-linear-gradient(
    -55deg,
    grey 1px,
    grey 10px,
    transparent 10px,
    transparent 20px
  ) !important;

  animation-name: MOVE-BG;
  animation-duration: 2s;
  animation-timing-function: linear;
  animation-iteration-count: infinite;
}
.ui.progress {
  margin: 0.5rem 0;
}
.progress {
  cursor: pointer;
  .bar {
    min-width: 0 !important;
  }
}
</style>

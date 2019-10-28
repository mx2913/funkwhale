<template>
  <section class="main pusher" :aria-label="labels.queue">
    <div class="ui vertical stripe queue segment">
      <div class="ui fluid container">
        <div class="ui stackable grid" id="queue-grid">
          <div class="ui text container">
            <div class="ui sticky basic clearing fixed-header segment">
              <h1 class="ui header">
                <div class="content">
                  <button @click="$store.commit('ui/queueExpanded', false)" class="ui right floated small basic button">
                    <i class="close icon"></i>
                    <translate translate-context="*/*/Button.Label/Verb">Close</translate>
                  </button>
                  <button class="ui right floated small basic button" @click="$store.dispatch('queue/clean'); $store.commit('ui/queueExpanded', false)">
                    <translate translate-context="Content/Library/Button.Label">Clear</translate>
                  </button>
                  {{ labels.queue }}
                  <div class="sub header">
                    <div>
                      <translate translate-context="Sidebar/Queue/Text" :translate-params="{index: queue.currentIndex + 1, length: queue.tracks.length}">
                        Track %{ index } of %{ length }
                      </translate> -
                      <span :title="labels.duration">
                        {{ timeLeft }}
                      </span>
                    </div>
                  </div>
                </div>
              </h1>
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
                    <i class="bars icon"></i>
                  </td>
                  <td class="image-cell">
                    <img class="ui mini image" v-if="track.album.cover && track.album.cover.original" :src="$store.getters['instance/absoluteUrl'](track.album.cover.small_square_crop)">
                    <img class="ui mini image" v-else src="../assets/audio/default-cover.png">
                  </td>
                  <td colspan="4">
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
          <div class="ui six wide column current-track">
            <div class="ui sticky basic segment">
              <template v-if="currentTrack">
                <img class="ui image" v-if="currentTrack.album.cover && currentTrack.album.cover.original" :src="$store.getters['instance/absoluteUrl'](currentTrack.album.cover.square_crop)">
                <img class="ui image" v-else src="../assets/audio/default-cover.png">
                <h2 class="ui header">
                  <div class="content">
                    <router-link :title="currentTrack.title" :to="{name: 'library.tracks.detail', params: {id: currentTrack.id }}">
                      {{ currentTrack.title | truncate(50) }}
                    </router-link>
                    <div class="sub header">
                      <router-link class="artist" :title="currentTrack.artist.name" :to="{name: 'library.artists.detail', params: {id: currentTrack.artist.id }}">
                        {{ currentTrack.artist.name | truncate(40) }}
                      </router-link> /
                      <router-link class="album" :title="currentTrack.album.title" :to="{name: 'library.albums.detail', params: {id: currentTrack.album.id }}">
                        {{ currentTrack.album.title | truncate(40) }}
                      </router-link>
                    </div>
                  </div>
                </h2>
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


export default {
  components: {
    draggable
  },
  data () {
    return {
      tracksChangeBuffer: null,
      time
    }
  },
  mounted () {
    let self = this
    this.$nextTick(() => {
      $(this.$el).find('.ui.sticky').sticky({context: '#queue-grid'})
    })
  },
  computed: {
    ...mapState({
      queue: state => state.queue,
    }),
    ...mapGetters({
      currentTrack: "queue/currentTrack",
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
  },
  methods: {
    ...mapActions({
      cleanTrack: "queue/cleanTrack"
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
  },
  watch: {
    '$route.fullPath': {
      handler (v, o) {
        if (o === '/') {
          // page load
          return
        }
        this.$store.commit('ui/queueExpanded', false)
      },
      deep: true
    },
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


#queue-grid .current-track {
  display: none;
  @include media(">tablet") {
    display: block;
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
</style>

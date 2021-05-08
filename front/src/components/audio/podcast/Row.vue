<template>
  <div
    :class="[
      { active: currentTrack && track.id === currentTrack.id },
      'track-row podcast row',
    ]"
    @mouseover="hover = track.id"
    @mouseleave="hover = null"
    @dblclick="activateTrack(track, index)"
  >
    <div
      v-if="showArt"
      class="image left floated column"
      role="button"
      @click.prevent.exact="activateTrack(track, index)"
    >
      <img
        alt=""
        class="ui artist-track mini image"
        v-if="
          track.album && track.album.cover && track.album.cover.urls.original
        "
        v-lazy="
          $store.getters['instance/absoluteUrl'](
            track.album.cover.urls.medium_square_crop
          )
        "
      />
      <img
        alt=""
        class="ui artist-track mini image"
        v-else-if="
          track.cover && track.cover.urls.original
        "
        v-lazy="
          $store.getters['instance/absoluteUrl'](
            track.cover.urls.medium_square_crop
          )
        "
      />
      <img
        alt=""
        class="ui artist-track mini image"
        v-else-if="
          track.artist && track.artist.cover && track.album.cover.urls.original
        "
        v-lazy="
          $store.getters['instance/absoluteUrl'](
            track.cover.urls.medium_square_crop
          )
        "
      />
      <img
        alt=""
        class="ui artist-track mini image"
        v-else
        src="../../../assets/audio/default-cover.png"
      />
    </div>
    <div tabindex=0 class="content left floated column">
      <p class="podcast-episode-title ellipsis">{{ track.title }}</p>
      <p class="podcast-episode-meta">
      An episode description, with all its twists and turns!
      This episode focuses on something I'm sure, but nobody really knows what it's focusing on.</p>
    </div>
    <div v-if="displayActions" class="meta right floated column">
      <play-button
        id="playmenu"
        class="play-button basic icon"
        :dropdown-only="true"
        :is-playable="track.is_playable"
        :dropdown-icon-classes="[
          'ellipsis',
          'vertical',
          'large really discrete',
        ]"
        :track="track"
      ></play-button>
    </div>
  </div>
</template>

<script>
import PlayIndicator from "@/components/audio/track/PlayIndicator";
import { mapActions, mapGetters } from "vuex";
import PlayButton from "@/components/audio/PlayButton";

export default {
  props: {
    tracks: Array,
    showAlbum: { type: Boolean, required: false, default: true },
    showArtist: { type: Boolean, required: false, default: true },
    showPosition: { type: Boolean, required: false, default: false },
    showArt: { type: Boolean, required: false, default: true },
    search: { type: Boolean, required: false, default: false },
    filters: { type: Object, required: false, default: null },
    nextUrl: { type: String, required: false, default: null },
    displayActions: { type: Boolean, required: false, default: true },
    showDuration: { type: Boolean, required: false, default: true },
    index: { type: Number, required: true },
    track: { type: Object, required: true },
  },

  data() {
    return {
      hover: null,
    }
  },

  components: {
    PlayIndicator,
    PlayButton,
  },

  computed: {
    ...mapGetters({
      currentTrack: "queue/currentTrack",
    }),

    isPlaying() {
      return this.$store.state.player.playing;
    },
  },

  methods: {

    prettyPosition(position, size) {
      var s = String(position);
      while (s.length < (size || 2)) {
        s = "0" + s;
      }
      return s;
    },

    ...mapActions({
      resumePlayback: "player/resumePlayback",
      pausePlayback: "player/pausePlayback",
    }),
  },
};
</script>

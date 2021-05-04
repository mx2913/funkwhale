<template>
  <div
    :class="[
      { active: currentTrack && track.id === currentTrack.id },
      'track-row row',
    ]"
    @mouseover="track.hover = true"
    @mouseleave="track.hover = false"
    @dblclick="activateTrack(track, index)"
  >
    <div class="actions one wide left floated column">
      <play-indicator
        v-if="
          !$store.state.player.isLoadingAudio &&
          currentTrack &&
          isPlaying &&
          track.id === currentTrack.id &&
          !track.hover
        "
      >
      </play-indicator>
      <button
        v-else-if="
          currentTrack &&
          !isPlaying &&
          track.id === currentTrack.id &&
          !track.hover
        "
        class="ui really tiny basic icon button play-button paused"
      >
        <i class="pause icon" />
      </button>
      <button
        v-else-if="
          currentTrack &&
          isPlaying &&
          track.id === currentTrack.id &&
          track.hover
        "
        class="ui really tiny basic icon button play-button"
        @click.prevent.exact="pausePlayback"
      >
        <i class="pause icon" />
      </button>
      <button
        v-else-if="
          currentTrack &&
          !isPlaying &&
          track.id === currentTrack.id &&
          track.hover
        "
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
      <span class="track-position" v-else-if="showPosition">
        {{ prettyPosition(track.position) }}
      </span>
    </div>
    <div v-if="showArt" class="image left floated column">
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
        v-else
        src="../../../assets/audio/default-cover.png"
      />
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
      <a v-else @click.prevent.exact="replacePlay(tracks, index)">
        {{ track.title }}
      </a>
    </div>
    <div v-if="showAlbum" class="content ellipsis left floated column">
      <router-link
        :to="{ name: 'library.albums.detail', params: { id: track.album.id } }"
        >{{ track.album.title }}</router-link
      >
    </div>
    <div v-if="showArtist" class="content ellipsis left floated column">
      <router-link
        class="artist link"
        :to="{
          name: 'library.artists.detail',
          params: { id: track.artist.id },
        }"
        >{{ track.artist.name }}</router-link
      >
    </div>
    <div
      v-if="$store.state.auth.authenticated"
      class="meta right floated column"
    >
      <track-favorite-icon
        class="tiny"
        :border="false"
        :track="track"
      ></track-favorite-icon>
    </div>
    <div v-if="showDuration" class="meta right floated column">
      <human-duration
        v-if="track.uploads[0] && track.uploads[0].duration"
        :duration="track.uploads[0].duration"
      ></human-duration>
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
import TrackFavoriteIcon from "@/components/favorites/TrackFavoriteIcon";
import PlayButton from "@/components/audio/PlayButton";

export default {
  props: {
    tracks: Array,
    showAlbum: { type: Boolean, required: false, default: true },
    showArtist: { type: Boolean, required: false, default: true },
    trackOnly: { type: Boolean, required: false, default: false },
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

  components: {
    PlayIndicator,
    TrackFavoriteIcon,
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
    replacePlay(tracks, trackIndex) {
      this.$store.dispatch("queue/clean");
      this.$store.dispatch("queue/appendMany", { tracks: tracks }).then(() => {
        this.$store.dispatch("queue/currentIndex", trackIndex);
      });
    },

    prettyPosition(position, size) {
      var s = String(position);
      while (s.length < (size || 2)) {
        s = "0" + s;
      }
      return s;
    },

    activateTrack(track, index) {
      if (
        this.currentTrack &&
        this.isPlaying &&
        track.id === this.currentTrack.id
      ) {
        this.pausePlayback();
      } else if (
        this.currentTrack &&
        !this.isPlaying &&
        track.id === this.currentTrack.id
      ) {
        this.resumePlayback();
      } else {
        this.replacePlay(this.tracks, index);
      }
    },

    ...mapActions({
      resumePlayback: "player/resumePlayback",
      pausePlayback: "player/pausePlayback",
    }),
  },
};
</script>

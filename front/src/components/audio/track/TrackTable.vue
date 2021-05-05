<template>
  <div>
    <!-- Show the search bar if search is true -->
    <inline-search-bar
      v-model="query"
      v-if="search"
      @search="
        additionalTracks = [];
        fetchData();
      "
    ></inline-search-bar>
    <div class="ui hidden divider"></div>

    <!-- Add a header if needed -->

    <slot name="header"></slot>

    <!-- Show a message if no tracks are available -->

    <slot v-if="!isLoading && allTracks.length === 0" name="empty-state">
      <empty-state
        @refresh="fetchData('tracks/')"
        :refresh="true"
      ></empty-state>
    </slot>
    <div v-else>
      <div
        :class="['track-table', 'ui', 'unstackable', 'grid', 'tablet-and-up']"
      >
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
          <div
            v-if="$store.state.auth.authenticated"
            class="meta right floated column"
          ></div>
          <div v-if="showDuration" class="meta right floated column">
            <i class="clock outline icon" style="padding: 0.5rem" />
          </div>
          <div v-if="displayActions" class="meta right floated column"></div>
        </div>

        <!-- For each item, build a row -->

        <track-row
          v-for="(track, index) in allTracks"
          :track="track"
          :key="track.id"
          :index="index"
          :tracks="allTracks"
          :show-album="showAlbum"
          :show-artist="showArtist"
          :show-position="showPosition"
          :show-art="showArt"
          :display-actions="displayActions"
          :show-duration="showDuration"
        ></track-row>
      </div>
    </div>

    <div
      :class="['track-table', 'ui', 'unstackable', 'grid', 'tablet-and-below']"
    >
      <div v-if="isLoading" class="ui inverted active dimmer">
        <div class="ui loader"></div>
      </div>

      <!-- For each item, build a row -->

      <track-mobile-row
        v-for="(track, index) in allTracks"
        :track="track"
        :key="track.id"
        :index="index"
        :tracks="allTracks"
        :show-position="showPosition"
        :show-art="showArt"
        :show-duration="showDuration"
        :is-artist="isArtist"
        :is-album="isAlbum"
      ></track-mobile-row>
    </div>
  </div>
</template>

<script>
import _ from "@/lodash";
import axios from "axios";
import TrackRow from "@/components/audio/track/TrackRow";
import TrackMobileRow from "@/components/audio/track/TrackMobileRow";

export default {
  components: {
    TrackRow,
    TrackMobileRow,
  },

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
    isArtist: { type: Boolean, required: false, default: false },
    isAlbum: { type: Boolean, required: false, default: false },
  },

  data() {
    return {
      fetchDataUrl: this.nextUrl,
      isLoading: false,
      additionalTracks: [],
      query: "",
    };
  },

  computed: {
    allTracks() {
      return (this.tracks || []).concat(this.additionalTracks);
    },

    labels() {
      return {
        title: this.$pgettext("*/*/*/Noun", "Title"),
        album: this.$pgettext("*/*/*/Noun", "Album"),
        artist: this.$pgettext("*/*/*/Noun", "Artist"),
      };
    },
  },
  methods: {
    fetchData(url) {
      if (!url) {
        return;
      }
      this.isLoading = true;
      let self = this;
      let params = _.clone(this.filters);
      params.page_size = this.limit;
      params.page = this.page;
      params.include_channels = true;
      axios.get(url, { params: params }).then(
        (response) => {
          self.nextPage = response.data.next;
          self.isLoading = false;
          self.objects = response.data.results;
          self.count = response.data.count;
          self.$emit("fetched", response.data);
        },
        (error) => {
          self.isLoading = false;
          self.errors = error.backendErrors;
        }
      );
    },
  },

  created() {
    if (!this.tracks) {
      this.fetchData("tracks/");
    }

    this.allTracks.forEach((track) => {
      this.$set(track, "hover", false);
    });
  },
};
</script>

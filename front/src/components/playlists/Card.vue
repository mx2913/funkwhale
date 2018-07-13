<template>
  <div class="ui card">
    <div class="ui top attached icon button" :style="coversStyle">
      <play-button class="orange" :playlist="playlist"><translate>Play all</translate></play-button>
    </div>
    <div class="content">
      <div class="header">
        <router-link class="discrete link" :to="{name: 'library.playlists.detail', params: {id: playlist.id }}">
          {{ playlist.name }}
        </router-link>
      </div>
      <div class="meta">
        <human-date :date="playlist.modification_date" />
      </div>
      <div class="meta">
        <duration :seconds="playlist.duration" />
      </div>
    </div>
    <div class="extra content">
      <user-link :user="playlist.user" class="left floated" />
      <span class="right floated">
        <translate
          translate-plural="%{ count } tracks"
          :translate-n="playlist.tracks_count"
          :translate-params="{count: playlist.tracks_count}">
          %{ count} track
        </translate>&nbsp;
        <i class="sound icon"></i>
      </span>
    </div>
  </div>
</template>

<script>
import PlayButton from '@/components/audio/PlayButton'

export default {
  props: ['playlist'],
  components: {
    PlayButton
  },
  computed: {
    coversStyle () {
      let self = this
      let urls = this.playlist.album_covers.map((url) => {
        url = self.$store.getters['instance/absoluteUrl'](url)
        return `url("${url}")`
      }).slice(0, 4)
      return {
        'background-image': urls.join(', ')
      }
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

.attached.button {
  background-color: rgb(243, 244, 245);
  background-size: 25% ;
  background-repeat: no-repeat;
  background-origin: border-box;
  background-position: 0 0, 33.33% 0, 66.67% 0, 100% 0;
  /* background-position: 0 0, 50% 0, 100% 0; */
  /* background-position: 0 0, 25% 0, 50% 0, 75% 0, 100% 0; */
  font-size: 2em;
  box-shadow: none !important;
}

</style>

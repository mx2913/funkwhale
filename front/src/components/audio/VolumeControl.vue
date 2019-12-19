<template>
   <span class="volume-control">
    <span
      role="button"
      v-if="sliderVolume === 0"
      :title="labels.unmute"
      :aria-label="labels.unmute"
      @click.prevent.stop="unmute">
      <i class="volume off icon"></i>
    </span>
    <span
      role="button"
      v-else-if="sliderVolume < 0.5"
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
      @click.prevent.stop=""
      v-model="sliderVolume" />
  </span>
</template>
<script>
import { mapState, mapGetters, mapActions } from "vuex"

export default {
  computed: {
    sliderVolume: {
      get () {
        return this.$store.state.player.volume
      },
      set (v) {
        this.$store.commit("player/volume", v)
      }
    },
    labels () {
      return {
        unmute: this.$pgettext('Sidebar/Player/Icon.Tooltip/Verb', "Unmute"),
        mute: this.$pgettext('Sidebar/Player/Icon.Tooltip/Verb', "Mute"),

      }
    }
  },
  methods: {
    ...mapActions({
      mute: "player/mute",
      unmute: "player/unmute",
      toggleMute: "player/toggleMute",
    }),

  }
}
</script>
<style lang="scss" scoped>

.volume-control {
  display: flex;
  line-height: inherit;
  align-items: center;
  input {
    max-width: 5em;
  }
}
</style>

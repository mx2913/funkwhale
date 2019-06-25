<template>
  <modal @update:show="$emit('update:show', $event)" :show="show">
    <header class="header">
      <translate translate-context="*/*/*/Noun">Keyboard shortcuts</translate>
    </header>
    <section class="scrolling content">
      <table
        class="ui compact collapsing basic table"
        v-for="section in sections"
        :key="section.title">
      <caption>{{ section.title }}</caption>
      <tbody>
        <tr v-for="shortcut in section.shortcuts" :key="shortcut.summary">
          <td>{{ shortcut.summary }}</td>
          <td><span class="ui label">{{ shortcut.key }}</span></td>
        </tr>
      </tbody>
      </table>
    </section>
    <footer class="actions">
      <div class="ui cancel button"><translate translate-context="Popup/Keyboard shortcuts/Button.Label/Verb">Close</translate></div>
    </footer>
  </modal>
</template>

<script>
import Modal from '@/components/semantic/Modal'

export default {
  props: ['show'],
  components: {
    Modal,
  },
  computed: {
    sections () {
      return [
        {
          title: this.$pgettext('Popup/Keyboard shortcuts/Title', 'General shortcuts'),
          shortcuts: [
            {
              key: 'h',
              summary: this.$pgettext('Popup/Keyboard shortcuts/Table.Label/Verb', 'Show available keyboard shortcuts')
            },
            {
              key: 'shift f',
              summary: this.$pgettext('Popup/Keyboard shortcuts/Table.Label/Verb', 'Focus searchbar')
            },
            {
              key: 'esc',
              summary: this.$pgettext('Popup/Keyboard shortcuts/Table.Label/Verb', 'Unfocus searchbar')
            },
          ]
        },
        // space.prevent.exact="togglePlay"
        // ctrl.left.prevent.exact="previous"
        // ctrl.right.prevent.exact="next"
        // right.prevent.exact="$store.dispatch('player/updateProgress', (currentTime + 1))"
        // left.prevent.exact="$store.dispatch('player/updateProgress', (currentTime - 1))"
        // ctrl.down.prevent.exact="$store.commit('player/incrementVolume', -0.1)"
        // ctrl.up.prevent.exact="$store.commit('player/incrementVolume', 0.1)"
        // m.prevent.exact="toggleMute"
        // l.prevent.exact="$store.commit('player/toggleLooping')"
        // s.prevent.exact="shuffle"
        // q.prevent.exact="clean"
        // f.prevent.exact="$store.dispatch('favorites/toggle', currentTrack.id)"

        {
          title: this.$pgettext('Popup/Keyboard shortcuts/Title', 'Audio player shortcuts'),
          shortcuts: [
            {
              key: 'space',
              summary: this.$pgettext('Popup/Keyboard shortcuts/Table.Label/Verb', 'Pause/play the current track')
            },
            {
              key: 'shift left',
              summary: this.$pgettext('Popup/Keyboard shortcuts/Table.Label/Verb', 'Play previous track')
            },
            {
              key: 'shift right',
              summary: this.$pgettext('Popup/Keyboard shortcuts/Table.Label/Verb', 'Play next track')
            },
            {
              key: 'left',
              summary: this.$pgettext('Popup/Keyboard shortcuts/Table.Label/Verb', 'Seek backwards')
            },
            {
              key: 'right',
              summary: this.$pgettext('Popup/Keyboard shortcuts/Table.Label/Verb', 'Seek forwards')
            },
            {
              key: 'shift up',
              summary: this.$pgettext('Popup/Keyboard shortcuts/Table.Label/Verb', 'Increase volume')
            },
            {
              key: 'shift down',
              summary: this.$pgettext('Popup/Keyboard shortcuts/Table.Label/Verb', 'Decrease volume')
            },
            {
              key: 'm',
              summary: this.$pgettext('Popup/Keyboard shortcuts/Table.Label/Verb', 'Toggle mute')
            },
            {
              key: 'l',
              summary: this.$pgettext('Popup/Keyboard shortcuts/Table.Label/Verb', 'Toggle queue looping')
            },
            {
              key: 's',
              summary: this.$pgettext('Popup/Keyboard shortcuts/Table.Label/Verb', 'Shuffle queue')
            },
            {
              key: 'q',
              summary: this.$pgettext('Popup/Keyboard shortcuts/Table.Label/Verb', 'Clear queue')
            },
            {
              key: 'f',
              summary: this.$pgettext('Popup/Keyboard shortcuts/Table.Label/Verb', 'Toggle favorite')
            },
          ]
        }
      ]
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>


import Vue from 'vue'
import Vuex from 'vuex'
import EmbedFrame from './EmbedFrame'
import locales from '@/locales'
import player from '@/store/player'
import queue from '@/store/queue'
import instance from '@/store/instance'
import GetTextPlugin from 'vue-gettext'

//Vue.config.productionTip = false
Vue.use(Vuex)

const store = new Vuex.Store({
  modules: {
    player,
    queue,
    instance
  }
})

let availableLanguages = (function () {
  let l = {}
  locales.locales.forEach(c => {
    l[c.code] = c.label
  })
  return l
})()
let defaultLanguage = 'en_US'
//if (availableLanguages[store.state.ui.currentLanguage]) {
//  defaultLanguage = store.state.ui.currentLanguage
//}
Vue.use(GetTextPlugin, {
  availableLanguages: availableLanguages,
  defaultLanguage: defaultLanguage,
  // cf https://github.com/Polyconseil/vue-gettext#configuration
  // not recommended but this is fixing weird bugs with translation nodes
  // not being updated when in v-if/v-else clauses
  autoAddKeyAttributes: true,
  languageVmMixin: {
    computed: {
      currentKebabCase: function () {
        return this.current.toLowerCase().replace('_', '-')
      }
    }
  },
  translations: {},
  silent: true
})

/* eslint-disable no-new */
new Vue({
  el: '#app',
  store,
  render (h) {
    return h('EmbedFrame')
  },
  components: { EmbedFrame }
})

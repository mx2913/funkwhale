<template>
  <div class="wrapper">
    <div class="ui two column grid">
      <div class="column">
        <h3 v-if="!!this.$slots.title" class="ui header">
          <slot name="title"></slot>
        </h3>
        <slot></slot>
      </div>
      <div class="column">
        <button :class="['right', 'floated', 'circular', 'icon', 'ui', {'disabled': !nextPage}, 'button',]" @click.prevent="fetchData(nextPage)">
          <i class="right arrow icon"></i>
        </button>
        <button :class="['right', 'floated', 'circular', 'icon', 'ui', {'disabled': !previousPage}, 'button',]" @click.prevent="fetchData(previousPage)">
          <i class="left arrow icon"></i>
        </button>
      </div>
    </div>
    <div class="ui hidden divider"></div>
    <div class="ui app-cards cards">
      <div v-if="isLoading" class="ui inverted active dimmer">
        <div class="ui loader"></div>
      </div>
      <album-card v-for="album in albums" :album="album" :key="album.id" />
    </div>
    <template v-if="!isLoading && albums.length === 0">
      <empty-state @refresh="fetchData('albums/')" :refresh="true"></empty-state>
    </template>
  </div>
</template>

<script>

import axios from 'axios'
import AlbumCard from '@/components/audio/album/Card'
import $ from 'jquery'

export default {
  components: {
    AlbumCard,
  },
  props: {
    limit: {type: Number, default: 4},
    filters: {type: Object, required: true},
  },
  data() {
    return {
      albums: [],
      count: 0,
      isLoading: false,
      errors: null,
      previousPage: null,
      nextPage: null,
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    fetchData (url) {
      url = url || 'albums/'
      this.isLoading = true
      let self = this
      let params = {q: this.query, ...this.filters}
      params.page_size = this.limit
      params.offset = this.offset
      axios.get(url, {params: params}).then((response) => {
        self.previousPage = response.data.previous
        self.nextPage = response.data.next
        self.isLoading = false
        self.albums = [...response.data.results]
        self.count = response.data.count
      }, error => {
        self.isLoading = false
        self.errors = error.backendErrors
      })
    },
  },
  mounted() {
    $('.component-album-card')
      .transition('scale')
  }
}
</script>
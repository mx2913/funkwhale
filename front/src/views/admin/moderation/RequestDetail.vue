<template>
  <main>
    <div
      v-if="isLoading"
      class="ui vertical segment"
    >
      <div :class="['ui', 'centered', 'active', 'inline', 'loader']" />
    </div>
    <template v-if="user_request">
      <div class="ui vertical stripe segment">
        <user-request-card :user-request="user_request" />
      </div>
    </template>
  </main>
</template>

<script>
import axios from 'axios'

import UserRequestCard from '@/components/manage/moderation/UserRequestCard'

export default {
  components: {
    UserRequestCard
  },
  props: { id: { type: Number, required: true } },
  data () {
    return {
      isLoading: true,
      user_request: null
    }
  },
  created () {
    this.fetchData()
  },
  methods: {
    fetchData () {
      const self = this
      this.isLoading = true
      const url = `manage/moderation/requests/${this.id}/`
      axios.get(url).then(response => {
        self.user_request = response.data
        self.isLoading = false
      })
    }
  }
}
</script>

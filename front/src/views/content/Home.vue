<script setup lang="ts">
import { humanSize } from '~/utils/filters'
import { useI18n } from 'vue-i18n'
import { computed } from 'vue'
import { useStore } from '~/store'

import { FwButton } from '@funkwhale/ui'

const { t } = useI18n()

const labels = computed(() => ({
  title: t('views.content.Home.title')
}))

const store = useStore()
const quota = computed(() => store.state.instance.settings.users.upload_quota.value)
const defaultQuota = computed(() => humanSize(quota.value * 1e6))
</script>

<template>
  <section
    v-title="labels.title"
    class="ui vertical aligned stripe segment"
  >
    <div class="ui text container">
      <h1>{{ labels.title }}</h1>
      <p>
        <strong>{{ $t('views.content.Home.help.uploadQuota', { quota: defaultQuota }) }}</strong>
      </p>
      <div class="ui segment">
        <h2>
          <i class="feed icon" />&nbsp;
          {{ $t('views.content.Home.header.channel') }}
        </h2>
        <p>
          {{ $t('views.content.Home.description.channel.1') }}&#32;{{ $t('views.content.Home.description.channel.2') }}
        </p>
        <fw-button
          color="primary"
          @click="$router.push({name: 'profile.overview', params: {username: store.state.auth.username}, hash: '#channels'})"
        >
          {{ $t('views.content.Home.button.start') }}
        </fw-button>
      </div>
      <div class="ui segment">
        <h2>
          <i class="cloud icon" />&nbsp;
          {{ $t('views.content.Home.header.upload') }}
        </h2>
        <p>
          {{ $t('views.content.Home.description.upload') }}
        </p>
        <fw-button
          color="primary"
          @click="$router.push({name: 'content.libraries.index'})"
        >
          {{ $t('views.content.Home.button.start') }}
        </fw-button>
      </div>
      <div class="ui segment">
        <h2>
          <i class="download icon" />&nbsp;
          {{ $t('views.content.Home.header.follow') }}
        </h2>
        <p>
          {{ $t('views.content.Home.description.follow') }}
        </p>
        <fw-button
          color="primary"
          @click="$router.push({name: 'content.remote.index'})"
        >
          {{ $t('views.content.Home.button.start') }}
        </fw-button>
      </div>
    </div>
  </section>
</template>

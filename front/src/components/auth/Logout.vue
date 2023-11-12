<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { FwButton } from '@funkwhale/ui'

const { t } = useI18n()
const labels = computed(() => ({
  title: t('components.auth.Logout.title')
}))
</script>

<template>
  <main
    v-title="labels.title"
    class="main pusher"
  >
    <section class="ui vertical stripe segment">
      <div
        v-if="$store.state.auth.authenticated"
        class="ui small text container"
      >
        <h2>
          {{ $t('components.auth.Logout.header.confirm') }}
        </h2>
        <p>
          {{ $t('components.auth.Logout.message.loggedIn', { username: $store.state.auth.username }) }}
        </p>
        <fw-button
          color="secondary"
          @click="$store.dispatch('auth/logout')"
        >
          {{ $t('components.auth.Logout.button.logout') }}
        </fw-button>
      </div>
      <div
        v-else
        class="ui small text container"
      >
        <h2>
          {{ $t('components.auth.Logout.header.unauthenticated') }}
        </h2>
        <fw-button
          color="primary"
          @click="$router.push('/login')"
        >
          {{ $t('components.auth.Logout.link.login') }}
        </fw-button>
      </div>
    </section>
  </main>
</template>

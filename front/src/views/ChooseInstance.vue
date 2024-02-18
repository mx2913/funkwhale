<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'
import { TAURI_DEFAULT_INSTANCE_URL } from '~/store/instance'
import { uniq } from 'lodash-es'
import { useRoute, useRouter } from 'vue-router'

import axios from 'axios'

const instanceUrl = ref('')

const store = useStore()
const suggestedInstances = computed(() => {
  const serverUrl = store.state.instance.frontSettings.defaultServerUrl
  return uniq([
    store.state.instance.instanceUrl,
    ...store.state.instance.knownInstances,
    serverUrl.endsWith('/') ? serverUrl : serverUrl + '/',
    store.getters['instance/defaultInstance']
  ]).filter(url => url !== TAURI_DEFAULT_INSTANCE_URL)
})

watch(() => store.state.instance.instanceUrl, () => store.dispatch('instance/fetchSettings'))

const route = useRoute()
const router = useRouter()

const { t } = useI18n()
const isError = ref(false)
const isLoading = ref(false)
const checkAndSwitch = async (url: string) => {
  isError.value = false
  isLoading.value = true

  try {
    const instanceUrl = new URL(url.startsWith('https://') || url.startsWith('http://') ? url : `https://${url}`).origin
    await axios.get(instanceUrl + '/api/v1/instance/nodeinfo/2.0/')

    store.commit('ui/addMessage', {
      content: t('views.ChooseInstance.message.newUrl', { url: instanceUrl }),
      date: new Date()
    })

    await nextTick()
    await store.dispatch('instance/setUrl', instanceUrl)
    router.push(route.query.next as string || '/')
  } catch (error) {
    isError.value = true
  }

  isLoading.value = false
}

const isTauriInstance = computed(() => store.getters['instance/url'].href === TAURI_DEFAULT_INSTANCE_URL)
</script>

<template>
  <div class="instance-chooser">
    <img class="light-logo" src="../assets/logo/logo-full-500.png">
    <img class="dark-logo" src="../assets/logo/logo-full-500-white.png">

    <div class="card">
      <h3 class="header">
        {{ t('views.ChooseInstance.header.chooseInstance') }}
      </h3>

      <div class="scrolling content">
        <div v-if="isError" role="alert" class="ui negative message">
          <h4 class="header">
            {{ t('views.ChooseInstance.header.failure') }}
          </h4>
          <ul class="list">
            <li>
              {{ t('views.ChooseInstance.help.serverDown') }}
            </li>
            <li>
              {{ t('views.ChooseInstance.help.notFunkwhaleServer') }}
            </li>
          </ul>
        </div>

        <form class="ui form" @submit.prevent="checkAndSwitch(instanceUrl)">
          <p v-if="store.state.instance.instanceUrl && !isTauriInstance" class="description">
            <i18n-t keypath="views.ChooseInstance.message.currentConnection">
              <a :href="store.state.instance.instanceUrl" target="_blank">
                {{ store.getters['instance/domain'] }}
                <i class="external icon" />
              </a>
            </i18n-t>
            {{ t('', { url: store.state.instance.instanceUrl, hostname: store.getters['instance/domain'] }) }}
          </p>
          <p v-else class="description">
            {{ t('views.ChooseInstance.help.selectPod') }}
          </p>

          <div class="field">
            <label for="instance-picker">{{ t('views.ChooseInstance.label.url') }}</label>
            <div class="ui action input">
              <input id="instance-picker" v-model="instanceUrl" type="text" placeholder="https://funkwhale.server">
              <button type="submit" :class="['ui', 'icon', { loading: isLoading }, 'button']">
                {{ t('views.ChooseInstance.button.submit') }}
              </button>
            </div>
          </div>
        </form>

        <div class="ui hidden divider" />

        <form v-if="suggestedInstances.length > 0" class="ui form" @submit.prevent="">
          <div class="field">
            <h4>
              {{ t('views.ChooseInstance.header.suggestions') }}
            </h4>
            <div class="h-scroll">
              <button v-for="(url, key) in suggestedInstances" :key="key" class="ui basic button"
                @click="checkAndSwitch(url)">
                {{ url }}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.instance-chooser {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 99000;

  background: var(--main-background);

  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;

  >.card {
    margin-top: 2rem;
    max-width: 30rem;
    width: 100%;
    background: #fff;
    padding: 1rem;
    border-radius: 0.5rem;
    box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.2);

    .h-scroll {
      max-width: 100%;
      overflow-x: auto;
      display: flex;
      padding: 0 6px 6px;
    }
  }
}

.theme-dark .instance-chooser>.card {
  background: var(--sidebar-background);
}

.theme-dark .instance-chooser>.light-logo {
  display: none;
}

.theme-light .instance-chooser>.dark-logo {
  display: none;
}
</style>

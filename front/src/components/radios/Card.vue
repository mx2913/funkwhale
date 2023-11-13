<script setup lang="ts">
import type { Radio } from '~/types'

import { ref, computed } from 'vue'
import { useStore } from '~/store'

import RadioButton from './Button.vue'
import { FwButton } from '@funkwhale/ui'

interface Props {
  type: string
  customRadio?: Radio | null
  objectId?: string | null
}

const props = withDefaults(defineProps<Props>(), {
  customRadio: null,
  objectId: null
})

const store = useStore()

const isDescriptionExpanded = ref(false)

const radio = computed(() => props.customRadio
  ? props.customRadio
  : store.getters['radios/types'][props.type]
)

const customRadioId = computed(() => props.customRadio?.id ?? null)
</script>

<template>
  <div class="ui card">
    <div class="content">
      <h4 class="header">
        <router-link
          v-if="radio.id"
          class="discrete link"
          :to="{name: 'library.radios.detail', params: {id: radio.id}}"
        >
          {{ radio.name }}
        </router-link>
        <template v-else>
          {{ radio.name }}
        </template>
      </h4>
      <div
        class="description"
        :class="{expanded: isDescriptionExpanded}"
        @click="isDescriptionExpanded = !isDescriptionExpanded"
      >
        {{ radio.description }}
      </div>
    </div>
    <div class="extra content">
      <user-link
        v-if="radio.user"
        :user="radio.user"
        class="left floated"
      />
      <div class="ui hidden divider" />
      <radio-button
        :type="type"
        class="right floated"
        :custom-radio-id="customRadioId"
        :object-id="objectId"
      />
      <fw-button
        v-if="$store.state.auth.authenticated && type === 'custom' && radio.user.id === $store.state.auth.profile?.id"
        color="secondary"
        class="right floated"
        icon="bi-pencil"
        :title="$t('components.radios.Card.button.edit')"
        @click="$router.push({name: 'library.radios.edit', params: {id: customRadioId }})"
      />
    </div>
  </div>
</template>

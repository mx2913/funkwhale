<script setup lang="ts">

import { FwButton } from '@funkwhale/ui'

interface Events {
  (e: 'refresh'): void
}

interface Props {
  refresh?: boolean
}

const emit = defineEmits<Events>()
withDefaults(defineProps<Props>(), {
  refresh: false
})
</script>

<template>
  <div class="ui small placeholder segment component-placeholder component-empty-state">
    <h4 class="ui header">
      <div class="content">
        <slot name="title">
          <i class="search icon" />
          {{ $t('components.common.EmptyState.header.noResults') }}
        </slot>
      </div>
    </h4>
    <div class="inline center aligned text">
      <slot />
      <fw-button
        v-if="refresh"
        color="secondary"
        @click="emit('refresh')"
      >
        {{ $t('components.common.EmptyState.button.refresh') }}
      </fw-button>
    </div>
  </div>
</template>

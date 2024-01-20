<script setup lang="ts">
import { computed } from 'vue'
import { Icon } from '@iconify/vue'

const props = defineProps<{
  src?: string | { coverUrl?: string }
}>()

const coverUrl = computed(() => {
  if (typeof props.src === 'string') return props.src
  return props.src?.coverUrl
})
</script>

<template>
  <div class="cover-art">
    <Transition mode="out-in">
      <img v-if="coverUrl" :src="coverUrl" />
      <Icon v-else icon="bi:disc" />
    </Transition>
  </div>
</template>

<style scoped lang="scss">
.cover-art {
  height: 3rem;
  width: 3rem;
  border-radius: 0.5rem;
  margin-right: 1rem;
  background: var(--fw-gray-200);
  color: var(--fw-gray-500);
  font-size: 1.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  position: relative;
  overflow: hidden;

  > img {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;

    &.v-enter-active,
    &.v-leave-active {
      transition: transform 0.2s ease, opacity 0.2s ease;
    }

    &.v-enter-from,
    &.v-leave-to {
      transform: translateY(1rem);
      opacity: 0;
    }

  }
}
</style>

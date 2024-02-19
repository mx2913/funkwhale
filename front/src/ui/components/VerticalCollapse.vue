<script setup lang="ts">
defineProps<{ open: boolean }>()
</script>

<template>
  <div
    class="v-collapse"
    :class="{ open }"
  >
    <div class="v-collapse-body">
      <slot />
    </div>
  </div>
</template>

<style scoped lang="scss">
.v-collapse {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 0.2s ease;

  &.open {
    grid-template-rows: 1fr;
  }

  .v-collapse-body {
    height: auto;
    overflow: hidden;
  }
}
</style>

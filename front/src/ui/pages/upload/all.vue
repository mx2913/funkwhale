<script setup lang="ts">
import { Icon } from '@iconify/vue'
import type { UploadGroupEntry } from '~/ui/stores/upload';

const allTracks: UploadGroupEntry[] = [
  
]

const columns = [
  { key: '', label: '' }
]
</script>

<template>
  <div v-if="allTracks.length === 0" class="flex flex-col items-center py-32">
    <Icon icon="bi:file-earmark-music" class="h-16 w-16" />

    <h3>There is no file in your library</h3>
    <p>Try uploading some before coming back here!</p>
  </div>
  <FwTable :rows="allTracks">

  </FwTable>
</template>

<style scoped>
h3 {
  font-size: 1.25rem;
  font-weight: 700;
  line-height: 1.2;
  color: var(--fw-gray-700);
}

p {
  font-size: 1rem;
  line-height: 1.5;
  color: var(--fw-gray-960);
}

svg {
  color: var(--fw-gray-600);
}
</style>

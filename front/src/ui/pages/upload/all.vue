<script setup lang="ts">
import { Icon } from '@iconify/vue'
import { computed } from 'vue'
import { bytesToHumanSize } from '~/ui/composables/bytes'
import { useUploadsStore, type UploadGroupEntry } from '~/ui/stores/upload'
import CoverArt from '~/ui/components/CoverArt.vue'

interface Recording {
  guid: string
  title: string
  artist: string
  album: string
  uploadDate: Date
  format: string
  size: string
  metadata: UploadGroupEntry['metadata']
}

const intl = new Intl.DateTimeFormat('en', {
  year: 'numeric',
  month: 'short',
  day: 'numeric'
})

// TODO: Fetch tracks from server
const uploads = useUploadsStore()
const allTracks = computed<Recording[]>(() => {
  return uploads.uploadGroups.flatMap(group => group.queue.map<Recording>((entry) => ({
    guid: entry.id,
    title: entry.metadata?.tags.title || 'Unknown title',
    artist: entry.metadata?.tags.artist || 'Unknown artist',
    album: entry.metadata?.tags.album || 'Unknown album',
    uploadDate: group.createdAt,
    format: 'flac',
    size: bytesToHumanSize(entry.file.size),
    metadata: entry.metadata
  })))
})

const columns = [
  { key: '>index', label: '#' },
  { key: 'title', label: 'Title' },
  { key: 'artist', label: 'Artist' },
  { key: 'album', label: 'Album' },
  { key: 'uploadDate', label: 'Upload date' },
  { key: 'format', label: 'Format' },
  { key: 'size', label: 'Size' }
]
</script>

<template>
  <div
    v-if="allTracks.length === 0"
    class="flex flex-col items-center py-32"
  >
    <Icon
      icon="bi:file-earmark-music"
      class="h-16 w-16"
    />

    <h3>There is no file in your library</h3>
    <p>Try uploading some before coming back here!</p>
  </div>
  <FwTable
    v-else
    id-key="guid"
    :columns="columns"
    :rows="allTracks"
  >
    <template #col-title="{ row, value }">
      <div class="flex items-center">
        <CoverArt
          :src="row.metadata"
          class="mr-2"
        />
        {{ value }}
      </div>
    </template>
    <template #col-upload-date="{ value }">
      {{ intl.format(value) }}
    </template>
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

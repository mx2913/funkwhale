<script setup lang="ts">
import { computed, ref, reactive } from 'vue'
import { useUploadsStore } from '~/ui/stores/upload'
import { bytesToHumanSize } from '~/ui/composables/bytes'
import UploadList from '~/ui/components/UploadList.vue'
import { useRouter } from 'vue-router'

const uploads = useUploadsStore()

const libraryOpen = computed({
  get: () => !!uploads.currentUploadGroup,
  set: (value) => {
    if (!value) {
      uploads.currentUploadGroup = undefined
    }
  }
})

// Server import
const serverPath = ref('/srv/funkwhale/data/music')

// Upload
const queue = computed(() => {
  return uploads.currentUploadGroup?.queue ?? []
})

const combinedFileSize = computed(() => bytesToHumanSize(
  queue.value.reduce((acc, { file }) => acc + file.size, 0)
))

// Actions
const processFiles = (fileList: FileList) => {
  if (!uploads.currentUploadGroup) return

  for (const file of fileList) {
    uploads.currentUploadGroup.queueUpload(file)
  }
}

const router = useRouter()
const cancel = () => {
  libraryOpen.value = false
  uploads.currentUploadGroup?.cancel()
  uploads.currentUploadGroup = undefined

  if (uploads.queue.length > 0) {
    return router.push('/ui/upload/running')
  }
}

const continueInBackground = () => {
  libraryOpen.value = false
  uploads.currentUploadGroup = undefined
  return router.push('/ui/upload/running')
}

// Sorting
const sortItems = reactive([
  { label: 'Upload time', value: 'upload-time' },
  { label: 'Upload time 2', value: 'upload-time-2' },
  { label: 'Upload time 3', value: 'upload-time-3' }
])
const currentSort = ref(sortItems[0])

// Filtering
const filterItems = reactive([
  { label: 'All', value: 'all' }
])
const currentFilter = ref(filterItems[0])

</script>

<template>
  <FwModal
    v-model="libraryOpen"
    title="Upload music to library"
  >
    <template #alert="{ closeAlert }">
      <FwAlert>
        Before uploading, please ensure your files are tagged properly.
        We recommend using Picard for that purpose.

        <template #actions>
          <FwButton @click="closeAlert">
            Got it
          </FwButton>
        </template>
      </FwAlert>
    </template>

    <FwFileInput
      :accept="['.flac', '.ogg', '.opus', '.mp3', '.aac', '.aif', '.aiff', '.m4a']"
      multiple
      auto-reset
      @files="processFiles"
    />

    <!-- Upload path -->
    <div v-if="queue.length > 0">
      <div class="list-header">
        <div class="file-count">
          {{ queue.length }} files, {{ combinedFileSize }}
        </div>

        <FwSelect
          v-model="currentFilter"
          icon="bi:filter"
          :items="filterItems"
        />
        <FwSelect
          v-model="currentSort"
          icon="bi:sort-down"
          :items="sortItems"
        />
      </div>

      <UploadList :uploads="queue" />
    </div>

    <!-- Import path -->
    <template v-else>
      <label>Import from server directory</label>
      <div class="flex items-center">
        <FwInput
          v-model="serverPath"
          class="w-full mr-4"
        />
        <FwButton color="secondary">
          Import
        </FwButton>
      </div>
    </template>

    <template #actions>
      <FwButton
        color="secondary"
        @click="cancel"
      >
        Cancel
      </FwButton>
      <FwButton @click="continueInBackground">
        {{ uploads.queue.length ? 'Continue in background' : 'Save and close' }}
      </FwButton>
    </template>
  </FwModal>
</template>

<style scoped lang="scss">
.list-header {
  display: flex;
  align-items: center;
  margin: 2rem 0 1rem;

  > .file-count {
    margin-right: auto;
    color: var(--fw-gray-600);
    font-weight: 900;
    font-size: 0.875rem;
  }
}

.flex:not(.flex-col) {
  .funkwhale.button {
    &:first-child {
      margin-left: 0;
    }

    &:last-child {
      margin-right: 0;
    }
  }
}
</style>

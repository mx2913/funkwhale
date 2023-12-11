<script setup lang="ts">
import { reactive, ref, computed } from 'vue'
import { UseTimeAgo } from '@vueuse/components'
import { Icon } from '@iconify/vue';
import { useUploadsStore } from '~/ui/stores/upload'

const filesystemStats = reactive({
  total: 10737418240,
  used: 3e9,
})

const filesystemProgress = computed(() => {
  if (filesystemStats.used === 0) return 0
  return filesystemStats.used / filesystemStats.total * 100
})

const bytesToHumanSize = (bytes: number) => {
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  if (bytes === 0) return '0 B'
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  if (i === 0) return `${bytes} ${sizes[i]}`
  return `${(bytes / 1024 ** i).toFixed(1)} ${sizes[i]}`
}

const tabs = [
  {
    label: 'Music library',
    icon: 'headphones',
    description: 'Host music you listen to.',
  },
  {
    label: 'Music channel',
    icon: 'music-note-beamed',
    description: 'Publish music you make.'
  },
  {
    label: 'Podcast channel',
    icon: 'mic',
    description: 'Publish podcast you make.',
  },
]

const currentTab = ref(tabs[0].label)


// Modals
const libraryOpen = ref(false)

// Server import
const serverPath = ref('/srv/funkwhale/data/music')

// Upload
const combinedFileSize = computed(() => bytesToHumanSize(
  uploads.queue.reduce((acc, { file }) => acc + file.size, 0)
))

const uploads = useUploadsStore()
const processFiles = (fileList: FileList) => {
  console.log('processFiles', fileList)
  for (const file of fileList) {
    uploads.queueUpload(file)
  }

}

const cancel = () => {
  libraryOpen.value = false
  uploads.cancelAll()
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
  <div class="flex items-center">
    <h1 class="mr-auto">Upload</h1>

    <div class="filesystem-stats">
      <div class="filesystem-stats--progress" :style="`--progress: ${filesystemProgress}%`" />
      <div class="flex items-center">
        {{ bytesToHumanSize(filesystemStats.total) }} total

        <div class="filesystem-stats--label full" />
        {{ bytesToHumanSize(filesystemStats.used) }} used

        <div class="filesystem-stats--label" />
        {{ bytesToHumanSize(filesystemStats.total - filesystemStats.used) }} available
      </div>
    </div>

  </div>

  <p> Select a destination for your audio files: </p>

  <div class="flex justify-between">
    <FwCard
      v-for="tab in tabs" :key="tab.label"
      :title="tab.label"
      :class="currentTab === tab.label && 'active'"
      @click="currentTab = tab.label"
    >
      <template #image>
        <div class="image-icon">
          <Icon :icon="'bi:' + tab.icon" />
        </div>
      </template>
      {{ tab.description }}
      <div class="radio-button" />
    </FwCard>
  </div>

  <div>
    <FwButton @click="libraryOpen = true">Open library</FwButton>
    <FwModal v-model="libraryOpen" title="Upload music to library">
      <template #alert="{ closeAlert }">
        <FwAlert>
          Before uploading, please ensure your files are tagged properly.
          We recommend using Picard for that purpose.

          <template #actions>
            <FwButton @click="closeAlert">Got it</FwButton>
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
      <div v-if="uploads.queue.length > 0">
        <div class="list-header">
          <div class="file-count">
            {{ uploads.queue.length }} files, {{ combinedFileSize }}
          </div>

          <FwSelect icon="bi:filter" v-model="currentFilter" :items="filterItems" />
          <FwSelect icon="bi:sort-down" v-model="currentSort" :items="sortItems" />
        </div>

        <div class="file-list">
          <div v-for="track in uploads.queue" :key="track.id" class="list-track">
            <div class="track-cover">
              <Transition mode="out-in">
                <img
                  v-if="track.coverUrl"
                  :src="track.coverUrl"
                />
                <Icon v-else icon="bi:disc" />
              </Transition>
            </div>
            <Transition mode="out-in">
              <div v-if="track.tags" class="track-data">
                <div class="track-title">{{ track.tags.title }}</div>
                {{ track.tags.artist }} / {{ track.tags.album }}
              </div>
              <div v-else class="track-title">
                {{ track.file.name }}
              </div>
            </Transition>
            <div class="upload-state">
              <FwPill :color="track.failReason ? 'red' : track.importedAt ? 'blue' : 'secondary'">
                {{
                  track.failReason
                    ? 'failed'
                    : track.importedAt
                      ? 'imported'
                      : track.progress === 100
                        ? 'processing'
                        : 'uploading'
                }}
              </FwPill>
              <div v-if="track.importedAt" class="track-progress">
                <UseTimeAgo :time="track.importedAt" v-slot="{ timeAgo }">{{ timeAgo }}</UseTimeAgo>
              </div>
              <div v-else class="track-progress">
                {{ bytesToHumanSize(track.file.size / 100 * track.progress) }}
                / {{ bytesToHumanSize(track.file.size) }}
                ⋅ {{ track.progress }}%
              </div>
            </div>
            <FwButton
              icon="bi:chevron-right"
              variant="ghost"
              color="secondary"
              :is-loading="!track.importedAt"
              :disabled="!track.importedAt"
            />
          </div>
        </div>

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
        <FwButton @click="cancel" color="secondary">Cancel</FwButton>
        <FwButton @click="libraryOpen = false">
          {{ uploads.queue.length ? 'Continue in background' : 'Save and close' }}
        </FwButton>
      </template>
    </FwModal>
  </div>
</template>

<style scoped lang="scss">
h1 {
  font-size: 36px;
  font-weight: 900;
  font-family: Lato, sans-serif;
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

.filesystem-stats {
  color: var(--fw-gray-700);
  > .flex {
    padding: 1ch;
  }
}

.filesystem-stats--progress {
  height: 20px;
  border: 1px solid var(--fw-gray-600);
  border-radius: 100vw;
  padding: 4px 3px;
}

.filesystem-stats--label.full::after,
.filesystem-stats--progress::after {
  content: '';
  display: block;
  background: var(--fw-gray-600);
  border-radius: 100vw;
  min-width: 4px;
  width: 100%;
  height: 100%;
  max-width: var(--progress, 100);
  transition: max-width 0.2s ease-out;
}

.filesystem-stats--label {
  height: 14px;
  border: 1px solid var(--fw-gray-600);
  border-radius: 100vw;
  padding: 2px 3px;
  width: 2em;
  margin: 0 1ch 0 3ch;
}

.funkwhale.card {
  --fw-card-width: 12.5rem;
  --fw-border-radius: 1rem;
  padding: 1.3rem 2rem;
  box-shadow: 0 2px 4px 2px rgba(#000, 0.1);
  user-select: none;
  margin-bottom: 1rem;

  :deep(.card-content) {
    padding-top: 0;
  }
}

.image-icon {
  background: var(--fw-pastel-blue-1);
  color: var(--fw-pastel-blue-3);
  height: 100%;
  width: 100%;
  font-size: 5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}
.funkwhale.card {
  margin-bottom: 2rem;
  transition: margin-bottom 0.2s ease;

  .radio-button {
    height: 1rem;
    width: 1rem;
    border: 1px solid var(--fw-gray-700);
    border-radius: 1rem;
    position: relative;
    margin: 0.5rem auto 0;
    transition: margin-bottom 0.2s ease;
  }

  &.active {
    margin-bottom: 1rem;

    .radio-button {
      margin-bottom: 1rem;

      &::after {
        content: '';
        background: var(--fw-blue-400);
        border: inherit;
        border-radius: inherit;
        position: absolute;
        inset: 3px;
      }
    }
  }
}

label {
  line-height: 1.2;
  font-weight: 900;
  margin: 2rem 0 0.75rem;
  display: block;
  color: var(--fw-gray-900);
}

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

.list-track {
  display: flex;
  align-items: center;
  padding: .5rem 0;

  &:not(:first-child) {
    border-top: 1px solid var(--fw-gray-200);
  }

  > .track-cover {
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

  .track-data,
  .track-title {
    font-size: 0.875rem;
    color: var(--fw-gray-960);
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;

    &.v-enter-active,
    &.v-leave-active {
      transition: transform 0.2s ease, opacity 0.2s ease;
    }

    &.v-enter-from {
      transform: translateY(1rem);
      opacity: 0;
    }

    &.v-leave-to {
      transform: translateY(-1rem);
      opacity: 0;
    }
  }
  .track-progress {
    font-size: 0.875rem;
    color: var(--fw-gray-600);
  }

  .upload-state {
    margin-left: auto;
    text-align: right;
    flex-shrink: 0;
    padding-left: 1ch;
    margin-right: 0.5rem;

    :deep(.funkwhale.pill) {
      margin-right: -0.5rem !important;
    }
  }

  :deep(.funkwhale.button):not(:hover) {
    background: transparent !important;
    border-color: transparent !important;
  }
}
</style>

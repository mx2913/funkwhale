<script setup lang="ts">
import { ref } from 'vue';
import { UploadGroup } from '~/ui/stores/upload'
import VerticalCollapse from '~/ui/components/VerticalCollapse.vue'
import UploadList from '~/ui/components/UploadList.vue'
import { UseTimeAgo } from '@vueuse/components'
import { Icon } from '@iconify/vue'


defineProps<{ groups: UploadGroup[], isUploading?: boolean }>()

const openUploadGroup = ref<UploadGroup>()
const toggle = (group: UploadGroup) => {
  openUploadGroup.value = openUploadGroup.value === group
    ? undefined
    : group
}

const labels = {
  'music-library': 'Music library',
  'music-channel': 'Music channel',
  'podcast-channel': 'Podcast channel',
}

const getDescription = (group: UploadGroup) => {
  if (group.queue.length === 0) return 'Unknown album'

  return group.queue.reduce((acc, { metadata }) => {
    if (!metadata) return acc

    let element = group.type === 'music-library'
      ? metadata.tags.album
      : metadata.tags.title
    
    element = acc.length < 3 
      ? element 
      : '...'

    if (!acc.includes(element)) {
      acc.push(element)
    }

    return acc
  }, [] as string[]).join(', ')
}
</script>

<template>
  <div>
    <div 
      class="upload-group"
      v-for="group of groups" 
      :key="group.guid"
    >
      <div class="flex items-center">
        <div class="upload-group-header">
          <div class="upload-group-title">{{ labels[group.type] }}</div>
          <div class="upload-group-albums">{{ getDescription(group) }}</div>
        </div>
        
        <div class="timeago">
          <UseTimeAgo :time="group.createdAt" v-slot="{ timeAgo }">{{ timeAgo }}</UseTimeAgo>
        </div>


        <FwPill v-if="group.failedCount > 0" color="red">
          <template #image>
            <div class="flex items-center justify-center">{{ group.failedCount }}</div>
          </template>
          failed
        </FwPill>

        <FwPill v-if="group.importedCount > 0" color="blue">
          <template #image>
            <div class="flex items-center justify-center">{{ group.importedCount }}</div>
          </template>
          imported
        </FwPill>

        <FwPill v-if="group.processingCount > 0" color="secondary">
          <template #image>
            <div class="flex items-center justify-center">{{ group.processingCount }}</div>
          </template>
          processing
        </FwPill>


        <FwButton
          @click="toggle(group)"
          variant="ghost"
          color="secondary"
          class="icon-only"
        >
          <template #icon>
            <Icon icon="bi:chevron-right" :rotate="group === openUploadGroup ? 1 : 0" />
          </template>
        </FwButton>
      </div>

      <div v-if="isUploading" class="flex items-center upload-progress">
        <FwButton v-if="group.processingCount === 0 && group.failedCount > 0" @click="group.retry()" color="secondary">Retry</FwButton>
        <FwButton v-else-if="group.queue.length !== group.importedCount" @click="group.cancel()" color="secondary">Interrupt</FwButton>

        <div class="progress">
          <div class="progress-bar" :style="{ width: `${group.progress}%` }" />
        </div>

        <div class="shrink-0">
          {{ group.importedCount }} / {{ group.queue.length }} files imported
        </div>
      </div>

      <VerticalCollapse @click.stop :open="openUploadGroup === group" class="collapse">
        <UploadList :uploads="group.queue" />
      </VerticalCollapse>
    </div>
  </div>
</template>

<style scoped lang="scss">
.upload-group {
  &:not(:first-child) {
    border-top: 1px solid var(--fw-gray-200);
    padding-top: 1rem;
  }

  .upload-group-header {
    .upload-group-title {
      color: var(--fw-gray-960);
      font-size: 0.9375rem;
    }

    .upload-group-albums {
      color: var(--fw-gray-960);
      font-size: 0.875rem;
    }
  }
}

.timeago {
  margin-left: auto;
  margin-right: 1rem;
  font-size: 0.875rem;
  color: var(--fw-gray-600);
}


.upload-progress {
  font-size: 0.875rem;
  color: var(--fw-gray-600);
  padding-top: 0.5rem;
  padding-bottom: 1rem;

  > :deep(.funkwhale.button) {
    margin: 0rem;
  }

  > :deep(.funkwhale.button) + .progress {
    margin-left: 1rem;
  }

  .progress {
    width: 100%;
    height: 0.5rem;
    background-color: var(--fw-gray-200);
    border-radius: 1rem;
    margin: 0 1rem 0 0;
    position: relative;

    .progress-bar {
      height: 100%;
      background-color: var(--fw-primary);
      border-radius: 1rem;
      width: 0;
      transition: width 0.2s ease;
    }
  }
}

.collapse {
  padding-bottom: 1rem;
}
</style>

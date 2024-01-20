<script setup lang="ts">
import type { UploadGroupEntry } from '~/ui/stores/upload'
import { bytesToHumanSize } from '~/ui/composables/bytes'
import { UseTimeAgo } from '@vueuse/components'
import CoverArt from '~/ui/components/CoverArt.vue'

defineProps<{
  uploads: UploadGroupEntry[]
  wide?: boolean
}>()

</script>

<template>
  <div class="file-list">
    <div v-for="track in uploads" :key="track.id" class="list-track" :class="{ wide }">
      <CoverArt :src="track.metadata" class="track-cover" />
      <Transition mode="out-in">
        <div v-if="track.metadata?.tags" class="track-data">
          <div class="track-title">{{ track.metadata.tags.title }}</div>
          {{ track.metadata.tags.artist }} / {{ track.metadata.tags.album }}
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
        <div v-if="track.importedAt" class="track-timeago">
          <UseTimeAgo :time="track.importedAt" v-slot="{ timeAgo }">{{ timeAgo }}</UseTimeAgo>
        </div>
        <div v-else class="track-progress">
          {{ bytesToHumanSize(track.file.size / 100 * track.progress) }}
          / {{ bytesToHumanSize(track.file.size) }}
          ⋅ {{ track.progress }}%
        </div>
      </div>
      <FwButton
        v-if="track.failReason"
        @click="track.retry()"
        icon="bi:arrow-repeat"
        variant="ghost"
        color="secondary"
      />
      <FwButton
        v-else
        icon="bi:chevron-right"
        variant="ghost"
        color="secondary"
        :is-loading="!track.importedAt"
        :disabled="!track.importedAt"
      />
    </div>
  </div>
</template>

<style scoped lang="scss">
.list-track {
  display: flex;
  align-items: center;
  padding: .5rem 0;

  &:not(:first-child) {
    border-top: 1px solid var(--fw-gray-200);
  }

  > :deep(.track-cover) {
    height: 3rem;
    width: 3rem;
    border-radius: 0.5rem;
    margin-right: 1rem;
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
  .track-timeago,
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

  &.wide {
    .upload-state {
      display: flex;
      align-items: center;
      margin-right: 1rem;

      .track-timeago,
      .track-progress {
        order: -1;
        margin-right: 1rem;
      }
    }
  }
}
</style>

<script setup lang="ts">
import { reactive, computed } from 'vue'
import { useUploadsStore } from '~/ui/stores/upload'
import { bytesToHumanSize } from '~/ui/composables/bytes'
import UploadModal from '~/ui/components/UploadModal.vue'

const filesystemStats = reactive({
  total: 10737418240,
  used: 3e9
})

const filesystemProgress = computed(() => {
  if (filesystemStats.used === 0) return 0
  return filesystemStats.used / filesystemStats.total * 100
})

const uploads = useUploadsStore()
const tabs = computed(() => [
  {
    label: 'Running',
    key: 'running',
    enabled: uploads.uploadGroups.length > 0
  },
  {
    label: 'New',
    key: '',
    enabled: true
  },
  {
    label: 'History',
    key: 'history',
    enabled: true
  },
  {
    label: 'All files',
    key: 'all',
    enabled: true
  }
].filter(tab => tab.enabled))
</script>

<template>
  <div class="flex items-center">
    <h1 class="mr-auto">
      Upload
    </h1>

    <div class="filesystem-stats">
      <div
        class="filesystem-stats--progress"
        :style="`--progress: ${filesystemProgress}%`"
      />
      <div class="flex items-center">
        {{ bytesToHumanSize(filesystemStats.total) }} total

        <div class="filesystem-stats--label full" />
        {{ bytesToHumanSize(filesystemStats.used) }} used

        <div class="filesystem-stats--label" />
        {{ bytesToHumanSize(filesystemStats.total - filesystemStats.used) }} available
      </div>
    </div>
  </div>

  <div class="mb-4 -ml-2">
    <RouterLink
      v-for="tab in tabs"
      :key="tab.key"
      :to="`/upload/${tab.key}`"
      custom
      #="{ navigate, isExactActive }"
    >
      <FwPill
        :color="isExactActive ? 'primary' : 'secondary'"
        @click="navigate"
      >
        {{ tab.label }}
      </FwPill>
    </RouterLink>
  </div>

  <RouterView />

  <UploadModal />
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

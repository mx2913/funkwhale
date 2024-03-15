<script setup lang="ts">
import { Icon } from '@iconify/vue'
import { useUploadsStore, type UploadGroupType } from '~/ui/stores/upload'
import { ref } from 'vue'
import axios from 'axios'
import { useAsyncState } from '@vueuse/core'

interface Tab {
  label: string
  icon: string
  description: string
  key: UploadGroupType
}

const tabs: Tab[] = [
  {
    label: 'Music library',
    icon: 'headphones',
    description: 'Host music you listen to.',
    key: 'music-library'
  },
  {
    label: 'Music channel',
    icon: 'music-note-beamed',
    description: 'Publish music you make.',
    key: 'music-channel'
  },
  {
    label: 'Podcast channel',
    icon: 'mic',
    description: 'Publish podcast you make.',
    key: 'podcast-channel'
  }
]

const currentTab = ref(tabs[0])

const uploads = useUploadsStore()
const openLibrary = () => {
  uploads.createUploadGroup(currentTab.value.key, target.value?.uuid)
}

const target = ref()
const { state: items } = useAsyncState(
  axios.get('/libraries/?scope=me')
    .then(t => t.data.results),
  []
)
</script>

<template>
  <div class="upload">
    <p> Select a destination for your audio files: </p>

    <div class="flex gap-8">
      <FwCard
        v-for="tab in tabs"
        :key="tab.key"
        :title="tab.label"
        :class="currentTab.key === tab.key && 'active'"
        @click="currentTab = tab"
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

    <FwSelect :items="items" v-model="target" id-key="uuid">
      <template #item="{ item }">
        <div class="library-item">
          <div class="box" />
          <div>
            <div>{{ item.name }}</div>
            <div>
              Shared with <fw-pill color="blue">{{ item.privacy_level }}</fw-pill>
              <div>{{ item.uploads_count }} uploads</div>
            </div>
          </div>
        </div>
      </template>
    </FwSelect>



    <FwButton :disabled="!target" @click="openLibrary">
      Open library
    </FwButton>
  </div>
</template>

<style scoped lang="scss">
:deep(.funkwhale.select) {
  margin-bottom: 1rem;
}

.funkwhale.card {
  --fw-card-width: 12.5rem;
  --fw-border-radius: 1rem;
  padding: 1.3rem 2rem;
  box-shadow: 0 2px 4px 2px rgba(#000, 0.1);
  user-select: none;
  margin-bottom: 1rem;
  margin-bottom: 2rem;
  transition: margin-bottom 0.2s ease;

  :deep(.card-content) {
    padding-top: 0;
  }

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

.upload > .funkwhale.button {
  margin-left: 0;
}

.library-item {
  width: 100%;
  display: flex;
  align-items: center;

  > .box {
    width: 2.75rem;
    height: 2.75rem;
    flex-shrink: 0;
    background: var(--fw-pastel-blue-1);
    border-radius: 8px;
    margin-right:8px;

    + div {
      width: 100%;

      > :last-child {
        display: flex;
        width: 100%;

        > div {
          margin-left: auto;
        }
      }
    }
  }

  .selected {
    font-size: 1rem;
  }
}

</style>

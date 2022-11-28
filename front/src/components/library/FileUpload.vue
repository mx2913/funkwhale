<script setup lang="ts">
import type { Library } from '~/types'

import { computed, ref } from 'vue'
import { humanSize, truncate } from '~/utils/filters'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'

import LibraryFilesTable from '~/views/content/libraries/FilesTable.vue'
import FsBrowser from './FsBrowser.vue'
import FsLogs from './FsLogs.vue'
import { useTrackUpload } from '~/composables/files/upload'
import { useImportStatus } from '~/composables/files/imports'

interface Props {
  library: Library
}

const props = defineProps<Props>()

const { t } = useI18n()
const store = useStore()

const currentTab = ref('uploads')
const supportedExtensions = computed(() => store.state.ui.supportedExtensions)

const labels = computed(() => ({
  tooltips: {
    denied: t('components.library.FileUpload.tooltip.denied'),
    server: t('components.library.FileUpload.tooltip.size'),
    network: t('components.library.FileUpload.tooltip.network'),
    timeout: t('components.library.FileUpload.tooltip.timeout'),
    retry: t('components.library.FileUpload.tooltip.retry'),
    extension: t(
      'components.library.FileUpload.tooltip.extension',
      { extensions: supportedExtensions.value.join(', ') }
    )
  } as Record<string, string>
}))

const { importReference, uploadFiles, files } = useTrackUpload(() => props.library.uuid)
const importStatus = useImportStatus(importReference.value)

// NOTE: TEMPORARY STUFF
interface TEMPFILE {
  id: any
  name: string
  size: number
  error: string
  success: boolean
  active: boolean
  progress: number
}
const retryableFiles = [] as TEMPFILE[]
const fsErrors = [] as string[]
const isLoadingQuota = false
const remainingSpace = 0
const retry = (files: TEMPFILE[]) => undefined
const fsPath = ['']
const isLoadingFs = false
const needsRefresh = false
const fsStatus = {} as any
const importFs = () => undefined
const cancelFsScan = () => undefined
</script>

<template>
  <div class="component-file-upload">
    <div class="ui top attached tabular menu">
      <a
        href=""
        :class="['item', {active: currentTab === 'uploads'}]"
        @click.prevent="currentTab = 'uploads'"
      >
        {{ $t('components.library.FileUpload.link.uploading') }}
        <div
          v-if="files.length === 0"
          class="ui label"
        >
          {{ $t('components.library.FileUpload.empty.noFiles') }}
        </div>
        <div
          v-else
          class="ui label"
        >
          {{ files.filter(file => file.status !== 'queued' && file.status !== 'uploading' ).length }}
          <span class="slash symbol" />
          {{ files.length }}
        </div>
      </a>
      <a
        href=""
        :class="['item', {active: currentTab === 'processing'}]"
        @click.prevent="currentTab = 'processing'"
      >
        {{ $t('components.library.FileUpload.link.processing') }}
        <div class="ui label">
          {{ importStatus.pending }}
        </div>
      </a>
    </div>
    <div :class="['ui', 'bottom', 'attached', 'segment', {hidden: currentTab != 'uploads'}]">
      <div :class="['ui', {loading: isLoadingQuota}, 'container']">
        <div :class="['ui', {red: remainingSpace === 0}, {warning: remainingSpace > 0 && remainingSpace <= 50}, 'small', 'statistic']">
          <div class="label">
            {{ $t('components.library.FileUpload.label.remainingSpace') }}
          </div>
          <div class="value">
            {{ humanSize(remainingSpace * 1000 * 1000) }}
          </div>
        </div>
        <div class="ui divider" />
        <h2 class="ui header">
          {{ $t('components.library.FileUpload.header.local') }}
        </h2>
        <div class="ui message">
          <p>
            {{ $t('components.library.FileUpload.message.local.message') }}
          </p>
          <ul>
            <li v-if="library.privacy_level != 'me'">
              {{ $t('components.library.FileUpload.message.local.copyright') }}
            </li>
            <li>
              {{ $t('components.library.FileUpload.message.local.tag') }}&nbsp;
              <a
                href="http://picard.musicbrainz.org/"
                target="_blank"
              >{{ $t('components.library.FileUpload.link.picard') }}</a>
            </li>
            <li>
              {{ $t('components.library.FileUpload.message.local.format') }}
            </li>
          </ul>
        </div>
        <div
          :class="['ui', 'icon', 'basic', 'button']"
          @click="uploadFiles"
        >
          <i class="upload icon" />&nbsp;
          {{ $t('components.library.FileUpload.label.uploadWidget') }}
          <br>
          <br>
          <i>
            {{ $t('components.library.FileUpload.label.extensions', {extensions: supportedExtensions.join(', ')}) }}
          </i>
        </div>
      </div>
      <div
        v-if="files.length > 0"
        class="table-wrapper"
      >
        <div class="ui hidden divider" />
        <table class="ui unstackable table">
          <thead>
            <tr>
              <th class="ten wide">
                {{ $t('components.library.FileUpload.table.upload.header.filename') }}
              </th>
              <th>
                {{ $t('components.library.FileUpload.table.upload.header.size') }}
              </th>
              <th>
                {{ $t('components.library.FileUpload.table.upload.header.status') }}
              </th>
              <th>
                {{ $t('components.library.FileUpload.table.upload.header.actions') }}
              </th>
            </tr>
            <tr v-if="retryableFiles.length > 1">
              <th class="ten wide" />
              <th />
              <th />
              <th>
                <button
                  class="ui right floated small basic button"
                  @click.prevent="retry(retryableFiles)"
                >
                  {{ $t('components.library.FileUpload.button.retry') }}
                </button>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="upload in files"
              :key="upload.id"
            >
              <td :title="upload.file.name">
                {{ truncate(upload.file.name, 60) }}
              </td>
              <td>{{ humanSize(upload.file.size) }}</td>
              <td>
                <span
                  v-if="upload.error"
                  class="ui tooltip"
                >
                  <span class="ui danger icon label">
                    <i class="question circle outline icon" /> {{ upload.error }}
                  </span>
                </span>
                <span
                  v-else-if="upload.status === 'uploaded' || upload.status === 'imported'"
                  class="ui success label"
                >
                  <span v-if="upload.status === 'uploaded'">
                    {{ $t('components.library.FileUpload.table.upload.status.uploaded') }}
                  </span>
                  <span v-if="upload.status === 'imported'">
                    {{ $t('components.library.FileUpload.table.upload.status.imported') }}
                  </span>
                </span>
                <span
                  v-else-if="upload.status === 'uploading'"
                  class="ui warning label"
                >
                  <span key="2">
                    {{ $t('components.library.FileUpload.table.upload.status.uploading') }}
                  </span>

                  {{ $t('components.library.FileUpload.table.upload.progress', { percent: upload.progress?.toFixed(2) }) }}
                </span>
                <span
                  v-else
                  class="ui label"
                >
                  <span key="3">
                    {{ $t('components.library.FileUpload.table.upload.status.pending') }}
                  </span>
                </span>
              </td>
              <td>
                <!-- <template v-if="upload.error">
                  <button
                    v-if="retryableFiles.includes(upload)"
                    class="ui tiny basic icon right floated button"
                    :title="labels.tooltips.retry"
                    @click.prevent="retry([upload])"
                  >
                    <i class="redo icon" />
                  </button>
                </template>
                <template v-else-if="!upload.success">
                  <button
                    class="ui tiny basic danger icon right floated button"
                    @click.prevent="upload.remove(upload)"
                  >
                    <i class="delete icon" />
                  </button>
                </template> -->
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="ui divider" />
      <h2 class="ui header">
        {{ $t('components.library.FileUpload.header.server') }}
      </h2>
      <div
        v-if="fsErrors.length > 0"
        role="alert"
        class="ui negative message"
      >
        <h3 class="header">
          {{ $t('components.library.FileUpload.header.failure') }}
        </h3>
        <ul class="list">
          <li
            v-for="(error, key) in fsErrors"
            :key="key"
          >
            {{ error }}
          </li>
        </ul>
      </div>
      <fs-browser
        v-model="fsPath"
        :loading="isLoadingFs"
        :data="fsStatus"
        @import="importFs"
      />
      <template v-if="fsStatus && fsStatus.import">
        <h3 class="ui header">
          {{ $t('components.library.FileUpload.header.status') }}
        </h3>
        <p v-if="fsStatus.import.reference !== importReference">
          {{ $t('components.library.FileUpload.description.previousImport') }}
        </p>
        <p v-else>
          {{ $t('components.library.FileUpload.description.import') }}
        </p>

        <button
          v-if="fsStatus.import.status === 'started' || fsStatus.import.status === 'pending'"
          class="ui button"
          @click="cancelFsScan"
        >
          {{ $t('components.library.FileUpload.button.cancel') }}
        </button>
        <fs-logs :data="fsStatus.import" />
      </template>
    </div>
    <div :class="['ui', 'bottom', 'attached', 'segment', {hidden: currentTab != 'processing'}]">
      <library-files-table
        :needs-refresh="needsRefresh"
        ordering-config-name="library.detail.upload"
        :filters="{import_reference: importReference}"
        :custom-objects="Object.values({})"
        @fetch-start="needsRefresh = false"
      />
    </div>
  </div>
</template>

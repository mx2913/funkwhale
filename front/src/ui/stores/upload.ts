
import { defineStore, acceptHMRUpdate } from 'pinia'
import { computed, reactive, readonly, ref, markRaw, toRaw, unref, watch } from 'vue'
import { whenever, useWebWorker } from '@vueuse/core'
import { nanoid } from 'nanoid'
import axios from 'axios'

import FileMetadataParserWorker from '~/ui/workers/file-metadata-parser.ts?worker'
import type { MetadataParsingResult } from '~/ui/workers/file-metadata-parser'

import type { Tags } from '~/ui/composables/metadata'

export type UploadGroupType = 'music-library' | 'music-channel' | 'podcast-channel'
export type FailReason = 'missing-tags' | 'upload-failed' | 'upload-cancelled'

export class UploadGroupEntry {
  id = nanoid()
  abortController = new AbortController()
  progress = 0

  error?: Error
  failReason?: FailReason
  importedAt?: Date

  metadata?: {
    tags: Tags,
    coverUrl?: string
  }

  constructor (public file: File, public uploadGroup: UploadGroup) {
    UploadGroup.entries[this.id] = this
  }

  async upload () {
    const body = new FormData()
    body.append('file', this.file)

    await axios.post(this.uploadGroup.uploadUrl, body, {
      headers: { 'Content-Type': 'multipart/form-data' },
      signal: this.abortController.signal,
      onUploadProgress: (e) => {
        // NOTE: If e.total is absent, we use the file size instead. This is only an approximation, as e.total is the total size of the request, not just the file.
        // see: https://developer.mozilla.org/en-US/docs/Web/API/ProgressEvent/total
        this.progress = Math.floor(e.loaded / (e.total ?? this.file.size) * 100)

        if (this.progress === 100) {
          console.log(`[${this.id}] upload complete!`)
        }
      }
    })

    console.log(`[${this.id}] import complete!`)
    this.importedAt = new Date()
  }

  fail (reason: FailReason, error: Error) {
    this.error = error
    this.failReason = reason
    this.importedAt = new Date()
  }

  cancel (reason: FailReason = 'upload-cancelled', error: Error = new Error('Upload cancelled')) {
    this.fail(reason, error)
    this.abortController.abort()
  }

  retry () {
    this.error = undefined
    this.failReason = undefined
    this.importedAt = undefined
    this.progress = 0
    this.abortController = new AbortController()

    if (!this.metadata) {
      this.fail('missing-tags', new Error('Missing metadata'))
      return
    }

    uploadQueue.push(this)
  }
}

export class UploadGroup {
  static entries = Object.create(null)

  queue: UploadGroupEntry[] = []
  createdAt = new Date()

  constructor (
    public guid: string,
    public type: UploadGroupType,
    public uploadUrl: string
  ) {}

  get progress () {
    return this.queue.reduce((total, entry) => total + entry.progress, 0) / this.queue.length
  }

  get failedCount () {
    return this.queue.filter((entry) => entry.failReason).length
  }

  get importedCount () {
    return this.queue.filter((entry) => entry.importedAt && !entry.failReason).length
  }

  get processingCount () {
    return this.queue.filter((entry) => !entry.importedAt && !entry.failReason).length
  }

  queueUpload(file: File) {
    const entry = new UploadGroupEntry(file, this)
    this.queue.push(entry)

    const { id, metadata } = entry
    if (!metadata) {
      console.log('sending message to worker', id)
      retrieveMetadata({ id, file })
    }

    uploadQueue.push(entry)
  }

  cancel () {
    for (const entry of this.queue) {
      if (entry.importedAt) continue
      entry.cancel()
    }
  }

  retry () {
    for (const entry of this.queue) {
      if (!entry.failReason) continue
      entry.retry()
    }
  }
}

const uploadQueue: UploadGroupEntry[] = reactive([])
const uploadGroups: UploadGroup[] = reactive([])
const currentUploadGroup = ref<UploadGroup>()
const currentIndex = ref(0)

// Remove the upload group from the list if there are no uploads
watch(currentUploadGroup, (_, from) => {
  if (from && from.queue.length === 0) {
    const index = uploadGroups.indexOf(from)
    if (index === -1) return
    uploadGroups.splice(index, 1)
  }
})

// Tag extraction with a Web Worker
const { post: retrieveMetadata, data: workerMetadata} = useWebWorker<MetadataParsingResult>(() => new FileMetadataParserWorker())
whenever(workerMetadata, (reactiveData) => {
  const data = toRaw(unref(reactiveData))
  const entry = UploadGroup.entries[data.id]
  console.log(data, entry)
  if (!entry) return

  if (data.status === 'success') {
    entry.metadata = {
      tags: markRaw(data.tags),
      coverUrl: data.coverUrl
    }
  } else {
    entry.cancel('missing-tags', data.error)
    console.warn(`Failed to parse metadata for file ${entry.file.name}:`, data.error)
  }
})

export const useUploadsStore = defineStore('uploads', () => {
  const createUploadGroup = async (type: UploadGroupType) => {
    // TODO: API call
    const uploadGroup = new UploadGroup('guid:' + nanoid(), type, 'https://httpbin.org/post')
    uploadGroups.push(uploadGroup)
    currentUploadGroup.value = uploadGroup
  }

  const currentUpload = computed(() => uploadQueue[currentIndex.value])
  const isUploading = computed(() => !!currentUpload.value)

  // Upload the file whenever it is available
  whenever(currentUpload, (entry) => entry.upload().catch((error) => {
    // The tags were missing, so we have cancelled the upload
    if (error.code === 'ERR_CANCELED') {
      return
    }

    entry.fail('upload-failed', error)
    console.error(error)
  }).finally(() => {
    // Move to the next upload despite failing
    currentIndex.value += 1
  }))

  // Prevent the user from leaving the page while uploading
  window.addEventListener('beforeunload', (event) => {
    if (isUploading.value) {
      event.preventDefault()
      return event.returnValue = 'The upload is still in progress. Are you sure you want to leave?'
    }
  })

  const progress = computed(() => {
    return uploadGroups.reduce((acc, group) => acc + group.progress, 0) / uploadGroups.length
  })

  // Return public API
  return {
    isUploading,
    currentIndex: readonly(currentIndex),
    currentUpload,
    queue: readonly(uploadQueue),
    uploadGroups: uploadGroups,
    createUploadGroup,
    currentUploadGroup,
    progress
  }
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useUploadsStore, import.meta.hot))
}

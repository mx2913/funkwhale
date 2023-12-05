
import { defineStore, acceptHMRUpdate } from 'pinia'
import { computed, reactive, readonly, ref, watchEffect, markRaw, toRaw, type Ref } from 'vue'
import { whenever, useWebWorker, type UseWebWorkerReturn } from '@vueuse/core'
import { not } from '@vueuse/math'
import axios from 'axios'

import FileMetadataParserWorker, { type MetadataParsingResult } from '~/ui/workers/file-metadata-parser.ts?worker'

import { getCoverUrl, getTags, type Tags } from '~/ui/composables/metadata'

interface UploadQueueEntry {
  id: string
  file: File

  // Upload info
  abortController: AbortController
  progress: number

  // Import info
  importedAt?: Date

  // Failure info
  failReason?: 'missing-tags' | 'upload-failed'
  error?: Error

  // Metadata
  tags?: Tags
  coverUrl?: string
}

export const useUploadsStore = defineStore('uploads', () => {
  const uploadQueue: UploadQueueEntry[] = reactive([])
  const currentIndex = ref(0)
  const currentUpload = computed(() => uploadQueue[currentIndex.value])
  const isUploading = computed(() => !!currentUpload.value)

  // Tag extraction with a Web Worker
  const worker = ref<UseWebWorkerReturn<MetadataParsingResult>>()
  const retrieveMetadata = (entry: Pick<UploadQueueEntry, 'id' | 'file'>) => {
    if (!worker.value) worker.value = useWebWorker<MetadataParsingResult>(FileMetadataParserWorker)
    worker.value.post(entry)
  }

  whenever(not(isUploading), () => {
    worker.value?.terminate()
    worker.value = undefined
  })


  whenever(() => worker.value?.data, (reactiveData) => {
    const data = toRaw(reactiveData)
    if (data.status === 'success') {
      const id = data.id as number
      const tags  = data.tags as Tags
      const coverUrl = data.coverUrl as string

      uploadQueue[id].tags = markRaw(tags)
      uploadQueue[id].coverUrl = coverUrl
    } else {
      const id = data.id as number
      const entry = uploadQueue[id]

      entry.error = data.error
      entry.failReason = 'missing-tags'
      entry.importedAt = new Date()
      entry.abortController.abort()

      console.warn(`Failed to parse metadata for file ${entry.file.name}:`, data.error)
    }
  })

  const upload = async (entry: UploadQueueEntry) => {
    const body = new FormData()
    body.append('file', entry.file)

    const uploadProgress = ref(0)

    await axios.post('https://httpbin.org/post', body, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      signal: entry.abortController.signal,
      onUploadProgress: (e) => {
        entry.progress = Math.floor(e.loaded / e.total * 100)

        if (entry.progress === 100) {
          console.log(`[${entry.id}] upload complete!`)
        }
      }
    })

    console.log(`[${entry.id}] import complete!`)
    entry.importedAt = new Date()
  }

  const queueUpload = async (file: File) => {
    let id = uploadQueue.length
    uploadQueue.push({
      id,
      file,
      progress: 0,
      abortController: new AbortController()
    })

    console.log('sending message to worker', id)
    retrieveMetadata({ id, file })
  }

  // Upload the file whenever it is available
  whenever(currentUpload, (entry) => upload(entry).catch((error) => {
    // The tags were missing, so we have cancelled the upload
    if (error.code === 'ERR_CANCELED') {
      return
    }

    entry.error = error
    entry.failReason = 'upload-failed'
    entry.importedAt = new Date()
    console.error(error)
  }).finally(() => {
    // Move to the next upload despite failing
    currentIndex.value += 1
  }))

  // Prevent the user from leaving the page while uploading
  window.addEventListener('beforeunload', (event) => {
    if (isUploading.value) {
      event.preventDefault()
      event.returnValue = 'The upload is still in progress. Are you sure you want to leave?'
    }
  })

  const cancelAll = () => {
    for (const upload of uploadQueue) {
      upload.abortController.abort()
    }

    uploadQueue.length = 0
    currentIndex.value = 0
  }

  // Return public API
  return {
    isUploading,
    queueUpload,
    currentUpload,
    cancelAll,
    queue: readonly(uploadQueue)
  }
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useUploadsStore, import.meta.hot))
}

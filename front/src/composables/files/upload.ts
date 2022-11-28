import { resolveUnref, useFileDialog, useSessionStorage, whenever, type MaybeComputedRef } from '@vueuse/core'
import { markRaw, reactive, readonly, ref, watchEffect } from 'vue'

import axios from 'axios'
import type { BackendError } from '~/types'

export const importReference = useSessionStorage('uploads:import-reference', new Date().toISOString())

export const useTrackUpload = (libraryUUID: MaybeComputedRef<string>) => {
  const { open, files } = useFileDialog({
    multiple: true,
    accept: 'audio/*'
  })

  interface FileUpload {
    id: string
    file: File
    progress: number
    status: 'queued' | 'uploading' | 'uploaded' | 'imported'
    error?: 'denied' | 'error'
  }

  const filesToUpload: FileUpload[] = reactive([])
  whenever(files, (files) => {
    for (const file of files) {
      filesToUpload.push({
        id: Math.random().toString().slice(2),
        file: markRaw(file),
        status: 'queued',
        progress: 0
      })
    }
  })

  const uploadingIndex = ref(0)
  watchEffect(async () => {
    if (uploadingIndex.value >= filesToUpload.length) {
      return
    }

    const upload = filesToUpload[uploadingIndex.value]
    switch (upload.status) {
      case 'uploading':
        return

      case 'uploaded':
      case 'imported':
        uploadingIndex.value += 1
        return
    }

    const formData = new FormData()

    const { file } = upload
    const name = file.webkitRelativePath || file.name || 'unknown'
    formData.append('audio_file', file, name)
    formData.append('source', `upload://${name}`)
    formData.append('library', resolveUnref(libraryUUID))
    formData.append('import_reference', importReference.value)
    // formData.append('import_metadata', JSON.stringify({
    //   title: name.replace(/\.[^/.]+$/, '')
    // }))

    try {
      upload.status = 'uploading'

      const { data } = await axios.post('/uploads', formData, {
        onUploadProgress: (progressEvent) => {
          upload.progress = progressEvent.loaded / progressEvent.total * 100
        }
      })

      upload.id = data.uuid
      upload.status = 'uploaded'
    } catch (error) {
      upload.error = (error as BackendError).backendErrors[0] === 'Entity Too Large'
        ? 'denied'
        : 'error'
    }

    uploadingIndex.value += 1
  })

  const uploadFiles = () => {
    open()
  }

  return {
    importReference,
    uploadFiles,
    files: readonly(filesToUpload)
  }
}

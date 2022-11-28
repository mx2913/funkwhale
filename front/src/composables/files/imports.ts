import { reactive } from 'vue'
import axios from 'axios'
import useErrorHandler from '../useErrorHandler'
import useWebSocketHandler from '../useWebSocketHandler'

type ImportStatus = Record<'pending' | 'finished' | 'skipped' | 'errored', number>

const fetchImportStatus = async (importReference: string) => {
  const importStatus: ImportStatus = {
    pending: 0,
    finished: 0,
    skipped: 0,
    errored: 0
  }

  for (const status of Object.keys(importStatus)) {
    try {
      const response = await axios.get('uploads/', {
        params: {
          import_reference: importReference,
          import_status: status,
          page_size: 1
        }
      })

      importStatus[status as keyof typeof importStatus] = response.data.count
    } catch (error) {
      useErrorHandler(error as Error)
    }
  }

  return importStatus
}

export const useImportStatus = (importReference: string) => {
  const importStatus: ImportStatus = reactive({
    pending: 0,
    finished: 0,
    skipped: 0,
    errored: 0
  })

  fetchImportStatus(importReference).then((status) => {
    for (const key of Object.keys(status)) {
      importStatus[key as keyof ImportStatus] = status[key as keyof ImportStatus]
    }
  })

  useWebSocketHandler('import.status_updated', async (event) => {
    if (event.upload.import_reference !== importReference) {
      return
    }

    importStatus[event.old_status] -= 1
    importStatus[event.new_status] += 1
  })

  return importStatus
}

export const useImports = () => {
  return {
    fetchImportStatus
  }
}

/// <reference lib="webworker" />

import { getCoverUrl, getTags, type Tags } from '~/ui/composables/metadata'

export interface MetadataParsingSuccess {
  id: string
  status: 'success'
  tags: Tags
  coverUrl: string | undefined
}

export interface MetadataParsingFailure {
  id: string
  status: 'failure'
  error: Error
}

export type MetadataParsingResult = MetadataParsingSuccess | MetadataParsingFailure

const parse = async (id: string, file: File) => {
  try {
    console.log(`[${id}] parsing...`)
    const tags = await getTags(file)
    console.log(`[${id}] tags:`, tags)
    const coverUrl = await getCoverUrl(tags)

    postMessage({ id, status: 'success', tags, coverUrl })
  } catch (error) {
    postMessage({ id, status: 'failure', error })
  }
}

addEventListener('message', async (event) => {
  parse(event.data.id, event.data.file)
})

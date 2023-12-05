/// <reference lib="webworker" />

import { getCoverUrl, getTags, type Tags } from '~/ui/composables/metadata'

export interface MetadataParsingSuccess {
  id: number
  status: 'success'
  tags: Tags
  coverUrl: string | undefined
}

export interface MetadataParsingFailure {
  id: number
  status: 'failure'
  error: Error
}

export type MetadataParsingResult = MetadataParsingSuccess | MetadataParsingFailure


const parse = async (id: number, file: File) => {
  try {
    console.log(`[${id}] parsing...`)
    const tags = await getTags(file)
    console.log(`[${id}] tags:`, tags)
    const coverUrl = await getCoverUrl(tags)

    postMessage({
      id,
      status: 'success',
      tags,
      coverUrl
    })
  } catch (error) {
    postMessage({
      id,
      status: 'failure',
      error
    })
  }
}

const queue = []
let queuePromise = Promise.resolve()
addEventListener('message', async (event) => {
  const id = event.data.id as number
  const file = event.data.file as File
  parse(id, file)
})

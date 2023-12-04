/// <reference lib="webworker" />

import { getCoverUrl, getTags } from '~/ui/composables/metadata'


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

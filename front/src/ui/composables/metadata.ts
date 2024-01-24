// TODO: use when Firefox issue is resolved, see: https://github.com/Borewit/music-metadata-browser/issues/948
// import * as Metadata from 'music-metadata-browser'
// import type { ICommonTagsResult } from 'music-metadata-browser'
//
// export type Tags = ICommonTagsResult
//
// export const getCoverUrl = async (tags: ICommonTagsResult[] | undefined): Promise<string | undefined> => {
//   if (pictures.length === 0) return undefined
//
//   const picture = Metadata.selectCover(pictures)
//
//   return await new Promise((resolve, reject) => {
//     const reader = Object.assign(new FileReader(), {
//       onload: () => resolve(reader.result as string),
//       onerror: () => reject(reader.error)
//     })
//
//     reader.readAsDataURL(new File([picture.data], "", { type: picture.type }))
//   })
// }
//
// export const getTags = async (file: File) => {
//   return Metadata.parseBlob(file).then(metadata => metadata.common)
// }

import * as jsmediaTags from 'jsmediatags/dist/jsmediatags.min.js'
import type { ShortcutTags } from 'jsmediatags'

const REQUIRED_TAGS = ['title', 'artist', 'album']

export type Tags = ShortcutTags

export const getCoverUrl = async (tags: Tags): Promise<string | undefined> => {
  if (!tags.picture) return undefined
  const { picture } = tags

  return await new Promise((resolve, reject) => {
    const reader = Object.assign(new FileReader(), {
      onload: () => resolve(reader.result as string),
      onerror: () => reject(reader.error)
    })

    reader.readAsDataURL(new File([picture.data], '', { type: picture.type }))
  })
}

export const getTags = async (file: File) => {
  return new Promise((resolve, reject) => {
    jsmediaTags.read(file, {
      onSuccess: ({ tags }) => {
        if (tags.picture?.data) {
          tags.picture.data = new Uint8Array(tags.picture.data)
        }

        const missingTags = REQUIRED_TAGS.filter(tag => !tags[tag])
        if (missingTags.length > 0) {
          return reject(new Error(`Missing tags: ${missingTags.join(', ')}`))
        }

        resolve(tags)
      },
      onError: (error) => reject(error)
    })
  })
}

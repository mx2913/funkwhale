import type { Track, Album, ArtistCredit, QueueItemSource } from '~/types'
import { useStore } from '~/store'

const store = useStore()

export function generateTrackCreditString (track: Track | Album | null): string | null {
  if (!track || !track.artist_credit || track.artist_credit.length === 0) {
    return null
  }

  const artistCredits = track.artist_credit.map((ac: ArtistCredit) => {
    return ac.artist.name + (ac.joinphrase ? ` ${ac.joinphrase}` : '')
  })

  return artistCredits.join()
}

export function generateTrackCreditStringFromQueue (track: QueueItemSource | null): string | null {
  if (!track || !track.artistCredit || track.artistCredit.length === 0) {
    return null
  }

  const artistCredits = track.artistCredit.map((ac: ArtistCredit) => {
    return ac.artist.name + (ac.joinphrase ? ` ${ac.joinphrase}` : '')
  })

  return artistCredits.join()
}

export function getArtistCoverUrl (artistCredit: ArtistCredit[]): string | undefined {
  for (let i = 0; i < artistCredit.length; i++) {
    const cover = artistCredit[i]?.artist?.cover
    const mediumSquareCrop = cover?.urls?.medium_square_crop

    if (mediumSquareCrop) {
      return store.getters['instance/absoluteUrl'](mediumSquareCrop)
    }
  }
  return undefined
}

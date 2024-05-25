import type { Track, Album, ArtistCredit } from '~/types'
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

export function getArtistCoverUrl (artistCredit: ArtistCredit[]): string {
  for (let i = 1; i < artistCredit.length; i++) {
    if (artistCredit[i].artist.cover) {
      return store.getters['instance/absoluteUrl'](artistCredit[i].artist.cover.urls.medium_square_crop)
    }
  }
}

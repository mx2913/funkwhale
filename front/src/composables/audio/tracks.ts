import type { QueueTrack, QueueTrackSource } from '~/composables/audio/queue'
import type { Track, Upload } from '~/types'
import type { Sound } from '~/api/player'

import { createGlobalState, syncRef, useTimeoutFn, whenever } from '@vueuse/core'
import { computed, ref, watchEffect } from 'vue'
import { LRUCache } from 'lru-cache'

import { connectAudioSource } from '~/composables/audio/audio-api'
import { usePlayer } from '~/composables/audio/player'
import { useQueue } from '~/composables/audio/queue'
import { soundImplementation } from '~/api/player'

import useLogger from '~/composables/useLogger'
import store from '~/store'

import axios from 'axios'

const ALLOWED_PLAY_TYPES: (CanPlayTypeResult | undefined)[] = ['maybe', 'probably']
const AUDIO_ELEMENT = document.createElement('audio')

const logger = useLogger()

const soundPromises = new Map<number, Promise<Sound>>()
const soundCache = new LRUCache<number, Sound>({
  max: 3,
  dispose: (sound) => sound.dispose()
})

const currentTrack = ref<QueueTrack>()

export const fetchTrackSources = async (id: number): Promise<QueueTrackSource[]> => {
  const { uploads } = await axios.get(`tracks/${id}/`)
    .then(response => response.data as Track, () => ({ uploads: [] as Upload[] }))

  return uploads.map(upload => ({
    uuid: upload.uuid,
    duration: upload.duration,
    mimetype: upload.mimetype,
    bitrate: upload.bitrate,
    url: store.getters['instance/absoluteUrl'](upload.listen_url)
  }))
}

const getTrackSources = async (track: QueueTrack): Promise<QueueTrackSource[]> => {
  const token = store.state.auth.authenticated && store.state.auth.scopedTokens.listen
  const appendToken = (url: string) => {
    if (token) {
      const newUrl = new URL(url)
      newUrl.searchParams.set('token', token)
      return newUrl.toString()
    }

    return url
  }

  if (track.sources.length === 0) {
    track.sources = await fetchTrackSources(track.id)
  }

  const sources: QueueTrackSource[] = track.sources
    .map((source) => ({
      ...source,
      url: appendToken(store.getters['instance/absoluteUrl'](source.url))
    }))

  // NOTE: Add a transcoded MP3 src at the end for browsers
  //       that do not support other codecs to be able to play it :)
  if (sources.length > 0) {
    const original = sources[0]
    const url = new URL(original.url)
    url.searchParams.set('to', 'mp3')

    const bitrate = Math.min(320000, original.bitrate ?? Infinity)
    sources.push({ uuid: 'transcoded', mimetype: 'audio/mpeg', url: url.toString(), bitrate })
  }

  return sources
    // NOTE: Filter out repeating and unplayable media types
    .filter(({ mimetype, bitrate }, index, array) => array.findIndex((upload) => upload.mimetype + upload.bitrate === mimetype + bitrate) === index)
    .filter(({ mimetype }) => ALLOWED_PLAY_TYPES.includes(AUDIO_ELEMENT.canPlayType(`${mimetype}`)))
}

// Use Tracks
export const useTracks = createGlobalState(() => {
  const createSound = async (track: QueueTrack): Promise<Sound> => {
    if (soundCache.has(track.id)) {
      return soundCache.get(track.id) as Sound
    }

    if (soundPromises.has(track.id)) {
      return soundPromises.get(track.id) as Promise<Sound>
    }

    const createSoundPromise = async () => {
      const sources = await getTrackSources(track)
      const { playNext } = useQueue()

      const SoundImplementation = soundImplementation.value
      const sound = new SoundImplementation(sources)

      sound.onSoundEnd(() => {
        logger.log('TRACK ENDED, PLAYING NEXT')

        // NOTE: We push it to the end of the job queue
        setTimeout(() => playNext(), 0)
      })

      // NOTE: When the sound is disposed, we need to delete it from the cache (#2157)
      whenever(sound.isDisposed, () => {
        soundCache.delete(track.id)
      })

      // NOTE: Bump current track to ensure that it lives despite enqueueing 3 tracks as next track:
      //
      //       In every queue we have 3 tracks that are cached, in the order, they're being played:
      //
      //       A B C
      //       ^ ^ ^______ C is the next track from the queue that has been preloaded in the 'Preload next track' code section
      //       \ \________ B is the currently played track
      //       \__________ A is the previous track
      //
      //       Now, let's make an assumption that caching next tracks is more valuable than caching previous tracks.
      //       To prevent track B from being disposed from the cache after enqueueing D and E tracks as 'next track' twice, we can fetch the track from the cache and bump its counter
      //       The cache state would be as follows:
      //
      //       A B C  --(user enqueues D as next track)->  C B D  --(user enqueues E as next track)->  D B E
      //
      //       Note that the queue would be changed as follows:
      //
      //       A B C  ->  A B D C  ->  A B E D C
      //
      //       This means that the currently playing track (B) is never removed from the cache (and isn't disposed prematurely) during its playback.
      //       However, we end up in a situation where previous track isn't cached anymore but two next tracks are.
      //       That implies that when user changes to the previous track (only before track B ends), a new sound instance would be created,
      //       which means that there might be some network requests before playback.
      if (currentTrack.value) {
        soundCache.get(currentTrack.value.id)
      }

      // Add track to the sound cache and remove from the promise cache
      soundCache.set(track.id, sound)
      soundPromises.delete(track.id)

      return sound
    }

    logger.log('NO TRACK IN CACHE, CREATING', track)
    const soundPromise = createSoundPromise()
    soundPromises.set(track.id, soundPromise)
    return soundPromise
  }

  // Skip when errored
  const { start: soundUnplayable, stop: abortSoundUnplayableTimeout } = useTimeoutFn(() => {
    const { isPlaying, looping, LoopingMode, pauseReason, PauseReason } = usePlayer()
    const { playNext } = useQueue()

    if (looping.value !== LoopingMode.LoopTrack) {
      return playNext()
    }

    isPlaying.value = false
    pauseReason.value = PauseReason.Errored
  }, 3000, { immediate: false })

  // Preload next track
  const { start: preload, stop: abortPreload } = useTimeoutFn(async (track: QueueTrack) => {
    const sound = await createSound(track)
    await sound.preload()
  }, 100, { immediate: false })

  // Create track from queue
  const createTrack = async (index: number) => {
    abortSoundUnplayableTimeout()

    const { queue, currentIndex } = useQueue()
    if (queue.value.length <= index || index === -1) return
    logger.log('LOADING TRACK', index)

    const track = queue.value[index]
    const sound = await createSound(track)

    if (!sound.playable) {
      soundUnplayable()
      return
    }

    logger.log('CONNECTING NODE', sound)

    sound.audioNode.disconnect()
    connectAudioSource(sound.audioNode)

    const { isPlaying } = usePlayer()
    if (isPlaying.value && index === currentIndex.value) {
      await sound.play()
    }
  }

  // NOTE: We want to have it called only once, hence we're using createGlobalState
  const initialize = createGlobalState(() => {
    const { currentIndex, currentTrack: track, queue, hasNext } = useQueue()

    whenever(track, () => {
      createTrack(currentIndex.value)
    }, { immediate: true })

    let lastTrack: QueueTrack
    watchEffect(async () => {
      abortPreload()

      if (!hasNext.value) return

      const nextTrack = queue.value[currentIndex.value + 1]
      if (!nextTrack || lastTrack === nextTrack) return
      lastTrack = nextTrack

      // NOTE: Preload next track
      preload(nextTrack)
    })

    syncRef(track, currentTrack, {
      direction: 'ltr'
    })
  })

  const currentSound = computed(() => soundCache.get(currentTrack.value?.id ?? -1))

  const clearCache = () => {
    return soundCache.clear()
  }

  return {
    initialize,
    createSound,
    createTrack,
    clearCache,
    currentSound
  }
})

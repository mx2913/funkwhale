import { LRUCache } from 'lru-cache'
import { currentIndex, useQueue } from '~/composables/audio/queue'
import { useTracks } from '~/composables/audio/tracks'
import { isEqual } from 'lodash-es'
import type { Sound } from '~/api/player'
import type { Track } from '~/types'

const { enqueue, enqueueAt, clear } = useQueue()

// @ts-expect-error We've added caches array in the mock file
const cache: LRUCache<number, Sound> = LRUCache.caches[0]

type CreateTrackFn = {
  (): Track
  id?: number
}

const createTrack = <CreateTrackFn>(() => {
  createTrack.id = createTrack.id ?? 0
  return { id: createTrack.id++, uploads: [] } as any as Track
})

const waitUntilCacheUpdated = async () => {
  const keys = [...cache.rkeys()]
  return vi.waitUntil(() => !isEqual(keys, [...cache.rkeys()]), { interval: 5 })
}

beforeAll(() => {
  const { initialize } = useTracks()
  initialize()
})

describe('cache', () => {
  beforeEach(async () => {
    createTrack.id = 0

    await clear()
    await enqueue(
      createTrack(),
      createTrack(),
      createTrack(),
      createTrack(),
      createTrack()
    )
  })

  it('useQueue().clear() clears track cache', async () => {
    expect(cache.size).toBe(1)
    await clear()
    expect(cache.size).toBe(0)
  })

  it('caches next track after 100ms', async () => {
    expect(cache.size).toBe(1)

    await waitUntilCacheUpdated()
    expect(cache.size).toBe(2)
  })

  it('preserves previous track in cache, when next track is playing', async () => {
    expect(cache.size).toBe(1)

    await waitUntilCacheUpdated()
    expect(cache.size).toBe(2)
    currentIndex.value += 1

    await waitUntilCacheUpdated()
    expect(cache.size).toBe(3)
  })

  it('maxes at 3 cache elements', async () => {
    expect(cache.size).toBe(1)
    const [[firstCachedId]] = cache.dump()

    await waitUntilCacheUpdated()
    expect(cache.size).toBe(2)
    currentIndex.value += 1

    await waitUntilCacheUpdated()
    expect(cache.size).toBe(3)
    currentIndex.value += 1

    await waitUntilCacheUpdated()
    expect(cache.size).toBe(3)
    expect(cache.dump().map(([id]) => id)).not.toContain(firstCachedId)
  })

  it('jumping around behaves correctly', async () => {
    currentIndex.value = 2
    // NOTE: waitUntilCacheUpdated() returns when first cache update is found
    //       That's why we need to call it twice after skipping the track
    await waitUntilCacheUpdated()
    await waitUntilCacheUpdated()
    expect([...cache.rkeys()]).toEqual([0, 2, 3])

    currentIndex.value = 3
    await waitUntilCacheUpdated()
    expect([...cache.rkeys()]).toEqual([2, 3, 4])

    // We change to the first song
    currentIndex.value = 0
    await waitUntilCacheUpdated()
    expect([...cache.rkeys()]).toEqual([3, 4, 0])

    // Now the next song should be enqueued
    await waitUntilCacheUpdated()
    expect([...cache.rkeys()]).toEqual([4, 0, 1])
  })

  describe('track enqueueing', () => {
    // NOTE: We always want to have tracks 0, 1, 2 in the cache
    beforeEach(async () => {
      currentIndex.value += 1
      // NOTE: waitUntilCacheUpdated() returns when first cache update is found
      //       That's why we need to call it twice after skipping the track
      await waitUntilCacheUpdated()
      await waitUntilCacheUpdated()
      expect(cache.size).toBe(3)
    })

    it('enqueueing track as next adds it to the cache', async () => {
      enqueueAt(currentIndex.value + 1, createTrack()) // id: 5
      await waitUntilCacheUpdated()
      const newIds = [...cache.rkeys()]
      expect(newIds).toEqual([2, 1, 5])
    })

    it('edge case: enqueueing track as next multiple times does not remove dispose current track', async () => {
      enqueueAt(currentIndex.value + 1, createTrack()) // id: 5
      await waitUntilCacheUpdated()
      enqueueAt(currentIndex.value + 1, createTrack()) // id: 6
      await waitUntilCacheUpdated()
      enqueueAt(currentIndex.value + 1, createTrack()) // id: 7
      await waitUntilCacheUpdated()
      const newIds = [...cache.rkeys()]
      expect(newIds).toEqual([6, 1, 7])
    })
  })
})

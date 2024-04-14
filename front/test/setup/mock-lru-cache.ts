import { vi } from 'vitest'

vi.doMock('lru-cache', async (importOriginal) => {
  const mod = await importOriginal<typeof import('lru-cache')>()

  class LRUCacheMock<K extends NonNullable<unknown>, V extends NonNullable<unknown>, FC> {
    static caches: typeof mod.LRUCache[] = []

    constructor (...args: ConstructorParameters<typeof mod.LRUCache<K, V, FC>>) {
      const cache = new mod.LRUCache<K, V, FC>(...args)
      LRUCacheMock.caches.push(cache as any)
      return cache
    }
  }

  return {
    ...mod,
    LRUCache: LRUCacheMock
  }
})

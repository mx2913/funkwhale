import { vi } from 'vitest'

// HACK: First we import the global store (and instance store indirectly) so that we don't fall into error pitfall
import _store from '~/store'

import { findDefaultInstanceUrl, TAURI_DEFAULT_INSTANCE_URL } from '~/store/instance'

afterEach(() => {
  vi.unstubAllEnvs()
})

describe('findDefaultInstanceUrl', () => {
  test('tauri', () => {
    vi.stubEnv('TAURI_ENV_PLATFORM', 'tauri')
    expect(findDefaultInstanceUrl()).toBe(TAURI_DEFAULT_INSTANCE_URL)
  })

  test('environment variable', () => {
    vi.stubEnv('VUE_APP_INSTANCE_URL', 'https://example.com')
    expect(findDefaultInstanceUrl()).toBe('https://example.com/')
  })

  test('location origin', () => {
    expect(findDefaultInstanceUrl()).toBe('http://localhost:3000/')
  })
})

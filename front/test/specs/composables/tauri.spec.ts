import { vi } from 'vitest'
import { isTauri } from '~/composables/tauri'

afterEach(() => {
  vi.unstubAllEnvs()
})

test('Correctly detects Tauri environment', () => {
  // Stub the Tauri environment variable
  vi.stubEnv('TAURI_ENV_PLATFORM', 'tauri')

  expect(isTauri()).toBe(true)
})

test('Correctly detects browser environment', () => {
  expect(isTauri()).toBe(false)
})

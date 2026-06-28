import { afterEach, vi } from 'vitest'
import { cleanup } from '@testing-library/react'
import '@testing-library/jest-dom'

class TestStorage implements Storage {
  private store: Record<string, string> = {}

  get length() {
    return Object.keys(this.store).length
  }

  clear() {
    this.store = {}
  }

  getItem(key: string) {
    return Object.prototype.hasOwnProperty.call(this.store, key)
      ? this.store[key]
      : null
  }

  key(index: number) {
    return Object.keys(this.store)[index] ?? null
  }

  removeItem(key: string) {
    delete this.store[key]
  }

  setItem(key: string, value: string) {
    this.store[key] = String(value)
  }
}

const installStorage = (name: 'localStorage' | 'sessionStorage') => {
  const storage = new TestStorage()

  Object.defineProperty(globalThis, 'Storage', {
    value: TestStorage,
    configurable: true,
    writable: true,
  })

  Object.defineProperty(globalThis, name, {
    value: storage,
    configurable: true,
    writable: true,
  })

  if (globalThis.window) {
    Object.defineProperty(globalThis.window, 'Storage', {
      value: TestStorage,
      configurable: true,
      writable: true,
    })

    Object.defineProperty(globalThis.window, name, {
      value: storage,
      configurable: true,
      writable: true,
    })
  }
}

installStorage('localStorage')
installStorage('sessionStorage')

// Cleanup after each test
afterEach(() => {
  cleanup()
})

// Mock URL.createObjectURL and URL.revokeObjectURL (not available in jsdom)
globalThis.URL.createObjectURL = vi.fn(() => 'blob:mock-url')
globalThis.URL.revokeObjectURL = vi.fn()

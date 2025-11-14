import { useEffect } from 'react'

type Modifier = 'ctrl' | 'cmd' | 'alt' | 'shift'

export const useKeyboardShortcut = (
  key: string,
  callback: () => void,
  modifiers: Modifier[] = []
) => {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const hasModifiers = modifiers.every((mod) => {
        if (mod === 'ctrl') return e.ctrlKey
        if (mod === 'cmd') return e.metaKey
        if (mod === 'alt') return e.altKey
        if (mod === 'shift') return e.shiftKey
        return false
      })

      if (hasModifiers && e.key.toLowerCase() === key.toLowerCase()) {
        e.preventDefault()
        callback()
      }
    }

    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [key, callback, modifiers])
}

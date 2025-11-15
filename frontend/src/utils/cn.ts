import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * Utility function to merge Tailwind CSS classes
 *
 * Combines clsx for conditional classes with tailwind-merge
 * to properly handle conflicting Tailwind classes
 *
 * @example
 * cn('px-2 py-1', 'px-4') // Returns 'py-1 px-4' (px-2 is overridden)
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

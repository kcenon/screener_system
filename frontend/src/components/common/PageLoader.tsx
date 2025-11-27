/**
 * Page loading spinner for lazy-loaded routes.
 *
 * Used as Suspense fallback when code-split pages are loading.
 *
 * @module components/common/PageLoader
 * @category Components
 */

interface PageLoaderProps {
  /** Custom loading text */
  text?: string
}

/**
 * Full page loading spinner component.
 *
 * @example
 * ```tsx
 * <Suspense fallback={<PageLoader />}>
 *   <LazyLoadedPage />
 * </Suspense>
 * ```
 */
export default function PageLoader({ text = 'Loading...' }: PageLoaderProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] w-full">
      {/* Spinner */}
      <div className="relative">
        <div className="w-12 h-12 border-4 border-gray-200 dark:border-gray-700 rounded-full animate-spin border-t-blue-600 dark:border-t-blue-400" />
      </div>

      {/* Loading text */}
      <p className="mt-4 text-sm text-gray-500 dark:text-gray-400">{text}</p>
    </div>
  )
}

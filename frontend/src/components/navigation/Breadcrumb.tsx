import { Link, useLocation } from 'react-router-dom'
import { ChevronRight, Home } from 'lucide-react'

interface BreadcrumbItem {
  label: string
  path?: string
}

const pathLabels: Record<string, string> = {
  screener: 'Screener',
  stocks: 'Stocks',
  compare: 'Compare Stocks',
  watchlists: 'Watchlists',
  login: 'Login',
  register: 'Register',
}

export default function Breadcrumb() {
  const location = useLocation()
  const pathnames = location.pathname.split('/').filter((x) => x)

  if (pathnames.length === 0) {
    return null
  }

  const breadcrumbs: BreadcrumbItem[] = [
    { label: 'Home', path: '/' },
  ]

  let currentPath = ''
  pathnames.forEach((segment, index) => {
    currentPath += `/${segment}`

    // Skip numeric segments (like stock codes)
    if (/^\d+$/.test(segment)) {
      return
    }

    const label = pathLabels[segment] || segment.charAt(0).toUpperCase() + segment.slice(1)
    const isLast = index === pathnames.length - 1

    breadcrumbs.push({
      label,
      path: isLast ? undefined : currentPath,
    })
  })

  // Don't show breadcrumb for single-level pages
  if (breadcrumbs.length <= 2) {
    return null
  }

  return (
    <nav aria-label="Breadcrumb" className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
        <ol className="flex items-center space-x-2 text-sm">
          {breadcrumbs.map((crumb, index) => {
            const isFirst = index === 0

            return (
              <li key={crumb.path || crumb.label} className="flex items-center">
                {index > 0 && (
                  <ChevronRight className="text-gray-400 mx-2" size={16} />
                )}
                {crumb.path ? (
                  <Link
                    to={crumb.path}
                    className="flex items-center gap-1 text-gray-600 hover:text-gray-900 transition-colors"
                  >
                    {isFirst && <Home size={16} />}
                    <span>{crumb.label}</span>
                  </Link>
                ) : (
                  <span className="text-gray-900 font-medium">{crumb.label}</span>
                )}
              </li>
            )
          })}
        </ol>
      </div>
    </nav>
  )
}

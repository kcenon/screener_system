/**
 * Quick Actions Widget
 *
 * Provides quick access buttons to common features like
 * screening, watchlists, comparison, etc.
 */

import { Link } from 'react-router-dom'
import { Search, Eye, GitCompare, BarChart3, FileDown, TrendingUp } from 'lucide-react'

interface QuickAction {
  id: string
  title: string
  description: string
  icon: typeof Search
  href: string
  color: string
}

const quickActions: QuickAction[] = [
  {
    id: 'screening',
    title: 'New Screening',
    description: 'Filter stocks by criteria',
    icon: Search,
    href: '/screener',
    color: 'blue',
  },
  {
    id: 'watchlists',
    title: 'Watchlists',
    description: 'View all watchlists',
    icon: Eye,
    href: '/watchlists',
    color: 'green',
  },
  {
    id: 'compare',
    title: 'Compare Stocks',
    description: 'Side-by-side comparison',
    icon: GitCompare,
    href: '/compare',
    color: 'purple',
  },
  {
    id: 'market',
    title: 'Market Overview',
    description: 'Sector & market analysis',
    icon: TrendingUp,
    href: '/market',
    color: 'orange',
  },
]

/**
 * Get color classes for action button
 */
function getColorClasses(color: string): {
  bg: string
  hover: string
  text: string
  iconBg: string
} {
  const colorMap: Record<string, { bg: string; hover: string; text: string; iconBg: string }> = {
    blue: {
      bg: 'bg-blue-50',
      hover: 'hover:bg-blue-100',
      text: 'text-blue-700',
      iconBg: 'bg-blue-100',
    },
    green: {
      bg: 'bg-green-50',
      hover: 'hover:bg-green-100',
      text: 'text-green-700',
      iconBg: 'bg-green-100',
    },
    purple: {
      bg: 'bg-purple-50',
      hover: 'hover:bg-purple-100',
      text: 'text-purple-700',
      iconBg: 'bg-purple-100',
    },
    orange: {
      bg: 'bg-orange-50',
      hover: 'hover:bg-orange-100',
      text: 'text-orange-700',
      iconBg: 'bg-orange-100',
    },
  }

  return colorMap[color] || colorMap.blue
}

/**
 * Quick Action Button Component
 */
function QuickActionButton({ action }: { action: QuickAction }) {
  const Icon = action.icon
  const colors = getColorClasses(action.color)

  return (
    <Link
      to={action.href}
      className={`block p-4 ${colors.bg} ${colors.hover} rounded-lg transition-colors`}
    >
      <div className="flex items-start gap-3">
        <div className={`p-2 ${colors.iconBg} rounded-lg flex-shrink-0`}>
          <Icon className={`w-5 h-5 ${colors.text}`} />
        </div>

        <div className="flex-1 min-w-0">
          <h3 className={`font-semibold ${colors.text} mb-1`}>{action.title}</h3>
          <p className="text-sm text-gray-600">{action.description}</p>
        </div>
      </div>
    </Link>
  )
}

/**
 * QuickActionsWidget Component
 */
export default function QuickActionsWidget() {
  return (
    <div className="space-y-3">
      {quickActions.map((action) => (
        <QuickActionButton key={action.id} action={action} />
      ))}
    </div>
  )
}

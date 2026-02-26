import {
  LucideIcon,
  TrendingUp,
  Filter,
  ListTodo,
  BarChart3,
} from 'lucide-react'

export interface NavigationItem {
  /** Translation key for the label (e.g., 'nav.market') */
  labelKey: string
  path?: string
  icon?: LucideIcon
  auth?: boolean
  children?: NavigationItem[]
  badge?: string
}

export const navigationConfig: NavigationItem[] = [
  {
    labelKey: 'nav.market',
    path: '/market',
    icon: BarChart3,
  },
  {
    labelKey: 'nav.screener',
    path: '/screener',
    icon: Filter,
  },
  {
    labelKey: 'nav.watchlists',
    path: '/watchlists',
    icon: ListTodo,
  },
  {
    labelKey: 'nav.compare',
    path: '/compare',
    icon: TrendingUp,
  },
]

export const userMenuConfig: NavigationItem[] = [
  {
    labelKey: 'nav.login',
    path: '/login',
  },
  {
    labelKey: 'nav.signup',
    path: '/register',
  },
]

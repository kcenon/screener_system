import { LucideIcon, TrendingUp, Filter, ListTodo } from 'lucide-react'

export interface NavigationItem {
  label: string
  path?: string
  icon?: LucideIcon
  auth?: boolean
  children?: NavigationItem[]
  badge?: string
}

export const navigationConfig: NavigationItem[] = [
  {
    label: 'Screener',
    path: '/screener',
    icon: Filter,
  },
  {
    label: 'Watchlists',
    path: '/watchlists',
    icon: ListTodo,
  },
  {
    label: 'Compare',
    path: '/compare',
    icon: TrendingUp,
  },
]

export const userMenuConfig: NavigationItem[] = [
  {
    label: 'Login',
    path: '/login',
  },
  {
    label: 'Register',
    path: '/register',
  },
]

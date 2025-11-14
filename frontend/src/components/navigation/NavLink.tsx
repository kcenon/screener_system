import { Link, useLocation } from 'react-router-dom'
import { LucideIcon } from 'lucide-react'
import clsx from 'clsx'

interface NavLinkProps {
  to: string
  label: string
  icon?: LucideIcon
  onClick?: () => void
  className?: string
}

export default function NavLink({ to, label, icon: Icon, onClick, className }: NavLinkProps) {
  const location = useLocation()
  const isActive = location.pathname === to || location.pathname.startsWith(to + '/')

  return (
    <Link
      to={to}
      onClick={onClick}
      className={clsx(
        'flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors',
        isActive
          ? 'bg-blue-50 text-blue-700'
          : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900',
        className
      )}
    >
      {Icon && <Icon size={18} />}
      <span>{label}</span>
    </Link>
  )
}

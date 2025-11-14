import { navigationConfig } from '@/config/navigation'
import NavLink from './NavLink'

interface NavMenuProps {
  className?: string
}

export default function NavMenu({ className }: NavMenuProps) {
  return (
    <nav className={className}>
      <ul className="flex items-center gap-1">
        {navigationConfig.map((item) => (
          <li key={item.path || item.label}>
            {item.path && (
              <NavLink
                to={item.path}
                label={item.label}
                icon={item.icon}
              />
            )}
          </li>
        ))}
      </ul>
    </nav>
  )
}

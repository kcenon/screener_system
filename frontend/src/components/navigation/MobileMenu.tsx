import { useState } from 'react'
import { Menu, X } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { navigationConfig } from '@/config/navigation'
import { useAuthStatus, useLogout } from '@/hooks/useAuth'
import clsx from 'clsx'

export default function MobileMenu() {
  const { t } = useTranslation()
  const [isOpen, setIsOpen] = useState(false)
  const location = useLocation()
  const { user } = useAuthStatus()
  const logoutMutation = useLogout()

  const handleLogout = () => {
    logoutMutation.mutate()
    closeMenu()
  }

  const closeMenu = () => setIsOpen(false)

  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path + '/')
  }

  return (
    <>
      {/* Hamburger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 text-gray-700 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-700 rounded-md lg:hidden transition-colors"
        aria-label="Toggle menu"
      >
        {isOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Mobile Menu Overlay */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black bg-opacity-50 dark:bg-opacity-70 z-40 lg:hidden"
            onClick={closeMenu}
          />

          {/* Menu Panel */}
          <div className="fixed top-0 left-0 bottom-0 w-64 bg-white dark:bg-gray-800 shadow-xl z-50 lg:hidden overflow-y-auto transition-colors">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">{t('app.name')}</h2>
              <button
                onClick={closeMenu}
                className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-700 rounded-md transition-colors"
                aria-label="Close menu"
              >
                <X size={20} />
              </button>
            </div>

            {/* Navigation Links */}
            <nav className="p-4">
              <ul className="space-y-1">
                {navigationConfig.map((item) => {
                  const Icon = item.icon
                  if (!item.path) return null

                  return (
                    <li key={item.path}>
                      <Link
                        to={item.path}
                        onClick={closeMenu}
                        className={clsx(
                          'flex items-center gap-3 px-3 py-2 rounded-md text-base font-medium transition-colors',
                          isActive(item.path)
                            ? 'bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
                            : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-white'
                        )}
                      >
                        {Icon && <Icon size={20} />}
                        <span>{t(item.labelKey)}</span>
                      </Link>
                    </li>
                  )
                })}
              </ul>
            </nav>

            {/* User Section */}
            <div className="border-t border-gray-200 dark:border-gray-700 p-4 mt-auto">
              {user ? (
                <>
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 bg-blue-600 dark:bg-blue-500 rounded-full flex items-center justify-center text-white font-semibold">
                      {user.name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">{user.name}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">{user.email}</p>
                    </div>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="w-full px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20 rounded-md transition-colors"
                  >
                    {t('nav.logout')}
                  </button>
                </>
              ) : (
                <div className="space-y-2">
                  <Link
                    to="/login"
                    onClick={closeMenu}
                    className="block w-full px-3 py-2 text-sm font-medium text-center text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 rounded-md transition-colors"
                  >
                    {t('nav.login')}
                  </Link>
                  <Link
                    to="/register"
                    onClick={closeMenu}
                    className="block w-full px-3 py-2 text-sm font-medium text-center text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 rounded-md transition-colors"
                  >
                    {t('nav.signup')}
                  </Link>
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </>
  )
}

import { Link } from 'react-router-dom'
import { BarChart3 } from 'lucide-react'
import NavMenu from './NavMenu'
import MobileMenu from './MobileMenu'
import UserMenu from './UserMenu'
import GlobalSearch from './GlobalSearch'
import { ThemeToggle } from '@/components/common/ThemeToggle'

export default function Navbar() {
  return (
    <header className="bg-white dark:bg-gray-800 shadow-sm sticky top-0 z-30 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-8">
            <Link to="/" className="flex items-center gap-2 text-xl font-bold text-gray-900 dark:text-white">
              <BarChart3 className="text-blue-600 dark:text-blue-400" size={28} />
              <span className="hidden sm:inline">Stock Screener</span>
            </Link>

            {/* Desktop Navigation */}
            <NavMenu className="hidden lg:block" />
          </div>

          {/* Right Section */}
          <div className="flex items-center gap-4">
            {/* Global Search */}
            <div className="hidden md:block">
              <GlobalSearch />
            </div>

            {/* Theme Toggle */}
            <ThemeToggle />

            {/* User Menu */}
            <div className="hidden lg:block">
              <UserMenu />
            </div>

            {/* Mobile Menu */}
            <MobileMenu />
          </div>
        </div>
      </div>
    </header>
  )
}

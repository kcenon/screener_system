/**
 * Card Component with Elevation System
 *
 * A flexible card component with multiple elevation levels and variants.
 * Provides visual depth through shadows and supports interactive states.
 *
 * @module design-system/components/Card
 */

import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/utils/cn'

/**
 * Card component variants using CVA (class-variance-authority)
 *
 * Provides type-safe variant composition with Tailwind classes
 */
const cardVariants = cva(
  // Base styles applied to all cards
  'rounded-lg transition-all duration-200',
  {
    variants: {
      /**
       * Elevation level (shadow depth)
       * - flat: No shadow (flush with background)
       * - low: Subtle shadow for subtle elevation
       * - medium: Moderate shadow for standard cards
       * - high: Strong shadow for prominent cards
       */
      elevation: {
        flat: 'shadow-none',
        low: 'shadow-card',
        medium: 'shadow-lg',
        high: 'shadow-xl',
      },

      /**
       * Interactive state
       * - true: Adds hover effects (lift on hover)
       * - false: Static card
       */
      interactive: {
        true: 'hover:shadow-card-hover cursor-pointer active:scale-[0.98]',
        false: '',
      },

      /**
       * Visual variant
       * - default: Standard card with solid background
       * - glass: Glassmorphism effect (translucent with blur)
       * - gradient: Subtle gradient background
       */
      variant: {
        default:
          'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700',
        glass:
          'bg-white/70 dark:bg-gray-800/70 backdrop-blur-lg border border-white/30 dark:border-gray-700/30',
        gradient:
          'bg-gradient-card-light dark:bg-gradient-card-dark border border-gray-200 dark:border-gray-700',
      },

      /**
       * Padding size
       * - none: No padding (for custom layouts)
       * - sm: Small padding (12px)
       * - md: Medium padding (16px)
       * - lg: Large padding (24px)
       */
      padding: {
        none: 'p-0',
        sm: 'p-3',
        md: 'p-4',
        lg: 'p-6',
      },
    },
    defaultVariants: {
      elevation: 'low',
      interactive: false,
      variant: 'default',
      padding: 'md',
    },
  },
)

/**
 * Card Props Interface
 */
export interface CardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> {
  /**
   * Card content
   */
  children: React.ReactNode

  /**
   * Additional CSS classes
   */
  className?: string

  /**
   * Optional click handler (automatically sets interactive=true)
   */
  onClick?: () => void
}

/**
 * Card Component
 *
 * Flexible card component with elevation system and multiple variants
 *
 * @example
 * ```tsx
 * // Standard card
 * <Card elevation="medium">
 *   <h2>Title</h2>
 *   <p>Content</p>
 * </Card>
 *
 * // Interactive card with glass effect
 * <Card
 *   variant="glass"
 *   elevation="high"
 *   interactive
 *   onClick={() => console.log('Clicked')}
 * >
 *   Click me
 * </Card>
 *
 * // Gradient card with custom padding
 * <Card variant="gradient" padding="lg">
 *   Premium content
 * </Card>
 * ```
 */
export function Card({
  children,
  elevation,
  interactive,
  variant,
  padding,
  className,
  onClick,
  ...props
}: CardProps) {
  return (
    <div
      className={cn(
        cardVariants({
          elevation,
          interactive: interactive || !!onClick,
          variant,
          padding,
        }),
        className,
      )}
      onClick={onClick}
      {...props}
    >
      {children}
    </div>
  )
}

/**
 * CardHeader Component
 *
 * Standardized card header with optional action buttons
 */
export interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string
  subtitle?: string
  action?: React.ReactNode
  className?: string
}

export function CardHeader({
  title,
  subtitle,
  action,
  className,
  ...props
}: CardHeaderProps) {
  return (
    <div
      className={cn(
        'flex items-start justify-between pb-3 border-b border-gray-200 dark:border-gray-700',
        className,
      )}
      {...props}
    >
      <div>
        <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100">
          {title}
        </h3>
        {subtitle && (
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            {subtitle}
          </p>
        )}
      </div>
      {action && <div className="flex-shrink-0 ml-4">{action}</div>}
    </div>
  )
}

/**
 * CardContent Component
 *
 * Standardized card content area with consistent spacing
 */
export interface CardContentProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
  className?: string
}

export function CardContent({
  children,
  className,
  ...props
}: CardContentProps) {
  return (
    <div className={cn('py-4', className)} {...props}>
      {children}
    </div>
  )
}

/**
 * CardFooter Component
 *
 * Standardized card footer for actions or metadata
 */
export interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
  className?: string
}

export function CardFooter({
  children,
  className,
  ...props
}: CardFooterProps) {
  return (
    <div
      className={cn(
        'pt-3 border-t border-gray-200 dark:border-gray-700',
        className,
      )}
      {...props}
    >
      {children}
    </div>
  )
}

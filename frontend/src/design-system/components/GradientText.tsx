/**
 * GradientText Component
 *
 * Renders text with gradient color effects for premium, AI, or branded content.
 * Uses CSS background-clip technique for smooth gradient text.
 *
 * @module design-system/components/GradientText
 */

import { cn } from '@/utils/cn'

/**
 * Available gradient presets
 */
export type GradientPreset =
  | 'premium'
  | 'ai'
  | 'hero'
  | 'bullish'
  | 'bearish'
  | 'custom'

/**
 * Gradient configuration map
 */
const gradientPresets: Record<GradientPreset, string> = {
  /**
   * Premium features (gold gradient)
   * Used for: Premium badges, pro features
   */
  premium: 'bg-gradient-to-r from-yellow-500 to-orange-600',

  /**
   * AI insights (purple gradient)
   * Used for: AI-generated content, ML predictions
   */
  ai: 'bg-gradient-to-r from-purple-500 to-indigo-600',

  /**
   * Hero sections (blue gradient)
   * Used for: Landing page headlines, CTAs
   */
  hero: 'bg-gradient-to-r from-blue-500 to-purple-600',

  /**
   * Bullish sentiment (green gradient)
   * Used for: Positive market indicators
   */
  bullish: 'bg-gradient-to-r from-green-500 to-emerald-600',

  /**
   * Bearish sentiment (red gradient)
   * Used for: Negative market indicators
   */
  bearish: 'bg-gradient-to-r from-red-500 to-rose-600',

  /**
   * Custom gradient (uses parent background)
   * Use with custom Tailwind gradient classes
   */
  custom: '',
}

/**
 * GradientText Props
 */
export interface GradientTextProps {
  /**
   * Text content to render with gradient
   */
  children: React.ReactNode

  /**
   * Gradient preset to use
   * @default 'premium'
   */
  gradient?: GradientPreset

  /**
   * Custom gradient class (only used with gradient='custom')
   * @example 'bg-gradient-to-r from-pink-500 to-purple-500'
   */
  customGradient?: string

  /**
   * Text size/weight classes
   * @example 'text-2xl font-bold'
   */
  className?: string

  /**
   * Apply animation on hover
   * @default false
   */
  animated?: boolean
}

/**
 * GradientText Component
 *
 * Renders text with smooth gradient color effects
 *
 * @example
 * ```tsx
 * // Premium badge
 * <GradientText gradient="premium">PRO</GradientText>
 *
 * // AI insight heading
 * <GradientText gradient="ai" className="text-xl font-bold">
 *   AI Analysis
 * </GradientText>
 *
 * // Custom gradient
 * <GradientText
 *   gradient="custom"
 *   customGradient="bg-gradient-to-r from-pink-500 to-blue-500"
 * >
 *   Custom Gradient
 * </GradientText>
 *
 * // Animated on hover
 * <GradientText gradient="hero" animated>
 *   Hover me!
 * </GradientText>
 * ```
 */
export function GradientText({
  children,
  gradient = 'premium',
  customGradient,
  className,
  animated = false,
}: GradientTextProps) {
  const gradientClass =
    gradient === 'custom' && customGradient
      ? customGradient
      : gradientPresets[gradient]

  return (
    <span
      className={cn(
        gradientClass,
        'bg-clip-text text-transparent font-bold',
        animated &&
          'transition-all duration-300 hover:scale-105 inline-block',
        className,
      )}
    >
      {children}
    </span>
  )
}

/**
 * GradientButton Component
 *
 * Button with gradient background (not text)
 *
 * @example
 * ```tsx
 * <GradientButton gradient="premium" onClick={() => {}}>
 *   Upgrade to Pro
 * </GradientButton>
 * ```
 */
export interface GradientButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /**
   * Gradient preset
   */
  gradient?: GradientPreset

  /**
   * Custom gradient class
   */
  customGradient?: string

  /**
   * Button size
   */
  size?: 'sm' | 'md' | 'lg'
}

const buttonSizes = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-base',
  lg: 'px-6 py-3 text-lg',
}

export function GradientButton({
  children,
  gradient = 'premium',
  customGradient,
  size = 'md',
  className,
  ...props
}: GradientButtonProps) {
  const gradientClass =
    gradient === 'custom' && customGradient
      ? customGradient
      : gradientPresets[gradient]

  return (
    <button
      className={cn(
        gradientClass,
        buttonSizes[size],
        'rounded-lg font-semibold text-white',
        'hover:opacity-90 active:scale-95',
        'transition-all duration-200',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        className,
      )}
      {...props}
    >
      {children}
    </button>
  )
}

/**
 * GradientBadge Component
 *
 * Small badge with gradient background
 *
 * @example
 * ```tsx
 * <GradientBadge gradient="premium">PRO</GradientBadge>
 * <GradientBadge gradient="ai">AI</GradientBadge>
 * ```
 */
export interface GradientBadgeProps {
  children: React.ReactNode
  gradient?: GradientPreset
  customGradient?: string
  className?: string
}

export function GradientBadge({
  children,
  gradient = 'premium',
  customGradient,
  className,
}: GradientBadgeProps) {
  const gradientClass =
    gradient === 'custom' && customGradient
      ? customGradient
      : gradientPresets[gradient]

  return (
    <span
      className={cn(
        gradientClass,
        'inline-flex items-center px-2.5 py-0.5 rounded-full',
        'text-xs font-semibold text-white',
        className,
      )}
    >
      {children}
    </span>
  )
}

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  // Enable class-based dark mode
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Primary (Financial Blue) - Extended palette
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6', // Main
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },

        // Market Colors (Semantic) - Gain
        gain: {
          50: '#ecfdf5',
          100: '#d1fae5',
          200: '#a7f3d0',
          300: '#6ee7b7',
          400: '#34d399',
          500: '#10b981', // Default
          600: '#059669',
          700: '#047857',
          800: '#065f46',
          900: '#064e3b',
        },

        // Market Colors (Semantic) - Loss
        loss: {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5',
          400: '#f87171',
          500: '#ef4444', // Default
          600: '#dc2626',
          700: '#b91c1c',
          800: '#991b1b',
          900: '#7f1d1d',
        },

        // Accent Colors - Gold (Premium features)
        gold: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b', // Default
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
        },

        // Accent Colors - Purple (AI insights)
        purple: {
          50: '#faf5ff',
          100: '#f3e8ff',
          200: '#e9d5ff',
          300: '#d8b4fe',
          400: '#c084fc',
          500: '#a855f7',
          600: '#9333ea',
          700: '#7e22ce',
          800: '#6b21a8',
          900: '#581c87',
        },

        // Accent Colors - Cyan (Notifications)
        cyan: {
          50: '#ecfeff',
          100: '#cffafe',
          200: '#a5f3fc',
          300: '#67e8f9',
          400: '#22d3ee',
          500: '#06b6d4', // Default
          600: '#0891b2',
          700: '#0e7490',
          800: '#155e75',
          900: '#164e63',
        },

        // Semantic Colors
        success: '#10b981',
        warning: '#f59e0b',
        danger: '#ef4444',
        info: '#3b82f6',

        // Extended Gray scale
        gray: {
          750: '#2d3748', // Custom color for elevated surfaces in dark mode
        },
      },

      // Gradient Definitions
      backgroundImage: {
        'gradient-hero': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'gradient-card-light': 'linear-gradient(145deg, #ffffff 0%, #f3f4f6 100%)',
        'gradient-card-dark': 'linear-gradient(145deg, #1f2937 0%, #111827 100%)',
        'gradient-premium': 'linear-gradient(90deg, #f59e0b 0%, #d97706 100%)',
        'gradient-ai': 'linear-gradient(90deg, #a855f7 0%, #7e22ce 100%)',
        'gradient-bullish': 'linear-gradient(90deg, #10b981 0%, #059669 100%)',
        'gradient-bearish': 'linear-gradient(90deg, #ef4444 0%, #dc2626 100%)',
      },

      // Box Shadows (Elevation System)
      boxShadow: {
        // Standard shadows (Tailwind defaults extended)
        'xs': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'sm': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
        'inner': 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',

        // Custom elevations for components
        'card': '0 4px 12px rgba(0, 0, 0, 0.08)',
        'card-hover': '0 8px 24px rgba(0, 0, 0, 0.12)',
        'modal': '0 20px 60px rgba(0, 0, 0, 0.3)',
        'dropdown': '0 10px 25px rgba(0, 0, 0, 0.15)',

        // Neumorphism (subtle 3D effect)
        'neomorph-light': '8px 8px 16px #d1d9e6, -8px -8px 16px #ffffff',
        'neomorph-dark': '8px 8px 16px #0f1419, -8px -8px 16px #2d3748',
      },
    },
  },
  plugins: [],
}

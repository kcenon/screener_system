import { afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom';

// Cleanup after each test
afterEach(() => {
  cleanup();
});

// Mock URL.createObjectURL and URL.revokeObjectURL (not available in jsdom)
global.URL.createObjectURL = vi.fn(() => 'blob:mock-url');
global.URL.revokeObjectURL = vi.fn();

// Mock react-i18next
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, options?: { count?: number }) => {
      // Return the key itself or formatted key for testing
      if (options?.count !== undefined) {
        return `${key.split('.').pop()} (${options.count})`;
      }
      // Return the last part of the key for readable test output
      const parts = key.split('.');
      return parts[parts.length - 1];
    },
    i18n: {
      language: 'ko',
      changeLanguage: vi.fn(),
    },
  }),
  initReactI18next: {
    type: '3rdParty',
    init: vi.fn(),
  },
  Trans: ({ children }: { children: React.ReactNode }) => children,
}));

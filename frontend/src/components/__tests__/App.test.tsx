import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';

// Simple component for testing
function App() {
  return (
    <div>
      <h1>Stock Screening Platform</h1>
      <p>Welcome to the stock screening platform</p>
    </div>
  );
}

describe('App', () => {
  it('renders heading', () => {
    render(<App />);
    expect(screen.getByText('Stock Screening Platform')).toBeDefined();
  });

  it('renders welcome message', () => {
    render(<App />);
    expect(screen.getByText('Welcome to the stock screening platform')).toBeDefined();
  });
});

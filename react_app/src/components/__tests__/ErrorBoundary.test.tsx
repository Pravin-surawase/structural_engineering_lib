import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { ErrorBoundary } from '../ui/ErrorBoundary';

// Component that throws an error
function ThrowError({ shouldThrow }: { shouldThrow: boolean }) {
  if (shouldThrow) {
    throw new Error('Test error');
  }
  return React.createElement('div', {}, 'No error');
}

describe('ErrorBoundary', () => {
  // Suppress console.error for these tests
  const originalError = console.error;
  beforeEach(() => {
    console.error = vi.fn();
  });
  afterEach(() => {
    console.error = originalError;
  });

  it('renders children when no error', () => {
    render(
      React.createElement(
        ErrorBoundary,
        { children: React.createElement(ThrowError, { shouldThrow: false }) }
      )
    );

    expect(screen.getByText('No error')).toBeInTheDocument();
  });

  it('catches error and shows fallback UI', () => {
    render(
      React.createElement(
        ErrorBoundary,
        { children: React.createElement(ThrowError, { shouldThrow: true }) }
      )
    );

    expect(screen.getByText(/Something went wrong/i)).toBeInTheDocument();
    expect(screen.queryByText('No error')).not.toBeInTheDocument();
  });

  it('displays error message', () => {
    render(
      React.createElement(
        ErrorBoundary,
        {
          showDetails: true,
          children: React.createElement(ThrowError, { shouldThrow: true })
        }
      )
    );

    expect(screen.getByText(/Test error/i)).toBeInTheDocument();
  });

  it('renders retry button', () => {
    render(
      React.createElement(
        ErrorBoundary,
        { children: React.createElement(ThrowError, { shouldThrow: true }) }
      )
    );

    expect(screen.getByRole('button', { name: /Try Again/i })).toBeInTheDocument();
  });

  it('renders home button', () => {
    render(
      React.createElement(
        ErrorBoundary,
        { children: React.createElement(ThrowError, { shouldThrow: true }) }
      )
    );

    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBeGreaterThan(1);
  });

  it('calls onError callback when error occurs', () => {
    const onError = vi.fn();

    render(
      React.createElement(
        ErrorBoundary,
        {
          onError,
          children: React.createElement(ThrowError, { shouldThrow: true })
        }
      )
    );

    expect(onError).toHaveBeenCalled();
  });
});

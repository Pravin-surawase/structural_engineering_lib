import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { TopBar } from '../layout/TopBar';

// Mock react-router-dom
const mockNavigate = vi.fn();
vi.mock('react-router-dom', () => ({
  useLocation: vi.fn(() => ({ pathname: '/design' })),
  useNavigate: vi.fn(() => mockNavigate),
  Link: ({ children, to, ...props }: any) =>
    React.createElement('a', { href: to, ...props }, children),
}));

// Mock framer-motion — render motion.header as plain header
vi.mock('framer-motion', () => ({
  motion: {
    header: React.forwardRef(({ children, ...props }: any, ref: any) =>
      React.createElement('header', { ...props, ref }, children)),
    div: React.forwardRef(({ children, ...props }: any, ref: any) =>
      React.createElement('div', { ...props, ref }, children)),
  },
  AnimatePresence: ({ children }: any) => React.createElement(React.Fragment, null, children),
}));

describe('TopBar', () => {
  it('renders the StructLib brand text', () => {
    render(React.createElement(TopBar));
    expect(screen.getByText('StructLib')).toBeInTheDocument();
  });

  it('renders navigation links', () => {
    render(React.createElement(TopBar));
    expect(screen.getByText('Design')).toBeInTheDocument();
    expect(screen.getByText('Import')).toBeInTheDocument();
    expect(screen.getByText('Batch')).toBeInTheDocument();
    expect(screen.getByText('Editor')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });

  it('renders home link pointing to /', () => {
    render(React.createElement(TopBar));
    const homeLink = screen.getByText('StructLib').closest('a');
    expect(homeLink).toHaveAttribute('href', '/');
  });

  it('returns null on home page', async () => {
    // Override useLocation to return home path
    const routerMock = await import('react-router-dom') as any;
    routerMock.useLocation.mockReturnValueOnce({ pathname: '/' });
    const { container } = render(React.createElement(TopBar));
    expect(container.innerHTML).toBe('');
  });
});

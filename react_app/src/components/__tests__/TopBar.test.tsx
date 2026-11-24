import { afterEach, beforeEach, describe, it, expect, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
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
  const dialogPrototype = HTMLDialogElement.prototype as HTMLDialogElement & {
    showModal: () => void;
    close: () => void;
  };
  const originalShowModal = dialogPrototype.showModal;
  const originalClose = dialogPrototype.close;

  beforeEach(() => {
    dialogPrototype.showModal = function showModal(this: HTMLDialogElement) {
      this.setAttribute('open', '');
    };
    dialogPrototype.close = function close(this: HTMLDialogElement) {
      this.removeAttribute('open');
      this.dispatchEvent(new Event('close'));
    };
  });

  afterEach(() => {
    dialogPrototype.showModal = originalShowModal;
    dialogPrototype.close = originalClose;
  });

  it('renders the StructLib brand text', () => {
    render(React.createElement(TopBar));
    expect(screen.getByText('StructLib')).toBeInTheDocument();
    expect(screen.getByText('By Pravin Surawase')).toBeVisible();
    expect(screen.getByRole('link', { name: /source credits/i })).toHaveAttribute('href', '/CREDITS.txt');
  });

  it('renders navigation links', () => {
    render(React.createElement(TopBar));
    expect(screen.getByText('Workbench')).toBeInTheDocument();
    expect(screen.getByText('Projects')).toBeInTheDocument();
    expect(screen.queryByText('Dashboard')).not.toBeInTheDocument();
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

  it('returns focus to Settings after button and Escape closes', () => {
    render(React.createElement(TopBar));

    const trigger = screen.getByRole('button', { name: 'Settings' });
    fireEvent.click(trigger);
    fireEvent.click(screen.getByRole('button', { name: 'Close settings' }));
    expect(document.activeElement).toBe(trigger);

    fireEvent.click(trigger);
    fireEvent(screen.getByRole('dialog'), new Event('cancel', { cancelable: true }));
    expect(document.activeElement).toBe(trigger);
  });
});

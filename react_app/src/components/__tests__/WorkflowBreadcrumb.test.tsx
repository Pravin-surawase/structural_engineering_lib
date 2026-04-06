import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { WorkflowBreadcrumb } from '../ui/WorkflowBreadcrumb';

// Mock react-router-dom
const mockNavigate = vi.fn();
const mockUseLocation = vi.fn(() => ({ pathname: '/import' }));

vi.mock('react-router-dom', () => ({
  useNavigate: vi.fn(() => mockNavigate),
  useLocation: () => mockUseLocation(),
}));

// Mock framer-motion — render motion.div as plain div
vi.mock('framer-motion', () => ({
  motion: {
    div: React.forwardRef(({ children, ...props }: any, ref: any) =>
      React.createElement('div', { ...props, ref }, children)),
    span: React.forwardRef(({ children, ...props }: any, ref: any) =>
      React.createElement('span', { ...props, ref }, children)),
  },
}));

// Mock lucide-react Check icon
vi.mock('lucide-react', () => ({
  Check: (props: any) => React.createElement('svg', { 'data-testid': 'check-icon', ...props }),
}));

// Mock cn utility
vi.mock('../../lib/utils', () => ({
  cn: (...args: any[]) => args.filter(Boolean).join(' '),
}));

// Mock importedBeamsStore
const mockBeams: any[] = [];
vi.mock('../../store/importedBeamsStore', () => ({
  useImportedBeamsStore: vi.fn(() => ({ beams: mockBeams })),
}));

beforeEach(() => {
  mockNavigate.mockClear();
  mockBeams.length = 0;
});

describe('WorkflowBreadcrumb', () => {
  it('renders all 4 workflow steps', () => {
    render(React.createElement(WorkflowBreadcrumb));
    expect(screen.getByText('Import')).toBeInTheDocument();
    expect(screen.getByText('Editor')).toBeInTheDocument();
    expect(screen.getByText('Batch Design')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });

  it('highlights the current step', () => {
    mockUseLocation.mockReturnValue({ pathname: '/editor' });
    render(React.createElement(WorkflowBreadcrumb));

    // The editor step button should have aria-current="step"
    const buttons = screen.getAllByRole('button');
    const editorButton = buttons[1]; // Index 1 = Editor
    expect(editorButton).toHaveAttribute('aria-current', 'step');
  });

  it('shows checkmark on completed steps', async () => {
    // Set beams so import step is complete, set location to /editor
    mockBeams.push({ id: '1', name: 'B1' });
    mockUseLocation.mockReturnValue({ pathname: '/editor' });

    render(React.createElement(WorkflowBreadcrumb));

    // Import step is complete (beams.length > 0 and we're past it)
    const checkIcons = screen.getAllByTestId('check-icon');
    expect(checkIcons.length).toBeGreaterThan(0);
  });

  it('navigates when a completed step is clicked', () => {
    // beams present, on editor page — import step should be clickable
    mockBeams.push({ id: '1', name: 'B1' });
    mockUseLocation.mockReturnValue({ pathname: '/editor' });

    render(React.createElement(WorkflowBreadcrumb));

    const buttons = screen.getAllByRole('button');
    // Click the Import button (index 0) — it's a completed/past step
    fireEvent.click(buttons[0]);
    expect(mockNavigate).toHaveBeenCalledWith('/import');
  });

  it('does not navigate to future incomplete steps', () => {
    mockUseLocation.mockReturnValue({ pathname: '/import' });

    render(React.createElement(WorkflowBreadcrumb));

    const buttons = screen.getAllByRole('button');
    // Dashboard button (index 3) — future step, should be disabled
    fireEvent.click(buttons[3]);
    expect(mockNavigate).not.toHaveBeenCalled();
  });
});

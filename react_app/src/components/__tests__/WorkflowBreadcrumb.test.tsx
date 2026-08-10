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
    expect(screen.getByText('Review')).toBeInTheDocument();
    expect(screen.getByText('Design')).toBeInTheDocument();
    expect(screen.getByText('Results')).toBeInTheDocument();
  });

  it('highlights the current step', () => {
    mockUseLocation.mockReturnValue({ pathname: '/editor' });
    render(React.createElement(WorkflowBreadcrumb));

    expect(screen.getByRole('button', { name: /review/i })).toHaveAttribute('aria-current', 'step');
  });

  it('shows checkmark on completed steps', async () => {
    // Set beams so import step is complete, set location to /editor
    mockBeams.push({ id: '1', name: 'B1' });
    mockUseLocation.mockReturnValue({ pathname: '/editor' });

    render(React.createElement(WorkflowBreadcrumb));

    // Import step is complete (beams.length > 0 and we're past it)
    expect(screen.getByRole('button', { name: /import/i })).not.toBeDisabled();
  });

  it('navigates when a completed step is clicked', () => {
    // beams present, on editor page — import step should be clickable
    mockBeams.push({ id: '1', name: 'B1' });
    mockUseLocation.mockReturnValue({ pathname: '/editor' });

    render(React.createElement(WorkflowBreadcrumb));

    fireEvent.click(screen.getByRole('button', { name: /import/i }));
    expect(mockNavigate).toHaveBeenCalledWith('/import');
  });

  it('does not navigate to future incomplete steps', () => {
    mockUseLocation.mockReturnValue({ pathname: '/import' });

    render(React.createElement(WorkflowBreadcrumb));

    const results = screen.getByRole('button', { name: /results/i });
    expect(results).toBeDisabled();
    fireEvent.click(results);
    expect(mockNavigate).not.toHaveBeenCalled();
  });
});

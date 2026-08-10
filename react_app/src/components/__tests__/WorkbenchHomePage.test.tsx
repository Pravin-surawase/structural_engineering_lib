import { fireEvent, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { WorkbenchHomePage } from '../pages/WorkbenchHomePage';

const navigate = vi.fn();

vi.mock('react-router-dom', () => ({
  useNavigate: () => navigate,
  useSearchParams: () => [new URLSearchParams()],
}));

describe('WorkbenchHomePage', () => {
  beforeEach(() => navigate.mockClear());

  it('keeps project, beam, and isolated-footing entries reachable', () => {
    render(<WorkbenchHomePage />);

    fireEvent.click(screen.getByRole('button', { name: /open isolated footing/i }));
    expect(navigate).toHaveBeenCalledWith('/workbench/footing/isolated/concentric');

    fireEvent.click(screen.getByRole('button', { name: /open quick beam/i }));
    expect(navigate).toHaveBeenCalledWith('/workbench/quick');

    fireEvent.click(screen.getByRole('button', { name: /^new project/i }));
    expect(navigate).toHaveBeenCalledWith('/workbench/projects/new');
  });
});

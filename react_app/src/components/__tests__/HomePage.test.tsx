import { fireEvent, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { HomePage } from '../pages/HomePage';

const navigate = vi.fn();

vi.mock('react-router-dom', () => ({
  useNavigate: () => navigate,
}));

describe('HomePage', () => {
  beforeEach(() => navigate.mockClear());

  it('offers one primary workbench action and two focused entries', () => {
    render(<HomePage />);

    fireEvent.click(screen.getByRole('button', { name: /open workbench/i }));
    expect(navigate).toHaveBeenCalledWith('/workbench');
    expect(screen.getByRole('button', { name: /quick beam/i })).toBeVisible();
    expect(screen.getByRole('button', { name: /new project/i })).toBeVisible();
  });

  it('shows the creator, source repository, and distributed credits', () => {
    render(<HomePage />);

    expect(screen.getByText('By Pravin Surawase')).toBeVisible();
    expect(screen.getByRole('link', { name: 'Source on GitHub' })).toHaveAttribute(
      'href',
      'https://github.com/Pravin-surawase/structural_engineering_lib',
    );
    expect(screen.getByRole('link', { name: 'Source credits' })).toHaveAttribute('href', '/CREDITS.txt');
    expect(screen.getByRole('link', { name: 'MIT License' })).toBeVisible();
  });
});

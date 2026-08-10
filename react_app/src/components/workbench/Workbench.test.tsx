import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { ResultLifecycleBadge } from './ResultLifecycleBadge';
import { StageNavigation } from './StageNavigation';
import { WorkbenchHeader } from './WorkbenchHeader';
import { WorkbenchShell } from './WorkbenchShell';

describe('workbench primitives', () => {
  it('keeps the narrow inspector and tray in the semantic reading order', () => {
    render(
      <WorkbenchShell
        header={<WorkbenchHeader title="Project review" primaryAction={<button>Run design</button>} />}
        inspector={<p>Selected beam</p>}
        tray={<p>Issue queue</p>}
      >
        <p>Main canvas</p>
      </WorkbenchShell>,
    );

    expect(screen.getByRole('region', { name: 'Workbench content' })).toHaveTextContent('Main canvas');
    expect(screen.getByRole('complementary', { name: 'Selected item inspector' })).toHaveTextContent('Selected beam');
    expect(screen.getByRole('region', { name: 'Workbench results and actions' })).toHaveTextContent('Issue queue');
    expect(screen.getByRole('button', { name: 'Run design' })).toBeVisible();
  });

  it('renders supplied stages without owning their destinations', async () => {
    const user = userEvent.setup();
    const selectReview = vi.fn();
    render(
      <StageNavigation
        stages={[
          { id: 'import', label: 'Import', state: 'complete', onSelect: vi.fn() },
          { id: 'review', label: 'Review', state: 'current', onSelect: selectReview },
          { id: 'design', label: 'Design', state: 'locked', description: 'Complete review first' },
        ]}
      />,
    );

    await user.click(screen.getByRole('button', { name: /review/i }));
    expect(selectReview).toHaveBeenCalledOnce();
    expect(screen.getByRole('button', { name: /design/i })).toBeDisabled();
    expect(screen.getByRole('button', { name: /review/i })).toHaveAttribute('aria-current', 'step');
  });

  it.each([
    ['current', 'Current result'],
    ['stale', 'Stale result'],
    ['pending', 'Result pending'],
    ['error', 'Result error'],
    ['unsupported', 'Unsupported case'],
    ['not_evaluated', 'Not evaluated'],
  ] as const)('renders %s as icon-plus-text lifecycle status', (lifecycle, label) => {
    render(<ResultLifecycleBadge lifecycle={lifecycle} />);
    expect(screen.getByRole('status')).toHaveTextContent(label);
    expect(screen.getByRole('status').querySelector('svg')).not.toBeNull();
  });
});

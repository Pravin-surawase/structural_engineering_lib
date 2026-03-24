import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useAutoDesign } from '../../hooks/useAutoDesign';

// Mock the API client
vi.mock('../../api/client', () => ({
  designBeam: vi.fn(),
}));

// Mock the design store
const mockSetResult = vi.fn();
const mockSetLoading = vi.fn();
const mockSetError = vi.fn();
const mockInputs = { width: 300, depth: 450, moment: 150, fck: 25, fy: 500 };

vi.mock('../../store/designStore', () => ({
  useDesignStore: vi.fn(() => ({
    inputs: mockInputs,
    setResult: mockSetResult,
    setLoading: mockSetLoading,
    setError: mockSetError,
  })),
}));

import { designBeam } from '../../api/client';

describe('useAutoDesign', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('returns runDesign function', () => {
    const { result } = renderHook(() => useAutoDesign(false));
    expect(result.current.runDesign).toBeInstanceOf(Function);
  });

  it('triggers design after debounce when enabled', async () => {
    const mockResponse = {
      success: true,
      message: 'ok',
      flexure: { ast_required: 500, ast_min: 200, ast_max: 3000, xu: 50, xu_max: 200, is_under_reinforced: true, moment_capacity: 180 },
      ast_total: 500,
      asc_total: 0,
      utilization_ratio: 0.83,
    };
    vi.mocked(designBeam).mockResolvedValue(mockResponse);

    renderHook(() => useAutoDesign(true));

    // Before debounce: no call
    expect(designBeam).not.toHaveBeenCalled();

    // Advance past debounce (300ms)
    await act(async () => {
      vi.advanceTimersByTime(350);
    });

    expect(designBeam).toHaveBeenCalledWith(mockInputs);
  });

  it('does not trigger when disabled', () => {
    renderHook(() => useAutoDesign(false));

    vi.advanceTimersByTime(500);
    expect(designBeam).not.toHaveBeenCalled();
  });

  it('sets loading state during design', async () => {
    vi.mocked(designBeam).mockResolvedValue({
      success: true,
      message: 'ok',
      flexure: { ast_required: 500, ast_min: 200, ast_max: 3000, xu: 50, xu_max: 200, is_under_reinforced: true, moment_capacity: 180 },
      ast_total: 500,
      asc_total: 0,
      utilization_ratio: 0.83,
    });

    renderHook(() => useAutoDesign(true));

    await act(async () => {
      vi.advanceTimersByTime(350);
    });

    expect(mockSetLoading).toHaveBeenCalledWith(true);
  });

  it('handles API errors gracefully', async () => {
    vi.mocked(designBeam).mockRejectedValue(new Error('Network error'));

    renderHook(() => useAutoDesign(true));

    // Advance past debounce to trigger the design call
    await act(async () => {
      vi.advanceTimersByTime(350);
    });

    // Allow the rejected promise to settle
    await act(async () => {
      await vi.runAllTimersAsync();
    });

    expect(mockSetError).toHaveBeenCalledWith('Network error');
  });
});

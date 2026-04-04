import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { CrossSectionView } from '../design/CrossSectionView';

describe('CrossSectionView', () => {
  const defaultProps = {
    width: 300,
    depth: 500,
    cover: 25,
    astRequired: 850,
  };

  it('renders SVG element', () => {
    const { container } = render(React.createElement(CrossSectionView, defaultProps));
    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
  });

  it('displays width dimension label', () => {
    render(React.createElement(CrossSectionView, defaultProps));
    expect(screen.getByText('300 mm')).toBeInTheDocument();
  });

  it('displays depth dimension label', () => {
    render(React.createElement(CrossSectionView, defaultProps));
    expect(screen.getByText('500 mm')).toBeInTheDocument();
  });

  it('renders correct number of tension bars', () => {
    // astRequired=850, barDia=16 (default), barArea≈201, ceil(850/201)=5 bars
    const { container } = render(React.createElement(CrossSectionView, defaultProps));
    const bottomBars = container.querySelectorAll('circle[fill="#c87533"]');
    // 5 tension + compression bars (both use copper color when no utilization)
    expect(bottomBars.length).toBeGreaterThanOrEqual(5);
  });

  it('renders bar label text with correct format', () => {
    render(React.createElement(CrossSectionView, { ...defaultProps, barDia: 20, barCount: 3 }));
    expect(screen.getByText('3-T20')).toBeInTheDocument();
  });

  it('shows utilization badge when provided', () => {
    render(React.createElement(CrossSectionView, { ...defaultProps, utilization: 0.87 }));
    expect(screen.getByText('87%')).toBeInTheDocument();
  });

  it('uses emerald color for low utilization', () => {
    const { container } = render(
      React.createElement(CrossSectionView, { ...defaultProps, utilization: 0.7, barCount: 3 })
    );
    // Emerald fill #10b981 for bars with utilization ≤ 0.85
    const emeraldBars = container.querySelectorAll('circle[fill="#10b981"]');
    expect(emeraldBars.length).toBeGreaterThan(0);
  });
});

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { BeamForm } from '../design/BeamForm';

// Mock dependencies
const mockSetInputs = vi.fn();
const mockSetLength = vi.fn();
const mockSetAutoDesign = vi.fn();

vi.mock('../../store/designStore', () => ({
  useDesignStore: vi.fn(() => ({
    inputs: { width: 300, depth: 450, moment: 150, shear: 80, fck: 25, fy: 500 },
    length: 4000,
    setInputs: mockSetInputs,
    setLength: mockSetLength,
    setResult: vi.fn(),
    setLoading: vi.fn(),
    setError: vi.fn(),
    isLoading: false,
    autoDesign: false,
    setAutoDesign: mockSetAutoDesign,
    wsLatency: null,
  })),
}));

vi.mock('../../hooks/useAutoDesign', () => ({
  useAutoDesign: vi.fn(),
}));

vi.mock('../../api/client', () => ({
  designBeam: vi.fn(),
}));

vi.mock('@tanstack/react-query', () => ({
  useMutation: vi.fn(() => ({
    mutate: vi.fn(),
    isPending: false,
  })),
}));

describe('BeamForm', () => {
  it('renders form heading', () => {
    render(React.createElement(BeamForm));
    expect(screen.getByText('Beam Design')).toBeInTheDocument();
  });

  it('renders geometry input labels', () => {
    render(React.createElement(BeamForm));
    expect(screen.getByText('Width (mm)')).toBeInTheDocument();
    expect(screen.getByText('Depth (mm)')).toBeInTheDocument();
    expect(screen.getByText('Length (mm)')).toBeInTheDocument();
  });

  it('renders loading and material labels', () => {
    render(React.createElement(BeamForm));
    expect(screen.getByText(/Moment/)).toBeInTheDocument();
    expect(screen.getByText(/Shear/)).toBeInTheDocument();
    expect(screen.getByText(/Concrete fck/)).toBeInTheDocument();
    expect(screen.getByText(/Steel fy/)).toBeInTheDocument();
  });

  it('shows Design Beam button when auto-design is off', () => {
    render(React.createElement(BeamForm));
    expect(screen.getByText('Design Beam')).toBeInTheDocument();
  });

  it('renders Live Preview toggle', () => {
    render(React.createElement(BeamForm));
    expect(screen.getByText('Live Preview')).toBeInTheDocument();
  });
});

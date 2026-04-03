import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { ExportPanel } from '../design/ExportPanel';

// Mock export hooks
const mockBBSMutate = vi.fn();
const mockDXFMutate = vi.fn();
const mockReportMutate = vi.fn();

vi.mock('../../hooks/useExport', () => ({
  useExportBBS: vi.fn(() => ({ mutate: mockBBSMutate, isPending: false, error: null })),
  useExportDXF: vi.fn(() => ({ mutate: mockDXFMutate, isPending: false, error: null })),
  useExportReport: vi.fn(() => ({ mutate: mockReportMutate, isPending: false, error: null })),
}));

describe('ExportPanel', () => {
  const defaultParams = {
    width: 300,
    depth: 500,
    fck: 25,
    fy: 500,
    ast_required: 850,
    moment: 150,
    shear: 75,
  };

  it('renders export heading', () => {
    render(React.createElement(ExportPanel, { beamParams: defaultParams }));
    expect(screen.getByText('Export')).toBeInTheDocument();
  });

  it('renders BBS button', () => {
    render(React.createElement(ExportPanel, { beamParams: defaultParams }));
    expect(screen.getByText('BBS')).toBeInTheDocument();
  });

  it('renders DXF button', () => {
    render(React.createElement(ExportPanel, { beamParams: defaultParams }));
    expect(screen.getByText('DXF')).toBeInTheDocument();
  });

  it('renders Report button', () => {
    render(React.createElement(ExportPanel, { beamParams: defaultParams }));
    expect(screen.getByText('Report')).toBeInTheDocument();
  });

  it('all three export buttons are enabled by default', () => {
    render(React.createElement(ExportPanel, { beamParams: defaultParams }));
    const buttons = screen.getAllByRole('button');
    buttons.forEach((btn) => {
      expect(btn).not.toBeDisabled();
    });
  });
});

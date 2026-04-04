import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { ImportView } from '../import/ImportView';

// Mock react-router-dom
vi.mock('react-router-dom', () => ({
  useNavigate: vi.fn(() => vi.fn()),
  useSearchParams: vi.fn(() => [new URLSearchParams(), vi.fn()]),
}));

// Mock stores
vi.mock('../../store/importedBeamsStore', () => ({
  useImportedBeamsStore: vi.fn(() => ({
    beams: [],
    isImporting: false,
    error: null,
    setBeams: vi.fn(),
    setError: vi.fn(),
    setImporting: vi.fn(),
  })),
}));

// Mock hooks
vi.mock('../../hooks/useCSVImport', () => ({
  useDualCSVImport: vi.fn(() => ({
    importFiles: vi.fn(),
    isImporting: false,
    error: null,
    data: null,
  })),
}));

// Mock API client
vi.mock('../../api/client', () => ({
  loadSampleData: vi.fn(),
}));

// Mock utilities
vi.mock('../../utils/sampleData', () => ({
  mapSampleBeamsToRows: vi.fn(() => []),
}));

vi.mock('../../utils/materialOverrides', () => ({
  applyMaterialOverrides: vi.fn((beams) => beams),
}));

// Mock FileDropZone
vi.mock('../ui/FileDropZone', () => ({
  FileDropZone: () => React.createElement('div', { 'data-testid': 'file-drop-zone' }, 'FileDropZone'),
}));

describe('ImportView', () => {
  it('renders the import heading', () => {
    render(React.createElement(ImportView));
    expect(screen.getByText('Import Beam Data')).toBeInTheDocument();
  });

  it('renders step indicators', () => {
    render(React.createElement(ImportView));
    expect(screen.getByText('1. Upload')).toBeInTheDocument();
    expect(screen.getByText('2. Preview & Design')).toBeInTheDocument();
    expect(screen.getByText('3. Building Editor')).toBeInTheDocument();
  });

  it('renders import mode tabs', () => {
    render(React.createElement(ImportView));
    expect(screen.getByText('Single CSV')).toBeInTheDocument();
    expect(screen.getByText('Dual CSV (Geometry + Forces)')).toBeInTheDocument();
  });

  it('renders material settings panel', () => {
    render(React.createElement(ImportView));
    expect(screen.getByText('Material Settings')).toBeInTheDocument();
    expect(screen.getByText('IS 456:2000', { exact: false })).toBeInTheDocument();
  });

  it('renders sample data button', () => {
    render(React.createElement(ImportView));
    expect(screen.getByText('Sample Building')).toBeInTheDocument();
  });
});

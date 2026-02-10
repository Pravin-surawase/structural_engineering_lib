/**
 * BeamTable Component
 *
 * Professional data table for beam list using AG Grid.
 * Features: sorting, filtering, selection, status indicators.
 */
import { useMemo, useCallback } from 'react';
import { AgGridReact } from '@ag-grid-community/react';
import { ClientSideRowModelModule } from '@ag-grid-community/client-side-row-model';
import { ModuleRegistry } from '@ag-grid-community/core';
import type { ColDef, SelectionChangedEvent, RowClassParams, RowClickedEvent } from '@ag-grid-community/core';
import '@ag-grid-community/styles/ag-grid.css';
import '@ag-grid-community/styles/ag-theme-alpine.css';

// Register AG Grid modules
ModuleRegistry.registerModules([ClientSideRowModelModule]);

export interface BeamRowData {
  id: string;
  story: string;
  width_mm: number;
  depth_mm: number;
  span_mm: number;
  mu_knm: number;
  vu_kn: number;
  fck_mpa: number;
  fy_mpa: number;
  ast_required?: number;
  ast_provided?: number;
  utilization?: number;
  status?: 'pending' | 'designing' | 'pass' | 'fail' | 'warning';
}

interface BeamTableProps {
  beams: BeamRowData[];
  onSelectionChange?: (selectedIds: string[]) => void;
  onBeamClick?: (beamId: string) => void;
  selectedBeamId?: string | null;
  isLoading?: boolean;
}

// Status cell renderer with colors
const StatusRenderer = (props: { value: string }) => {
  const status = props.value || 'pending';
  const colors: Record<string, { bg: string; text: string }> = {
    pending: { bg: 'bg-zinc-700/50', text: 'text-zinc-400' },
    designing: { bg: 'bg-blue-500/20', text: 'text-blue-400' },
    pass: { bg: 'bg-emerald-500/20', text: 'text-emerald-400' },
    fail: { bg: 'bg-red-500/20', text: 'text-red-400' },
    warning: { bg: 'bg-amber-500/20', text: 'text-amber-400' },
  };
  const { bg, text } = colors[status] || colors.pending;

  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${bg} ${text}`}>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
};

// Utilization bar renderer
const UtilizationRenderer = (props: { value: number }) => {
  const value = props.value ?? 0;
  const pct = Math.min(100, Math.max(0, value * 100));
  const color = value > 1 ? 'bg-red-500' : value > 0.9 ? 'bg-amber-500' : 'bg-emerald-500';

  return (
    <div className="flex items-center gap-2 w-full">
      <div className="flex-1 h-2 bg-zinc-700 rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full transition-all`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs text-zinc-400 w-12 text-right">{(value * 100).toFixed(0)}%</span>
    </div>
  );
};

export function BeamTable({
  beams,
  onSelectionChange,
  onBeamClick,
  selectedBeamId,
  isLoading = false,
}: BeamTableProps) {
  // Column definitions
  const columnDefs = useMemo<ColDef<BeamRowData>[]>(() => [
    {
      headerName: 'ID',
      field: 'id',
      width: 120,
      pinned: 'left',
      checkboxSelection: true,
      headerCheckboxSelection: true,
    },
    { headerName: 'Story', field: 'story', width: 100 },
    { headerName: 'Width (mm)', field: 'width_mm', width: 100, type: 'numericColumn' },
    { headerName: 'Depth (mm)', field: 'depth_mm', width: 100, type: 'numericColumn' },
    { headerName: 'Span (mm)', field: 'span_mm', width: 100, type: 'numericColumn' },
    { headerName: 'Mu (kN·m)', field: 'mu_knm', width: 100, type: 'numericColumn', valueFormatter: p => p.value?.toFixed(1) },
    { headerName: 'Vu (kN)', field: 'vu_kn', width: 100, type: 'numericColumn', valueFormatter: p => p.value?.toFixed(1) },
    { headerName: 'fck (MPa)', field: 'fck_mpa', width: 90, type: 'numericColumn' },
    { headerName: 'fy (MPa)', field: 'fy_mpa', width: 90, type: 'numericColumn' },
    {
      headerName: 'Ast Req (mm²)',
      field: 'ast_required',
      width: 120,
      type: 'numericColumn',
      valueFormatter: p => p.value?.toFixed(0) || '-',
    },
    {
      headerName: 'Utilization',
      field: 'utilization',
      width: 150,
      cellRenderer: UtilizationRenderer,
    },
    {
      headerName: 'Status',
      field: 'status',
      width: 100,
      cellRenderer: StatusRenderer,
    },
  ], []);

  // Default column settings
  const defaultColDef = useMemo<ColDef>(() => ({
    sortable: true,
    filter: true,
    resizable: true,
    suppressMovable: false,
  }), []);

  // Handle selection changes
  const handleSelectionChanged = useCallback(
    (event: SelectionChangedEvent<BeamRowData>) => {
      const selectedRows = event.api.getSelectedRows();
      const ids = selectedRows.map((row) => row.id);
      onSelectionChange?.(ids);
    },
    [onSelectionChange]
  );

  // Handle row click
  const handleRowClicked = useCallback(
    (event: RowClickedEvent<BeamRowData>) => {
      if (event.data) {
        onBeamClick?.(event.data.id);
      }
    },
    [onBeamClick]
  );

  // Row class for selected state
  const getRowClass = useCallback(
    (params: RowClassParams<BeamRowData>) => {
      if (params.data?.id === selectedBeamId) {
        return 'ag-row-selected-highlight';
      }
      return '';
    },
    [selectedBeamId]
  );

  if (isLoading) {
    return (
      <div className="w-full h-96 bg-zinc-900/50 rounded-lg animate-pulse flex items-center justify-center">
        <span className="text-zinc-500">Loading beams...</span>
      </div>
    );
  }

  return (
    <div
      className="ag-theme-alpine-dark w-full h-96 rounded-lg overflow-hidden"
      style={{
        '--ag-background-color': 'rgb(24 24 27)',
        '--ag-header-background-color': 'rgb(39 39 42)',
        '--ag-odd-row-background-color': 'rgb(24 24 27)',
        '--ag-row-hover-color': 'rgb(63 63 70 / 0.5)',
        '--ag-selected-row-background-color': 'rgb(59 130 246 / 0.2)',
        '--ag-border-color': 'rgb(63 63 70)',
        '--ag-font-family': 'inherit',
        '--ag-font-size': '13px',
      } as React.CSSProperties}
    >
      <AgGridReact<BeamRowData>
        rowData={beams}
        columnDefs={columnDefs}
        defaultColDef={defaultColDef}
        rowSelection="multiple"
        suppressRowClickSelection={false}
        onSelectionChanged={handleSelectionChanged}
        onRowClicked={handleRowClicked}
        getRowClass={getRowClass}
        animateRows={true}
        pagination={true}
        paginationPageSize={20}
        suppressCellFocus={true}
        domLayout="normal"
      />
    </div>
  );
}

export default BeamTable;

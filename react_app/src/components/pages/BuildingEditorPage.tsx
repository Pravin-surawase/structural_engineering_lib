/**
 * BuildingEditorPage - The flagship feature.
 *
 * Top 30%: 3D building view with floor isolation + camera fly-to
 * Bottom 70%: Full-screen AG Grid editor with editable cells
 * Right sidebar (toggleable): Design checks, suggestions, detailing
 *
 * Material strip above grid shows global fck/fy/cover settings.
 * Columns show envelope forces (Mu, Vu) not split start/mid/end.
 */
import { Suspense, useMemo, useCallback, useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { AgGridReact } from "@ag-grid-community/react";
import { ClientSideRowModelModule } from "@ag-grid-community/client-side-row-model";
import { ModuleRegistry } from "@ag-grid-community/core";
import type {
  CellValueChangedEvent,
  ColDef,
  RowClickedEvent,
  RowSelectionOptions,
} from "@ag-grid-community/core";
import "@ag-grid-community/styles/ag-grid.css";
import "@ag-grid-community/styles/ag-theme-alpine.css";
import {
  ArrowLeft,
  Download,
  RefreshCw,
  PanelRightOpen,
  PanelRightClose,
  Layers,
  ChevronDown,
  FileText,
  FileSpreadsheet,
  File,
} from "lucide-react";
import { useImportedBeamsStore } from "../../store/importedBeamsStore";
import { Viewport3D } from "../viewport/Viewport3D";
import { BeamDetailPanel } from "../design/BeamDetailPanel";
import { useBatchDesign } from "../../hooks/useBatchDesign";
import { useExportBuildingSummary } from "../../hooks/useExport";
import type { BeamCSVRow } from "../../types/csv";
import { deriveBeamStatus } from "../../utils/beamStatus";
import { WorkflowHint } from "../ui/WorkflowHint";
import { WorkflowBreadcrumb } from "../ui/WorkflowBreadcrumb";
import { useWorkspaceStore } from "../../workspace/workspaceStore";
import { projectExportReadiness } from "../../workspace/resultRecords";

ModuleRegistry.registerModules([ClientSideRowModelModule]);

const EDITOR_ROW_SELECTION: RowSelectionOptions<BeamCSVRow> = {
  mode: "singleRow",
  enableClickSelection: true,
  checkboxes: false,
};

/* ---- Helpers ---- */

/** Compute envelope moment from start/mid/end */
function getEnvelopeMu(beam: BeamCSVRow): number {
  return Math.max(
    Math.abs(beam.Mu_start ?? 0),
    Math.abs(beam.Mu_mid ?? 0),
    Math.abs(beam.Mu_end ?? 0),
    Math.abs(beam.mu_envelope ?? 0)
  );
}

/** Compute envelope shear from start/end */
function getEnvelopeVu(beam: BeamCSVRow): number {
  return Math.max(
    Math.abs(beam.Vu_start ?? 0),
    Math.abs(beam.Vu_end ?? 0),
    Math.abs(beam.vu_envelope ?? 0)
  );
}

/* ---- Main Component ---- */

export function BuildingEditorPage() {
  const navigate = useNavigate();
  const {
    beams,
    selectedId,
    selectBeam,
    selectFloor,
    setBeams,
    restoreFromWorkspace,
  } = useImportedBeamsStore();
  const workspaceSnapshot = useWorkspaceStore((state) => state.snapshot);
  const workspaceProjectId = workspaceSnapshot?.projectId;
  const workspaceLoadState = useWorkspaceStore((state) => state.loadState);
  const workspaceLoadError = useWorkspaceStore((state) => state.loadError);
  const [sidebarClosedForId, setSidebarClosedForId] = useState<string | null>(null);
  const [floorFilter, setFloorFilter] = useState<string>("all");
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showExportMenu, setShowExportMenu] = useState(false);
  const gridRef = useRef<AgGridReact>(null);
  const { startBatchDesign, status: batchStatus } = useBatchDesign();
  const isDesigning = batchStatus === "running";
  const { mutate: exportBuilding, isPending: exportPending } = useExportBuildingSummary();

  useEffect(() => {
    if (beams.length === 0 && workspaceSnapshot?.members.length) {
      restoreFromWorkspace(workspaceSnapshot);
    }
  }, [beams.length, restoreFromWorkspace, workspaceSnapshot]);

  useEffect(() => {
    if (workspaceProjectId) {
      useWorkspaceStore.getState().setStage("review");
    }
  }, [workspaceProjectId]);

  // Global material settings
  const [globalFck, setGlobalFck] = useState(25);
  const [globalFy, setGlobalFy] = useState(500);
  const [globalCover, setGlobalCover] = useState(40);

  const stories = useMemo(
    () => [...new Set(beams.map((b) => b.story).filter(Boolean))].sort(),
    [beams]
  );

  const filteredBeams = useMemo(() => {
    if (floorFilter === "all") return beams;
    return beams.filter((b) => b.story === floorFilter);
  }, [beams, floorFilter]);

  const selectedBeam = useMemo(
    () => beams.find((b) => b.id === selectedId),
    [beams, selectedId]
  );
  const showSidebar = selectedId !== null && sidebarClosedForId !== selectedId;

  const statusCounts = useMemo(() => {
    const counts = { pass: 0, fail: 0, warning: 0, pending: 0, designing: 0 };
    beams.forEach((beam) => { counts[deriveBeamStatus(beam)] += 1; });
    return counts;
  }, [beams]);

  const completedCount = statusCounts.pass + statusCounts.fail + statusCounts.warning;
  const progressPct = beams.length > 0 ? (completedCount / beams.length) * 100 : 0;
  const exportReadiness = useMemo(
    () => projectExportReadiness(workspaceSnapshot),
    [workspaceSnapshot],
  );
  const heldBeamCount = exportReadiness.heldMemberIds.length;
  const exportsHeld = !exportReadiness.eligible;

  const handleRowClicked = useCallback(
    (event: RowClickedEvent<BeamCSVRow>) => {
      if (event.data) selectBeam(event.data.id);
    },
    [selectBeam]
  );

  const handleFloorChange = useCallback(
    (value: string) => {
      setFloorFilter(value);
      selectFloor(value === "all" ? null : value);
    },
    [selectFloor]
  );

  const handleGlobalMaterialChange = useCallback(
    (field: "fck" | "fy" | "cover", value: number) => {
      if (field === "fck") setGlobalFck(value);
      else if (field === "fy") setGlobalFy(value);
      else setGlobalCover(value);
      const updated = beams.map((b) => ({
        ...b,
        [field]: value,
        status: "pending" as const,
        is_valid: false,
      }));
      setBeams(updated);
    },
    [beams, setBeams]
  );

  const handleDesignAll = useCallback(() => {
    if (beams.length === 0) return;
    startBatchDesign(beams);
  }, [beams, startBatchDesign]);

  const handleBuildingExport = useCallback(
    (format: "html" | "pdf" | "csv") => {
      if (!projectExportReadiness(useWorkspaceStore.getState().snapshot).eligible) return;
      setShowExportMenu(false);
      const payload = beams.map((b) => ({
        beam_id: b.id,
        story: b.story ?? "",
        width: b.b,
        depth: b.D,
        span_length: b.span ?? 0,
        fck: b.fck ?? globalFck,
        fy: b.fy ?? globalFy,
        moment: getEnvelopeMu(b),
        shear: getEnvelopeVu(b),
        ast_required: b.ast_required ?? 0,
        ast_provided: b.ast_provided ?? 0,
        asc_required: b.asc_required ?? 0,
        bar_count: b.bar_count,
        bar_diameter: b.bar_diameter,
        stirrup_diameter: b.stirrup_diameter ?? 8,
        stirrup_spacing: b.stirrup_spacing,
        utilization: b.utilization ?? 0,
        is_safe: b.is_valid ?? false,
        status: deriveBeamStatus(b),
      }));
      exportBuilding({ project_name: "Building Project", beams: payload, format });
    },
    [beams, globalFck, globalFy, exportBuilding]
  );

  const handleCellValueChanged = useCallback(
    (event: CellValueChangedEvent<BeamCSVRow>) => {
      if (event.data) {
        // Get fresh state inside callback to avoid stale closure issues
        const currentBeams = useImportedBeamsStore.getState().beams;
        const updatedBeams = currentBeams.map((b) =>
          b.id === event.data!.id
            ? { ...b, ...event.data, status: "pending" as const, is_valid: false }
            : b
        );
        useImportedBeamsStore.getState().setBeams(updatedBeams);
      }
    },
    [] // No dependencies - we get fresh state inside
  );

  // Column definitions — envelope-based default, advanced for detail
  const columnDefs = useMemo<ColDef<BeamCSVRow>[]>(
    () => [
      { headerName: "ID", field: "id", width: 120, pinned: "left", cellClass: "font-mono text-white/80" },
      { headerName: "Story", field: "story", width: 80 },
      { headerName: "b (mm)", field: "b", width: 80, editable: true, type: "numericColumn", cellClass: "bg-blue-500/5 text-right font-mono",
        valueFormatter: (p) => p.value != null ? Number(p.value).toLocaleString() : "-" },
      { headerName: "D (mm)", field: "D", width: 80, editable: true, type: "numericColumn", cellClass: "bg-blue-500/5 text-right font-mono",
        valueFormatter: (p) => p.value != null ? Number(p.value).toLocaleString() : "-" },
      { headerName: "Span (mm)", field: "span", width: 95, type: "numericColumn", cellClass: "text-right font-mono",
        valueFormatter: (p) => p.value != null ? Number(p.value).toLocaleString() : "-" },
      {
        headerName: "Mu (kN\u00b7m)",
        width: 100,
        editable: true,
        type: "numericColumn",
        cellClass: "bg-blue-500/5 text-right font-mono",
        valueGetter: (p) => p.data ? getEnvelopeMu(p.data) : 0,
        valueSetter: (p) => {
          if (p.data) {
            p.data.mu_envelope = Number(p.newValue);
            p.data.Mu_mid = Number(p.newValue);
          }
          return true;
        },
        valueFormatter: (p) => p.value ? Number(p.value).toFixed(1) : "-",
      },
      {
        headerName: "Vu (kN)",
        width: 90,
        editable: true,
        type: "numericColumn",
        cellClass: "bg-blue-500/5 text-right font-mono",
        valueGetter: (p) => p.data ? getEnvelopeVu(p.data) : 0,
        valueSetter: (p) => {
          if (p.data) {
            p.data.vu_envelope = Number(p.newValue);
            p.data.Vu_start = Number(p.newValue);
          }
          return true;
        },
        valueFormatter: (p) => p.value ? Number(p.value).toFixed(1) : "-",
      },
      {
        headerName: "Ast Req (mm\u00b2)",
        field: "ast_required",
        width: 100,
        type: "numericColumn",
        valueFormatter: (p) => p.value != null ? Number(p.value).toFixed(0) : "-",
        cellClass: "text-white/50 text-right font-mono",
      },
      {
        headerName: "Bars",
        width: 90,
        valueGetter: (p) => {
          if (!p.data?.bar_count || !p.data?.bar_diameter) return null;
          return `${p.data.bar_count}-T${p.data.bar_diameter}`;
        },
        cellClass: "text-white/70 font-mono",
      },
      {
        headerName: "Stirrup",
        width: 100,
        valueGetter: (p) => {
          if (!p.data?.stirrup_spacing) return null;
          const dia = p.data.stirrup_diameter ?? 8;
          return `${dia}\u00d8@${p.data.stirrup_spacing}`;
        },
        cellClass: "text-white/70 font-mono",
      },
      // Advanced columns
      { headerName: "Mu_start", field: "Mu_start", width: 90, type: "numericColumn",
        valueFormatter: (p) => p.value != null ? Number(p.value).toFixed(1) : "-", hide: !showAdvanced, cellClass: "text-right font-mono" },
      { headerName: "Mu_mid", field: "Mu_mid", width: 90, type: "numericColumn",
        valueFormatter: (p) => p.value != null ? Number(p.value).toFixed(1) : "-", hide: !showAdvanced, cellClass: "text-right font-mono" },
      { headerName: "Mu_end", field: "Mu_end", width: 90, type: "numericColumn",
        valueFormatter: (p) => p.value != null ? Number(p.value).toFixed(1) : "-", hide: !showAdvanced, cellClass: "text-right font-mono" },
      { headerName: "Vu_start", field: "Vu_start", width: 90, type: "numericColumn",
        valueFormatter: (p) => p.value != null ? Number(p.value).toFixed(1) : "-", hide: !showAdvanced, cellClass: "text-right font-mono" },
      { headerName: "Vu_end", field: "Vu_end", width: 90, type: "numericColumn",
        valueFormatter: (p) => p.value != null ? Number(p.value).toFixed(1) : "-", hide: !showAdvanced, cellClass: "text-right font-mono" },
      { headerName: "Ast Prov", field: "ast_provided", width: 90, type: "numericColumn",
        valueFormatter: (p) => p.value != null ? Number(p.value).toFixed(0) : "-", hide: !showAdvanced, cellClass: "text-right font-mono" },
      { headerName: "Asc Req", field: "asc_required", width: 90, type: "numericColumn",
        valueFormatter: (p) => p.value != null ? Number(p.value).toFixed(0) : "-", hide: !showAdvanced, cellClass: "text-right font-mono" },
      { headerName: "Bar #", field: "bar_count", width: 65, editable: true, type: "numericColumn",
        cellClass: "bg-blue-500/5 text-right font-mono", hide: !showAdvanced },
      { headerName: "Bar \u00d8", field: "bar_diameter", width: 75, editable: true, type: "numericColumn",
        cellClass: "bg-blue-500/5 text-right font-mono",
        valueFormatter: (p) => p.value ? `${p.value} mm` : "-", hide: !showAdvanced },
      { headerName: "Str \u00d8", field: "stirrup_diameter", width: 70, editable: true, type: "numericColumn",
        cellClass: "bg-blue-500/5 text-right font-mono",
        valueFormatter: (p) => p.value ? `${p.value}` : "8", hide: !showAdvanced },
      { headerName: "Str Sp", field: "stirrup_spacing", width: 80, editable: true, type: "numericColumn",
        cellClass: "bg-blue-500/5 text-right font-mono",
        valueFormatter: (p) => p.value ? `${p.value}` : "-", hide: !showAdvanced },
      {
        headerName: "Util.",
        headerTooltip: "Governing IS 456 compliance utilization",
        field: "utilization",
        width: 95,
        cellRenderer: UtilizationRenderer,
      },
      {
        headerName: "Status",
        field: "status",
        valueGetter: (params) => (params.data ? deriveBeamStatus(params.data) : "pending"),
        width: 85,
        cellRenderer: StatusRenderer,
      },
    ],
    [showAdvanced]
  );

  const defaultColDef = useMemo<ColDef>(
    () => ({ sortable: true, filter: true, resizable: true, suppressMovable: false }),
    []
  );

  if (beams.length === 0) {
    if (workspaceLoadState === "loading") {
      return (
        <div className="flex h-screen items-center justify-center bg-zinc-950 pt-14" role="status">
          <RefreshCw className="mr-2 h-4 w-4 animate-spin text-blue-300" />
          <p className="text-zinc-300">Restoring the last project…</p>
        </div>
      );
    }
    return (
      <div className="h-screen pt-14 flex items-center justify-center bg-zinc-950">
        <div className="text-center">
          <p className="text-zinc-400 mb-4">No beams loaded</p>
          {workspaceLoadState === "error" && workspaceLoadError ? (
            <p className="mb-4 max-w-md text-sm text-rose-300" role="alert">
              {workspaceLoadError}
            </p>
          ) : null}
          <button onClick={() => navigate("/import")}
            className="px-6 py-2.5 bg-blue-600 text-white rounded-xl text-sm font-medium">
            Import Beams
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen pt-14 flex flex-col bg-zinc-950">
      {/* Workflow Breadcrumb */}
      <WorkflowBreadcrumb />

      {/* Toolbar */}
      <div className="flex min-h-11 shrink-0 flex-wrap items-center justify-between gap-2 border-b border-white/5 px-4 py-2">
        <div className="flex min-w-0 flex-wrap items-center gap-3">
          <button onClick={() => navigate("/import")} className="p-1.5 rounded-lg hover:bg-white/5 text-white/50 hover:text-white/80 transition-colors">
            <ArrowLeft className="w-4 h-4" />
          </button>
          <span className="text-sm font-medium text-white">Building Editor</span>
          <span className="text-xs text-zinc-400">
            {beams.length} beams &middot; {stories.length} stories
          </span>
          {isDesigning && <span className="text-xs text-blue-300 animate-pulse">Designing…</span>}
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5 text-zinc-400" />
            <select value={floorFilter} onChange={(e) => handleFloorChange(e.target.value)}
              className="px-2 py-1 text-xs text-white bg-white/5 border border-white/10 rounded-lg appearance-none cursor-pointer">
              <option value="all" className="bg-zinc-900">All Floors</option>
              {stories.map((s) => <option key={s} value={s} className="bg-zinc-900">{s}</option>)}
            </select>
          </div>

          <button onClick={handleDesignAll} disabled={isDesigning}
            className="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium transition-colors flex items-center gap-1.5 disabled:opacity-40">
            <RefreshCw className={`w-3.5 h-3.5 ${isDesigning ? "animate-spin" : ""}`} />
            Design All
          </button>
          <button onClick={() => setShowAdvanced((prev) => !prev)}
            className={`px-2 py-1 rounded-lg text-[10px] uppercase tracking-wide border transition-colors ${
              showAdvanced ? "bg-blue-500/20 text-blue-300 border-blue-500/40" : "bg-white/5 text-zinc-400 border-white/10 hover:text-zinc-200"
            }`}>
            {showAdvanced ? "Advanced" : "Simple"}
          </button>
          <div className="relative">
            <button
              onClick={() => !exportsHeld && setShowExportMenu(!showExportMenu)}
              disabled={exportPending || exportsHeld}
              className="p-1.5 rounded-lg hover:bg-white/5 text-zinc-400 hover:text-zinc-200 transition-colors disabled:opacity-40 flex items-center gap-1"
              title={exportsHeld ? `Exports held: ${heldBeamCount} beams are FAIL or not designed` : "Export building summary"}
            >
              <Download className={`w-4 h-4 ${exportPending ? "animate-pulse" : ""}`} />
              <ChevronDown className="w-3 h-3" />
            </button>
            {exportsHeld && (
              <span className="sr-only" role="status">
                Exports held: {heldBeamCount} beams are FAIL or HOLD.
              </span>
            )}
            {showExportMenu && (
              <div className="absolute right-0 top-full mt-1 w-52 bg-zinc-900 border border-white/10 rounded-xl shadow-2xl z-50 py-1 overflow-hidden">
                <button onClick={() => handleBuildingExport("html")}
                  className="w-full flex items-center gap-2.5 px-3 py-2 text-xs text-white/70 hover:bg-white/5 hover:text-white transition-colors">
                  <FileText className="w-3.5 h-3.5 text-blue-400" /> HTML Summary Report
                </button>
                <button onClick={() => handleBuildingExport("pdf")}
                  className="w-full flex items-center gap-2.5 px-3 py-2 text-xs text-white/70 hover:bg-white/5 hover:text-white transition-colors">
                  <File className="w-3.5 h-3.5 text-red-400" /> PDF Summary Report
                </button>
                <button onClick={() => handleBuildingExport("csv")}
                  className="w-full flex items-center gap-2.5 px-3 py-2 text-xs text-white/70 hover:bg-white/5 hover:text-white transition-colors">
                  <FileSpreadsheet className="w-3.5 h-3.5 text-green-400" /> CSV Data Export
                </button>
              </div>
            )}
          </div>
          <button onClick={() => setSidebarClosedForId(showSidebar ? selectedId : null)}
            className={`p-1.5 rounded-lg transition-colors ${showSidebar ? "bg-blue-500/20 text-blue-400" : "hover:bg-white/5 text-zinc-400 hover:text-zinc-200"}`}
            title="Toggle checks panel">
            {showSidebar ? <PanelRightClose className="w-4 h-4" /> : <PanelRightOpen className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Workflow hint */}
      <div className="px-4 pt-3 pb-2">
        <WorkflowHint
          stepNumber={selectedId ? 3 : 1}
          totalSteps={3}
          title={selectedId ? "View Beam Details" : "Select & Design Beams"}
          description={
            selectedId
              ? "Click a beam in the table to view details. Use 'Design All' to batch-design all beams, or click individual rows."
              : "Select global materials (M-grade, Fe-grade) above. Click 'Design All' to run batch design on all beams."
          }
          nextAction={selectedId ? "Export → BBS/DXF/Report" : "Click 'Design All'"}
          storageKey="workflow_hint_building_editor"
        />
      </div>

      {/* Material strip + progress */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-white/5 bg-zinc-950/80 px-4 py-2">
        <div className="flex flex-wrap items-center gap-3">
          <MaterialSelect label="Concrete" value={globalFck} onChange={(v) => handleGlobalMaterialChange("fck", v)}
            options={[20, 25, 30, 35, 40, 45, 50]} format={(v) => `M${v}`} />
          <MaterialSelect label="Steel" value={globalFy} onChange={(v) => handleGlobalMaterialChange("fy", v)}
            options={[415, 500, 550]} format={(v) => `Fe${v}`} />
          <MaterialSelect label="Cover" value={globalCover} onChange={(v) => handleGlobalMaterialChange("cover", v)}
            options={[25, 30, 35, 40, 45, 50]} format={(v) => `${v}mm`} />
          <span className="text-[10px] text-zinc-500 ml-1">IS 456:2000</span>
        </div>

        <div className="flex items-center gap-3">
          <div className="w-32 h-1.5 bg-white/10 rounded-full overflow-hidden">
            <div className="h-full bg-blue-500/60 rounded-full transition-all" style={{ width: `${progressPct}%` }} />
          </div>
          <div className="flex gap-1.5 text-[10px] uppercase tracking-wide">
            {statusCounts.pass > 0 && <span className="px-1.5 py-0.5 rounded-full bg-green-500/20 text-green-300">{statusCounts.pass}</span>}
            {statusCounts.warning > 0 && <span className="px-1.5 py-0.5 rounded-full bg-amber-500/20 text-amber-300">{statusCounts.warning}</span>}
            {statusCounts.fail > 0 && <span className="px-1.5 py-0.5 rounded-full bg-red-500/20 text-red-300">{statusCounts.fail}</span>}
            {statusCounts.pending > 0 && <span className="px-1.5 py-0.5 rounded-full bg-white/10 text-zinc-400">{statusCounts.pending}</span>}
            {statusCounts.designing > 0 && <span className="px-1.5 py-0.5 rounded-full bg-blue-500/20 text-blue-300 animate-pulse">{statusCounts.designing}</span>}
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex min-h-0 flex-1 flex-col overflow-y-auto lg:flex-row lg:overflow-hidden">
        <div className="flex min-h-[40rem] min-w-0 flex-1 flex-col lg:min-h-0">
          {/* 3D Building View (top 30%) */}
          <div className="relative h-72 min-h-[200px] border-b border-white/5 lg:h-[30%]">
            <Suspense fallback={<div className="flex items-center justify-center h-full bg-zinc-900"><p className="text-zinc-400 animate-pulse">Loading 3D...</p></div>}>
              <Viewport3D mode="building" forceMode />
            </Suspense>

            {selectedBeam && (
              <div className="absolute top-3 left-3 px-3 py-1.5 rounded-lg bg-black/60 backdrop-blur text-xs text-white/70">
                {selectedBeam.story || "Unknown"} &middot; {selectedBeam.id}
              </div>
            )}

            {selectedBeam &&
              (selectedBeam.stirrup_spacing == null || selectedBeam.bar_diameter == null || selectedBeam.bar_count == null) &&
              (selectedBeam.ast_required != null || selectedBeam.ast_provided != null) && (
                <div className="absolute top-3 right-3 px-3 py-1.5 rounded-lg bg-amber-500/20 border border-amber-500/40 text-[10px] text-amber-200">
                  Detail Preview (estimated)
                </div>
              )}
          </div>

          {/* AG Grid Editor (bottom 70%) */}
          <div className="min-h-[26rem] flex-1 ag-theme-alpine-dark" style={{
            "--ag-background-color": "rgb(9 9 11)",
            "--ag-header-background-color": "rgb(24 24 27)",
            "--ag-odd-row-background-color": "rgb(9 9 11)",
            "--ag-row-hover-color": "rgb(63 63 70 / 0.3)",
            "--ag-selected-row-background-color": "rgb(59 130 246 / 0.15)",
            "--ag-border-color": "rgb(39 39 42)",
            "--ag-font-family": "inherit",
            "--ag-font-size": "12px",
            "--ag-row-height": "36px",
            "--ag-header-height": "38px",
          } as React.CSSProperties}>
            <AgGridReact<BeamCSVRow>
              ref={gridRef}
              rowData={filteredBeams}
              columnDefs={columnDefs}
              defaultColDef={defaultColDef}
              rowSelection={EDITOR_ROW_SELECTION}
              onRowClicked={handleRowClicked}
              onCellValueChanged={handleCellValueChanged}
              animateRows
              suppressCellFocus={false}
              domLayout="normal"
              getRowId={(params) => params.data.id}
              rowClassRules={{ "!bg-blue-500/10": (params) => params.data?.id === selectedId }}
            />
          </div>
        </div>

        {/* Beam Detail Panel — slides in when a beam is selected */}
        {showSidebar && selectedBeam && (
          <div className="w-full shrink-0 overflow-y-auto border-t border-white/5 bg-zinc-950 lg:w-[420px] lg:border-t-0 lg:border-l">
            <BeamDetailPanel
              beam={selectedBeam}
              onClose={() => { selectBeam(null); setSidebarClosedForId(null); }}
            />
          </div>
        )}
      </div>
    </div>
  );
}

/* ---- Material Select ---- */

function MaterialSelect({ label, value, onChange, options, format }: {
  label: string; value: number; onChange: (v: number) => void;
  options: number[]; format: (v: number) => string;
}) {
  return (
    <div className="flex items-center gap-1.5">
      <span className="text-[10px] text-zinc-400">{label}</span>
      <div className="relative">
        <select value={value} onChange={(e) => onChange(Number(e.target.value))}
          className="px-2 py-0.5 pr-5 text-xs text-white bg-white/[0.04] border border-white/10 rounded-md appearance-none cursor-pointer focus:outline-none focus:ring-1 focus:ring-blue-500/50">
          {options.map((opt) => <option key={opt} value={opt} className="bg-zinc-900">{format(opt)}</option>)}
        </select>
        <ChevronDown className="absolute right-1 top-1/2 -translate-y-1/2 w-3 h-3 text-zinc-500 pointer-events-none" />
      </div>
    </div>
  );
}


/* ---- Cell Renderers ---- */

function StatusRenderer(props: { value: string }) {
  const status = props.value || "pending";
  const styles: Record<string, string> = {
    pending: "bg-zinc-700/50 text-zinc-400",
    designing: "bg-blue-500/20 text-blue-400",
    pass: "bg-emerald-500/20 text-emerald-400",
    fail: "bg-red-500/20 text-red-400",
    warning: "bg-amber-500/20 text-amber-400",
  };
  return (
    <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${styles[status] || styles.pending}`}>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
}

function UtilizationRenderer(props: { value: number }) {
  const value = props.value ?? 0;
  const pct = Math.min(100, Math.max(0, value * 100));
  const color = value > 1 ? "bg-red-500" : value > 0.9 ? "bg-amber-500" : "bg-emerald-500";
  return (
    <div className="flex items-center gap-2 w-full">
      <div className="flex-1 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-[10px] text-zinc-400 w-8 text-right">{value ? `${(value * 100).toFixed(0)}%` : "-"}</span>
    </div>
  );
}

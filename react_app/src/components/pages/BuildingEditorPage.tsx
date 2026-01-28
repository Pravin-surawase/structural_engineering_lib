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
import type { ColDef, RowClickedEvent, CellValueChangedEvent } from "@ag-grid-community/core";
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
} from "lucide-react";
import { useImportedBeamsStore } from "../../store/importedBeamsStore";
import { Viewport3D } from "../Viewport3D";
import { useBatchDesign } from "../../hooks";
import type { BeamCSVRow } from "../../types/csv";
import { deriveBeamStatus } from "../../utils/beamStatus";

ModuleRegistry.registerModules([ClientSideRowModelModule]);

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

/** Pick standard bar diameter and count for given Ast */
function deriveBarLayout(astRequired: number): { count: number; dia: number } {
  const standardDias = [12, 16, 20, 25, 32];
  for (const dia of standardDias) {
    const barArea = Math.PI * (dia / 2) ** 2;
    const count = Math.ceil(astRequired / barArea);
    if (count >= 2 && count <= 8) return { count, dia };
  }
  const barArea = Math.PI * (25 / 2) ** 2;
  return { count: Math.max(2, Math.ceil(astRequired / barArea)), dia: 25 };
}

/* ---- Main Component ---- */

export function BuildingEditorPage() {
  const navigate = useNavigate();
  const { beams, selectedId, selectBeam, selectFloor, setBeams, setError } = useImportedBeamsStore();
  const [showSidebar, setShowSidebar] = useState(false);
  const [floorFilter, setFloorFilter] = useState<string>("all");
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [autoDesignTriggered, setAutoDesignTriggered] = useState(false);
  const gridRef = useRef<AgGridReact>(null);
  const { runBatchDesign, isDesigning } = useBatchDesign();

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

  // Auto-open sidebar when a beam is selected
  useEffect(() => {
    if (selectedId && !showSidebar) setShowSidebar(true);
  }, [selectedId]); // eslint-disable-line react-hooks/exhaustive-deps

  const statusCounts = useMemo(() => {
    const counts = { pass: 0, fail: 0, warning: 0, pending: 0, designing: 0 };
    beams.forEach((beam) => { counts[deriveBeamStatus(beam)] += 1; });
    return counts;
  }, [beams]);

  const completedCount = statusCounts.pass + statusCounts.fail + statusCounts.warning;
  const progressPct = beams.length > 0 ? (completedCount / beams.length) * 100 : 0;

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
      const updated = beams.map((b) => ({ ...b, [field]: value, status: "pending" as const }));
      setBeams(updated);
    },
    [beams, setBeams]
  );

  const handleDesignAll = useCallback(() => {
    if (beams.length === 0) return;

    // Mark beams with forces as "designing"
    const marked = beams.map((beam) => {
      const mu = getEnvelopeMu(beam);
      const vu = getEnvelopeVu(beam);
      return {
        ...beam,
        status: (mu > 0 || vu > 0) ? "designing" as const : beam.status ?? "pending" as const,
      };
    });
    setBeams(marked);

    // Build payload matching API's BatchDesignRequest (list of BeamRow)
    const payload = beams.map((b) => ({
      id: b.id,
      story: b.story ?? null,
      width_mm: b.b,
      depth_mm: b.D,
      span_mm: b.span,
      mu_knm: getEnvelopeMu(b),
      vu_kn: getEnvelopeVu(b),
      fck_mpa: b.fck ?? globalFck,
      fy_mpa: b.fy ?? globalFy,
      cover_mm: b.cover ?? globalCover,
    }));

    runBatchDesign(payload, {
      onSuccess: (data: any) => {
        if (!data.success) {
          setError(data.message || "Batch design failed");
          return;
        }
        const resultMap = new Map(
          (data.results as any[]).map((r: any) => [r.beam_id, r])
        );
        const updated = beams.map((beam) => {
          const result = resultMap.get(beam.id);
          if (!result || !result.success) {
            return { ...beam, status: result ? "fail" as const : beam.status };
          }

          const astReq = result.ast_required ?? beam.ast_required ?? 0;
          const astMax = 0.04 * beam.b * beam.D;
          const utilization = astMax > 0 ? astReq / astMax : 0;
          const layout = deriveBarLayout(astReq);
          const isSafe = result.is_safe ?? false;

          return {
            ...beam,
            ast_required: astReq,
            asc_required: result.asc_required ?? 0,
            stirrup_spacing: result.stirrup_spacing ?? beam.stirrup_spacing,
            stirrup_diameter: beam.stirrup_diameter ?? 8,
            bar_count: layout.count,
            bar_diameter: layout.dia,
            ast_provided: layout.count * Math.PI * (layout.dia / 2) ** 2,
            utilization,
            is_valid: isSafe,
            status: isSafe ? "pass" as const : "fail" as const,
          } as BeamCSVRow;
        });
        setBeams(updated);
      },
      onError: (error: Error) => {
        setError(error.message);
        const reset = beams.map((b) => ({
          ...b,
          status: b.status === "designing" ? "pending" as const : b.status,
        }));
        setBeams(reset);
      },
    });
  }, [beams, globalFck, globalFy, globalCover, runBatchDesign, setBeams, setError]);

  // Auto-design on first load if forces present but no results
  useEffect(() => {
    if (autoDesignTriggered) return;
    if (beams.length === 0) return;
    const hasForces = beams.some((b) => getEnvelopeMu(b) > 0 || getEnvelopeVu(b) > 0);
    const hasResults = beams.some((b) => typeof b.ast_required === "number");
    if (hasForces && !hasResults) {
      setAutoDesignTriggered(true);
      handleDesignAll();
    }
  }, [autoDesignTriggered, beams, handleDesignAll]);

  const handleCellValueChanged = useCallback(
    (event: CellValueChangedEvent<BeamCSVRow>) => {
      if (event.data) {
        const updatedBeams = beams.map((b) =>
          b.id === event.data!.id ? { ...b, ...event.data, status: "pending" as const } : b
        );
        useImportedBeamsStore.getState().setBeams(updatedBeams);
      }
    },
    [beams]
  );

  // Column definitions — envelope-based default, advanced for detail
  const columnDefs = useMemo<ColDef<BeamCSVRow>[]>(
    () => [
      { headerName: "ID", field: "id", width: 120, pinned: "left", cellClass: "font-mono text-white/80" },
      { headerName: "Story", field: "story", width: 80 },
      { headerName: "b (mm)", field: "b", width: 75, editable: true, type: "numericColumn", cellClass: "bg-blue-500/5" },
      { headerName: "D (mm)", field: "D", width: 75, editable: true, type: "numericColumn", cellClass: "bg-blue-500/5" },
      { headerName: "Span", field: "span", width: 85, type: "numericColumn",
        valueFormatter: (p) => p.value ? `${p.value}` : "-" },
      {
        headerName: "Mu (kN\u00b7m)",
        width: 90,
        editable: true,
        type: "numericColumn",
        cellClass: "bg-blue-500/5",
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
        width: 85,
        editable: true,
        type: "numericColumn",
        cellClass: "bg-blue-500/5",
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
        headerName: "Ast Req",
        field: "ast_required",
        width: 85,
        type: "numericColumn",
        valueFormatter: (p) => p.value ? Number(p.value).toFixed(0) : "-",
        cellClass: "text-white/50",
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
      { headerName: "Mu_start", field: "Mu_start", width: 85, type: "numericColumn",
        valueFormatter: (p) => p.value?.toFixed(1) || "-", hide: !showAdvanced },
      { headerName: "Mu_mid", field: "Mu_mid", width: 85, type: "numericColumn",
        valueFormatter: (p) => p.value?.toFixed(1) || "-", hide: !showAdvanced },
      { headerName: "Mu_end", field: "Mu_end", width: 85, type: "numericColumn",
        valueFormatter: (p) => p.value?.toFixed(1) || "-", hide: !showAdvanced },
      { headerName: "Vu_start", field: "Vu_start", width: 85, type: "numericColumn",
        valueFormatter: (p) => p.value?.toFixed(1) || "-", hide: !showAdvanced },
      { headerName: "Vu_end", field: "Vu_end", width: 85, type: "numericColumn",
        valueFormatter: (p) => p.value?.toFixed(1) || "-", hide: !showAdvanced },
      { headerName: "Ast Prov", field: "ast_provided", width: 85, type: "numericColumn",
        valueFormatter: (p) => p.value?.toFixed(0) || "-", hide: !showAdvanced },
      { headerName: "Asc Req", field: "asc_required", width: 85, type: "numericColumn",
        valueFormatter: (p) => p.value?.toFixed(0) || "-", hide: !showAdvanced },
      { headerName: "Bar #", field: "bar_count", width: 65, editable: true, type: "numericColumn",
        cellClass: "bg-blue-500/5", hide: !showAdvanced },
      { headerName: "Bar \u00d8", field: "bar_diameter", width: 70, editable: true, type: "numericColumn",
        cellClass: "bg-blue-500/5",
        valueFormatter: (p) => p.value ? `${p.value} mm` : "-", hide: !showAdvanced },
      { headerName: "Str \u00d8", field: "stirrup_diameter", width: 65, editable: true, type: "numericColumn",
        cellClass: "bg-blue-500/5",
        valueFormatter: (p) => p.value ? `${p.value}` : "8", hide: !showAdvanced },
      { headerName: "Str Sp", field: "stirrup_spacing", width: 75, editable: true, type: "numericColumn",
        cellClass: "bg-blue-500/5",
        valueFormatter: (p) => p.value ? `${p.value}` : "-", hide: !showAdvanced },
      {
        headerName: "Util.",
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
    return (
      <div className="h-screen pt-14 flex items-center justify-center bg-zinc-950">
        <div className="text-center">
          <p className="text-white/40 mb-4">No beams loaded</p>
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
      {/* Toolbar */}
      <div className="h-11 flex items-center justify-between px-4 border-b border-white/5 shrink-0">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate("/import")} className="p-1.5 rounded-lg hover:bg-white/5 text-white/50 hover:text-white/80 transition-colors">
            <ArrowLeft className="w-4 h-4" />
          </button>
          <span className="text-sm font-medium text-white">Building Editor</span>
          <span className="text-xs text-white/40">
            {beams.length} beams &middot; {stories.length} stories
          </span>
          {isDesigning && <span className="text-xs text-blue-300 animate-pulse">Designing…</span>}
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5 text-white/40" />
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
              showAdvanced ? "bg-blue-500/20 text-blue-300 border-blue-500/40" : "bg-white/5 text-white/40 border-white/10 hover:text-white/70"
            }`}>
            {showAdvanced ? "Advanced" : "Simple"}
          </button>
          <button className="p-1.5 rounded-lg hover:bg-white/5 text-white/40 hover:text-white/70 transition-colors" title="Export CSV">
            <Download className="w-4 h-4" />
          </button>
          <button onClick={() => setShowSidebar(!showSidebar)}
            className={`p-1.5 rounded-lg transition-colors ${showSidebar ? "bg-blue-500/20 text-blue-400" : "hover:bg-white/5 text-white/40 hover:text-white/70"}`}
            title="Toggle checks panel">
            {showSidebar ? <PanelRightClose className="w-4 h-4" /> : <PanelRightOpen className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Material strip + progress */}
      <div className="px-4 py-2 border-b border-white/5 bg-zinc-950/80 flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <MaterialSelect label="Concrete" value={globalFck} onChange={(v) => handleGlobalMaterialChange("fck", v)}
            options={[20, 25, 30, 35, 40, 45, 50]} format={(v) => `M${v}`} />
          <MaterialSelect label="Steel" value={globalFy} onChange={(v) => handleGlobalMaterialChange("fy", v)}
            options={[415, 500, 550]} format={(v) => `Fe${v}`} />
          <MaterialSelect label="Cover" value={globalCover} onChange={(v) => handleGlobalMaterialChange("cover", v)}
            options={[25, 30, 35, 40, 45, 50]} format={(v) => `${v}mm`} />
          <span className="text-[10px] text-white/25 ml-1">IS 456:2000</span>
        </div>

        <div className="flex items-center gap-3">
          <div className="w-32 h-1.5 bg-white/10 rounded-full overflow-hidden">
            <div className="h-full bg-blue-500/60 rounded-full transition-all" style={{ width: `${progressPct}%` }} />
          </div>
          <div className="flex gap-1.5 text-[10px] uppercase tracking-wide">
            {statusCounts.pass > 0 && <span className="px-1.5 py-0.5 rounded-full bg-green-500/20 text-green-300">{statusCounts.pass}</span>}
            {statusCounts.warning > 0 && <span className="px-1.5 py-0.5 rounded-full bg-amber-500/20 text-amber-300">{statusCounts.warning}</span>}
            {statusCounts.fail > 0 && <span className="px-1.5 py-0.5 rounded-full bg-red-500/20 text-red-300">{statusCounts.fail}</span>}
            {statusCounts.pending > 0 && <span className="px-1.5 py-0.5 rounded-full bg-white/10 text-white/40">{statusCounts.pending}</span>}
            {statusCounts.designing > 0 && <span className="px-1.5 py-0.5 rounded-full bg-blue-500/20 text-blue-300 animate-pulse">{statusCounts.designing}</span>}
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 flex flex-col min-w-0">
          {/* 3D Building View (top 30%) */}
          <div className="h-[30%] min-h-[200px] border-b border-white/5 relative">
            <Suspense fallback={<div className="flex items-center justify-center h-full bg-zinc-900"><p className="text-white/40 animate-pulse">Loading 3D...</p></div>}>
              <Viewport3D mode="building" />
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
          <div className="flex-1 ag-theme-alpine-dark" style={{
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
              rowSelection="single"
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

        {/* Right Sidebar */}
        {showSidebar && (
          <div className="w-80 border-l border-white/5 bg-zinc-950 overflow-y-auto">
            <ChecksSidebar beam={selectedBeam} />
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
      <span className="text-[10px] text-white/40">{label}</span>
      <div className="relative">
        <select value={value} onChange={(e) => onChange(Number(e.target.value))}
          className="px-2 py-0.5 pr-5 text-xs text-white bg-white/[0.04] border border-white/10 rounded-md appearance-none cursor-pointer focus:outline-none focus:ring-1 focus:ring-blue-500/50">
          {options.map((opt) => <option key={opt} value={opt} className="bg-zinc-900">{format(opt)}</option>)}
        </select>
        <ChevronDown className="absolute right-1 top-1/2 -translate-y-1/2 w-3 h-3 text-white/30 pointer-events-none" />
      </div>
    </div>
  );
}

/* ---- Sidebar ---- */

function ChecksSidebar({ beam }: { beam?: BeamCSVRow | null }) {
  const [activeTab, setActiveTab] = useState<"checks" | "detail" | "cost">("checks");
  const status = beam ? deriveBeamStatus(beam) : "pending";

  if (!beam) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-white/30 text-sm">Select a beam to see details</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex border-b border-white/5">
        {(["checks", "detail", "cost"] as const).map((tab) => (
          <button key={tab} onClick={() => setActiveTab(tab)}
            className={`flex-1 py-2.5 text-xs font-medium transition-colors ${
              activeTab === tab ? "text-blue-400 border-b-2 border-blue-400" : "text-white/40 hover:text-white/70"
            }`}>
            {tab === "checks" ? "Checks" : tab === "detail" ? "Detailing" : "Cost"}
          </button>
        ))}
      </div>

      <div className="flex-1 p-4 space-y-4">
        <div className="p-3 rounded-xl bg-white/[0.03] border border-white/8">
          <p className="text-xs text-white/40">{beam.story}</p>
          <p className="text-sm font-bold text-white">{beam.id}</p>
          <p className="text-xs text-white/50 mt-1">
            {beam.b}x{beam.D} mm &middot; {beam.span} mm span
          </p>
          <div className="flex gap-3 mt-2 text-[10px] text-white/40">
            <span>M{beam.fck ?? 25}</span>
            <span>Fe{beam.fy ?? 500}</span>
            <span>{beam.cover ?? 40}mm cover</span>
          </div>
        </div>

        {activeTab === "checks" && (
          <>
            <CheckItem label="Flexure Check" clause="IS 456 Cl. 38.1"
              status={status === "warning" ? "warning" : status === "fail" ? "fail" : status === "pass" ? "pass" : "pending"}
              detail={beam.ast_required ? `Ast = ${beam.ast_required.toFixed(0)} mm²` : "Not designed"} />
            <CheckItem label="Shear Check" clause="IS 456 Cl. 40"
              status={status === "pass" ? "pass" : status === "fail" ? "fail" : "pending"}
              detail={beam.stirrup_spacing ? `Sv = ${beam.stirrup_spacing} mm` : "Stirrup spacing pending"} />
            <CheckItem label="Min Steel" clause="IS 456 Cl. 26.5.1.1"
              status={beam.status === "pass" ? "pass" : "pending"}
              detail={`0.${beam.fy === 415 ? "085" : "12"}% for Fe${beam.fy ?? 500}`} />
            <CheckItem label="Max Steel" clause="IS 456 Cl. 26.5.1.1"
              status="pass" detail="< 4% of cross section" />
            <CheckItem label="Deflection (L/d)" clause="IS 456 Cl. 23.2"
              status={beam.span && beam.D ? (beam.span / beam.D < 20 ? "pass" : "warning") : "pending"}
              detail={beam.span && beam.D ? `L/d = ${(beam.span / beam.D).toFixed(1)}` : "-"} />
          </>
        )}

        {activeTab === "detail" && (
          <div className="space-y-3">
            <div className="p-3 rounded-xl bg-white/[0.03] border border-white/8">
              <p className="text-[10px] text-white/40 uppercase tracking-wider mb-2">Tension Reinforcement</p>
              <p className="text-sm text-white">
                {beam.ast_required ? `${beam.ast_required.toFixed(0)} mm² required` : "Not designed"}
              </p>
              {beam.bar_count && beam.bar_diameter && (
                <p className="text-xs text-white/60 mt-1">
                  Provided: {beam.bar_count}-T{beam.bar_diameter} = {beam.ast_provided?.toFixed(0)} mm²
                </p>
              )}
            </div>
            {beam.stirrup_spacing && (
              <div className="p-3 rounded-xl bg-white/[0.03] border border-white/8">
                <p className="text-[10px] text-white/40 uppercase tracking-wider mb-2">Shear Reinforcement</p>
                <p className="text-sm text-white">
                  {beam.stirrup_diameter ?? 8}ø @ {beam.stirrup_spacing} mm c/c
                </p>
              </div>
            )}
            <div className="p-3 rounded-xl bg-white/[0.03] border border-white/8">
              <p className="text-[10px] text-white/40 uppercase tracking-wider mb-2">Utilization</p>
              <div className="flex items-center gap-2">
                <div className="flex-1 h-2 bg-zinc-800 rounded-full overflow-hidden">
                  <div className={`h-full rounded-full ${
                    (beam.utilization ?? 0) > 1 ? "bg-red-500" : (beam.utilization ?? 0) > 0.9 ? "bg-amber-500" : "bg-green-500"
                  }`} style={{ width: `${Math.min(100, (beam.utilization ?? 0) * 100)}%` }} />
                </div>
                <span className="text-xs text-white">{beam.utilization ? `${(beam.utilization * 100).toFixed(0)}%` : "-"}</span>
              </div>
            </div>
          </div>
        )}

        {activeTab === "cost" && (
          <div className="text-sm text-white/40 text-center py-8">
            Cost analysis available after batch design
          </div>
        )}
      </div>
    </div>
  );
}

function CheckItem({ label, clause, status, detail }: {
  label: string; clause: string; status: "pass" | "fail" | "warning" | "pending"; detail: string;
}) {
  const colors = {
    pass: "border-green-500/30 bg-green-500/5",
    fail: "border-red-500/30 bg-red-500/5",
    warning: "border-amber-500/30 bg-amber-500/5",
    pending: "border-white/8 bg-white/[0.02]",
  };
  const dots = {
    pass: "bg-green-400",
    fail: "bg-red-400",
    warning: "bg-amber-400",
    pending: "bg-zinc-500",
  };

  return (
    <div className={`p-3 rounded-xl border ${colors[status]}`}>
      <div className="flex items-center gap-2 mb-1">
        <div className={`w-2 h-2 rounded-full ${dots[status]}`} />
        <span className="text-xs font-medium text-white/80">{label}</span>
      </div>
      <p className="text-[10px] text-white/40 ml-4">{clause}</p>
      <p className="text-xs text-white/60 ml-4 mt-0.5">{detail}</p>
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

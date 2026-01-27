import { Suspense, useState } from "react";
import {
  Box,
  FileUp,
  Settings,
  Layers,
  Home,
} from "lucide-react";
import { FloatingDock } from "../ui/FloatingDock";
import { Viewport3D } from "../Viewport3D";
import { LandingView } from "../LandingView";
import { ImportView } from "../ImportView";
import { DesignView } from "../DesignView";
import { BeamTable, type BeamRowData } from "../BeamTable";
import { useImportedBeamsStore } from "../../store/importedBeamsStore";
import { loadSampleData } from "../../api/client";
import { mapSampleBeamsToRows } from "../../utils/sampleData";

type ViewMode = "home" | "design" | "import" | "results" | "settings";

/**
 * ModernAppLayout - Gen Z-style layout with floating dock navigation.
 *
 * View modes:
 * - home: Landing page with CTAs (Try Sample, Import, Manual)
 * - design: Single beam design form
 * - import: CSV/Excel import with drag-drop
 * - results: 3D visualization with beam list
 * - settings: Configuration (TODO)
 */
export function ModernAppLayout() {
  const [viewMode, setViewMode] = useState<ViewMode>("home");
  const [isLoadingSample, setIsLoadingSample] = useState(false);
  const { beams, setBeams, setError } = useImportedBeamsStore();

  const handleLoadSample = async () => {
    setIsLoadingSample(true);
    try {
      const data = await loadSampleData();
      if (data.success) {
        const storeBeams = mapSampleBeamsToRows(data.beams);
        setBeams(storeBeams as any);
        setViewMode("results");
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load sample data");
    } finally {
      setIsLoadingSample(false);
    }
  };

  const dockItems = [
    {
      id: "home",
      icon: <Home className="w-full h-full" />,
      label: "Home",
      active: viewMode === "home",
      onClick: () => setViewMode("home"),
    },
    {
      id: "design",
      icon: <Box className="w-full h-full" />,
      label: "Beam Design",
      active: viewMode === "design",
      onClick: () => setViewMode("design"),
    },
    {
      id: "import",
      icon: <FileUp className="w-full h-full" />,
      label: "Import Data",
      active: viewMode === "import",
      onClick: () => setViewMode("import"),
    },
    {
      id: "results",
      icon: <Layers className="w-full h-full" />,
      label: "Results",
      badge: beams.length > 0 ? beams.length : undefined,
      active: viewMode === "results",
      onClick: () => setViewMode("results"),
    },
    {
      id: "settings",
      icon: <Settings className="w-full h-full" />,
      label: "Settings",
      active: viewMode === "settings",
      onClick: () => setViewMode("settings"),
    },
  ];

  return (
    <div className="relative h-screen w-screen bg-zinc-950 overflow-hidden">
      {/* Main Content Area */}
      <div className="h-full pb-24">
        {viewMode === "home" && (
          <LandingView
            onLoadSample={handleLoadSample}
            onImportCSV={() => setViewMode("import")}
            onManualDesign={() => setViewMode("design")}
            isLoading={isLoadingSample}
          />
        )}

        {viewMode === "design" && (
          <DesignView onBack={() => setViewMode("home")} />
        )}

        {viewMode === "import" && (
          <ImportView
            onBack={() => setViewMode("home")}
            onImportComplete={() => setViewMode("results")}
          />
        )}

        {viewMode === "results" && (
          <ResultsView onBack={() => setViewMode("home")} />
        )}

        {viewMode === "settings" && (
          <SettingsView onBack={() => setViewMode("home")} />
        )}
      </div>

      {/* Floating Navigation */}
      <FloatingDock items={dockItems} />
    </div>
  );
}

/**
 * Results view with 3D visualization and beam list.
 */
interface ResultsViewProps {
  onBack: () => void;
}

function ResultsView({ onBack }: ResultsViewProps) {
  const { beams, selectedId, selectBeam } = useImportedBeamsStore();
  const beamCount = beams.length;

  const rows = beams.map<BeamRowData>((beam) => ({
    id: beam.id,
    story: beam.story ?? "",
    width_mm: beam.b,
    depth_mm: beam.D,
    span_mm: beam.span,
    mu_knm: beam.Mu_mid ?? beam.Mu_start ?? beam.Mu_end ?? 0,
    vu_kn: beam.Vu_start ?? beam.Vu_end ?? 0,
    fck_mpa: beam.fck ?? 25,
    fy_mpa: beam.fy ?? 500,
    ast_required: beam.ast_required,
    ast_provided: beam.ast_provided,
    utilization: beam.utilization,
    status: beam.status ?? "pending",
  }));

  return (
    <div className="flex flex-col h-full p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-2xl font-bold text-white">3D Model View</h2>
          <p className="text-white/50">{beamCount} beams loaded</p>
        </div>
        <button
          onClick={onBack}
          className="px-4 py-2 text-sm text-white/60 hover:text-white transition-colors"
        >
          ← Back
        </button>
      </div>

      <div className="grid grid-cols-12 gap-6 flex-1 min-h-0">
        {/* 3D Viewport */}
        <div className="col-span-7 rounded-2xl overflow-hidden border border-white/10 min-h-[400px]">
          <Suspense
            fallback={
              <div className="flex items-center justify-center h-full bg-zinc-900">
                <div className="animate-pulse text-white/50">
                  Loading 3D viewport...
                </div>
              </div>
            }
          >
            <Viewport3D mode="building" />
          </Suspense>
        </div>

        {/* Beam Table */}
        <div className="col-span-5 flex flex-col gap-3 min-h-0">
          <div className="flex items-center justify-between">
            <p className="text-sm text-white/60">Beam List</p>
            {selectedId && (
              <button
                onClick={() => selectBeam(null)}
                className="text-xs text-white/60 hover:text-white"
              >
                Clear Selection
              </button>
            )}
          </div>
          <BeamTable
            beams={rows}
            onSelectionChange={(ids) => selectBeam(ids[0] ?? null)}
            onBeamClick={(beamId) => selectBeam(beamId)}
            selectedBeamId={selectedId}
          />
          <p className="text-xs text-white/40">
            Click a row to focus the 3D view on that beam.
          </p>
        </div>
      </div>
    </div>
  );
}

/**
 * Settings placeholder view.
 */
interface SettingsViewProps {
  onBack: () => void;
}

function SettingsView({ onBack }: SettingsViewProps) {
  return (
    <div className="flex flex-col h-full p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-2xl font-bold text-white">Settings</h2>
          <p className="text-white/50">Configure application preferences</p>
        </div>
        <button
          onClick={onBack}
          className="px-4 py-2 text-sm text-white/60 hover:text-white transition-colors"
        >
          ← Back
        </button>
      </div>

      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <Settings className="w-16 h-16 text-white/20 mx-auto mb-4" />
          <p className="text-white/40">Settings panel coming soon</p>
          <p className="text-sm text-white/30 mt-2">
            API configuration, units, export preferences
          </p>
        </div>
      </div>
    </div>
  );
}

export default ModernAppLayout;

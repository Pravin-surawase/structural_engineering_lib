import { Suspense, useState } from "react";
import {
  Box,
  FileUp,
  Play,
  Settings,
  Layers,
  Database,
} from "lucide-react";
import { BentoGrid, BentoCard, BentoCardHeader } from "../ui/BentoGrid";
import { FloatingDock } from "../ui/FloatingDock";
import { Viewport3D } from "../Viewport3D";
import { useImportedBeamsStore } from "../../store/importedBeamsStore";

type ViewMode = "design" | "import" | "results" | "settings";

/**
 * ModernAppLayout - Gen Z-style bento grid layout with floating dock.
 *
 * Replaces the traditional sidebar layout with:
 * - BentoGrid for content organization
 * - FloatingDock for navigation
 * - Glassmorphism visual effects
 */
export function ModernAppLayout() {
  const [viewMode, setViewMode] = useState<ViewMode>("design");
  const { beams, selectedId } = useImportedBeamsStore();

  const dockItems = [
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
      {/* Main Content Grid */}
      <BentoGrid className="h-full pb-24">
        {/* 3D Viewport - Takes 8 columns */}
        <BentoCard colSpan={8} rowSpan={3} variant="solid" className="p-0">
          <Suspense
            fallback={
              <div className="flex items-center justify-center h-full">
                <div className="animate-pulse text-white/50">
                  Loading 3D viewport...
                </div>
              </div>
            }
          >
            <Viewport3D />
          </Suspense>
        </BentoCard>

        {/* Input Panel - 4 columns */}
        <BentoCard colSpan={4} rowSpan={2} variant="glass">
          <BentoCardHeader
            title="Section Input"
            subtitle="Define beam geometry"
            icon={<Box className="w-4 h-4" />}
            badge="IS 456"
          />
          <DesignInputPanel />
        </BentoCard>

        {/* Quick Stats - 4 columns */}
        <BentoCard colSpan={4} rowSpan={1} variant="elevated" glow>
          <BentoCardHeader
            title="Quick Results"
            icon={<Database className="w-4 h-4" />}
          />
          <QuickStatsPanel />
        </BentoCard>

        {/* Status Bar - Full width at bottom */}
        <BentoCard colSpan={12} rowSpan={1} variant="default">
          <div className="flex items-center justify-between h-full">
            <div className="flex items-center gap-4">
              <span className="text-xs text-white/50">
                {beams.length} beams loaded
              </span>
              {selectedId && (
                <span className="text-xs text-blue-400">
                  Selected: {selectedId}
                </span>
              )}
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              <span className="text-xs text-white/50">Ready</span>
            </div>
          </div>
        </BentoCard>
      </BentoGrid>

      {/* Floating Navigation */}
      <FloatingDock items={dockItems} />
    </div>
  );
}

/**
 * Design input panel for beam parameters.
 */
function DesignInputPanel() {
  const [width, setWidth] = useState(300);
  const [depth, setDepth] = useState(450);
  const [span, setSpan] = useState(4000);
  const [moment, setMoment] = useState(100);

  return (
    <div className="space-y-4">
      <InputField
        label="Width (b)"
        value={width}
        onChange={setWidth}
        unit="mm"
        min={150}
        max={1000}
      />
      <InputField
        label="Depth (D)"
        value={depth}
        onChange={setDepth}
        unit="mm"
        min={200}
        max={1500}
      />
      <InputField
        label="Span (L)"
        value={span}
        onChange={setSpan}
        unit="mm"
        min={1000}
        max={12000}
      />
      <InputField
        label="Moment (Mu)"
        value={moment}
        onChange={setMoment}
        unit="kN·m"
        min={0}
        max={2000}
      />

      <button className="w-full py-2.5 mt-4 text-sm font-medium text-white bg-blue-600 hover:bg-blue-500 rounded-xl transition-colors flex items-center justify-center gap-2">
        <Play className="w-4 h-4" />
        Run Design
      </button>
    </div>
  );
}

interface InputFieldProps {
  label: string;
  value: number;
  onChange: (value: number) => void;
  unit: string;
  min?: number;
  max?: number;
}

function InputField({ label, value, onChange, unit, min, max }: InputFieldProps) {
  return (
    <div className="flex items-center justify-between gap-4">
      <label className="text-xs text-white/60 whitespace-nowrap">{label}</label>
      <div className="flex items-center gap-2 flex-1 justify-end">
        <input
          type="number"
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          min={min}
          max={max}
          className="w-20 px-2 py-1.5 text-right text-sm text-white bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500/50"
        />
        <span className="text-xs text-white/40 w-10">{unit}</span>
      </div>
    </div>
  );
}

/**
 * Quick stats panel showing key design results.
 */
function QuickStatsPanel() {
  return (
    <div className="grid grid-cols-2 gap-4 h-full pt-2">
      <StatItem label="Ast req" value="628" unit="mm²" status="ok" />
      <StatItem label="Ast prov" value="804" unit="mm²" status="ok" />
      <StatItem label="% Steel" value="0.59" unit="%" status="ok" />
      <StatItem label="DCR" value="0.78" unit="" status="ok" />
    </div>
  );
}

interface StatItemProps {
  label: string;
  value: string;
  unit: string;
  status: "ok" | "warn" | "error";
}

function StatItem({ label, value, unit, status }: StatItemProps) {
  const statusColors = {
    ok: "text-green-400",
    warn: "text-yellow-400",
    error: "text-red-400",
  };

  return (
    <div className="flex flex-col">
      <span className="text-xs text-white/50">{label}</span>
      <span className={`text-lg font-semibold ${statusColors[status]}`}>
        {value}
        {unit && <span className="text-xs font-normal text-white/30 ml-1">{unit}</span>}
      </span>
    </div>
  );
}

export default ModernAppLayout;

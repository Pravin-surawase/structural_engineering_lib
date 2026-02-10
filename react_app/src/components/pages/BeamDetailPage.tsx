/**
 * BeamDetailPage - Full-screen 3D beam results with overlay panels.
 *
 * Shows the designed beam in detail with rebar, stirrups,
 * cross-section views, and draggable result panels.
 */
import { Suspense, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Eye, EyeOff } from "lucide-react";
import { useDesignStore } from "../../store/designStore";
import { Viewport3D } from "../viewport/Viewport3D";
import { CrossSectionView } from "../design/CrossSectionView";

type ViewTab = "3d" | "section";

export function BeamDetailPage() {
  const navigate = useNavigate();
  const { inputs, length, result } = useDesignStore();
  const [activeTab, setActiveTab] = useState<ViewTab>("3d");
  const [showPanels, setShowPanels] = useState(true);

  if (!result) {
    return (
      <div className="h-screen pt-14 flex items-center justify-center bg-zinc-950">
        <div className="text-center">
          <p className="text-white/40 mb-4">No design results yet</p>
          <button
            onClick={() => navigate("/design")}
            className="px-6 py-2.5 bg-blue-600 text-white rounded-xl text-sm font-medium"
          >
            Go to Design
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen pt-14 flex flex-col bg-zinc-950">
      {/* Toolbar */}
      <div className="h-12 flex items-center justify-between px-4 border-b border-white/5 shrink-0">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate("/design")} className="p-1.5 rounded-lg hover:bg-white/5 text-white/50 hover:text-white/80 transition-colors">
            <ArrowLeft className="w-4 h-4" />
          </button>
          <span className="text-sm font-medium text-white">
            Beam {inputs.width}x{inputs.depth} — {(length / 1000).toFixed(1)}m span
          </span>
          <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${result.success ? "bg-green-500/20 text-green-400" : "bg-red-500/20 text-red-400"}`}>
            {result.success ? "SAFE" : "FAIL"}
          </span>
        </div>

        <div className="flex items-center gap-2">
          {/* View tabs */}
          <div className="flex bg-white/5 rounded-lg p-0.5">
            <button
              onClick={() => setActiveTab("3d")}
              className={`px-3 py-1 text-xs rounded-md transition-colors ${activeTab === "3d" ? "bg-white/10 text-white" : "text-white/40 hover:text-white/70"}`}
            >
              3D View
            </button>
            <button
              onClick={() => setActiveTab("section")}
              className={`px-3 py-1 text-xs rounded-md transition-colors ${activeTab === "section" ? "bg-white/10 text-white" : "text-white/40 hover:text-white/70"}`}
            >
              Cross Section
            </button>
          </div>

          <button
            onClick={() => setShowPanels(!showPanels)}
            className="p-1.5 rounded-lg hover:bg-white/5 text-white/40 hover:text-white/70 transition-colors"
          >
            {showPanels ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 relative">
        {activeTab === "3d" ? (
          <Suspense fallback={<div className="flex items-center justify-center h-full"><p className="text-white/40 animate-pulse">Loading 3D viewport...</p></div>}>
            <Viewport3D mode="design" />
          </Suspense>
        ) : (
          <div className="h-full flex items-center justify-center p-8 bg-zinc-900/50">
            <CrossSectionView
              width={inputs.width}
              depth={inputs.depth}
              cover={40}
              astRequired={result.flexure?.ast_required ?? 0}
              stirrupDia={8}
            />
          </div>
        )}

        {/* Floating result panels */}
        {showPanels && (
          <div className="absolute bottom-4 left-4 right-4 flex gap-3">
            <FloatingCard title="Flexure" items={[
              { l: "Ast Required", v: `${result.flexure?.ast_required?.toFixed(0) || "-"} mm²` },
              { l: "xu / xu,max", v: `${result.flexure?.xu?.toFixed(1) || "-"} / ${result.flexure?.xu_max?.toFixed(1) || "-"} mm` },
              { l: "Mu,cap", v: `${result.flexure?.moment_capacity?.toFixed(0) || "-"} kN·m` },
            ]} />
            <FloatingCard title="Shear" items={[
              { l: "τv / τc", v: `${result.shear?.tau_v?.toFixed(2) || "-"} / ${result.shear?.tau_c?.toFixed(2) || "-"} MPa` },
              { l: "Stirrup Sv", v: result.shear?.stirrup_spacing ? `${result.shear.stirrup_spacing} mm` : "-" },
              { l: "Vu,cap", v: result.shear?.shear_capacity ? `${result.shear.shear_capacity.toFixed(0)} kN` : "-" },
            ]} />
            <FloatingCard title="Summary" items={[
              { l: "Ast total", v: `${result.ast_total?.toFixed(0) || "-"} mm²` },
              { l: "Utilization", v: `${(result.utilization_ratio * 100).toFixed(0)}%` },
              { l: "Status", v: result.success ? "SAFE" : "FAIL" },
            ]} accent={result.success ? "green" : "red"} />
          </div>
        )}
      </div>
    </div>
  );
}

function FloatingCard({ title, items, accent }: {
  title: string;
  items: { l: string; v: string }[];
  accent?: "green" | "red";
}) {
  const borderColor = accent === "green" ? "border-green-500/30" : accent === "red" ? "border-red-500/30" : "border-white/10";
  return (
    <div className={`flex-1 p-3 rounded-xl bg-zinc-900/80 backdrop-blur-xl border ${borderColor}`}>
      <h4 className="text-[10px] font-semibold text-white/50 uppercase tracking-wider mb-2">{title}</h4>
      <div className="space-y-1">
        {items.map((item) => (
          <div key={item.l} className="flex justify-between text-xs">
            <span className="text-white/40">{item.l}</span>
            <span className="text-white font-medium">{item.v}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
